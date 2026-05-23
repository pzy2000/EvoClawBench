import argparse
import time
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()

timeout = httpx.Timeout(300.0, connect=60.0)
client = httpx.AsyncClient(timeout=timeout)

# ── 认证 Token（两个路由共用） ──────────────────────────────────────────────────
TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
    "eyJjdXJyZW50VGltZSI6MTc3OTQzMjA2MTIxMCwiZXhwIjoxNzgwMDM2ODYxLCJ1c2VybmFtZSI6IjExOCJ9."
    "A8cGLDqYHOaSv94m6EqbxknzQCpyDsjHdXxuOLhj8ME"
)

# ── 上游端点 ────────────────────────────────────────────────────────────────────
GOOGLE_URL = (
    "https://arsenal-openai.10jqka.com.cn:8443"
    "/vtuber/ai_access/v1/publishers/google/models/generate_content"
)
QIANWEN_URL = (
    "https://arsenal-openai.10jqka.com.cn:8443"
    "/vtuber/ai_access/qianwen/v1/chat/completions"
)
KIMI_URL = (
    "http://arsenal-openai.myhexin.com"
    "/vtuber/ai_access/kimi_moonshot/v2/chat/completions"
)
GPT_URL = (
    "https://arsenal-openai.10jqka.com.cn:8443"
    "/vtuber/ai_access/chatgpt/v3/chat/completions"
)

# ── 各系列模型前缀 ───────────────────────────────────────────────────────────────
# 来源：qianwen_minimax_api.md + KIMI接口文档 + openai_api_manual.pdf
_QIANWEN_PREFIXES = (
    "qwen",        # qwen-plus, qwen-max, qwen3-*, qwen2.5-*, qwq-*
    "qwq",
    "deepseek",    # deepseek-v3, deepseek-r1, deepseek-r1-distill-*
    "minimax",     # MiniMax/MiniMax-M2.5, minimax-* 走同一内部端点
)
_KIMI_PREFIXES = (
    "moonshot",    # moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
    "kimi",        # kimi-* 内部别名
)
_GPT_PREFIXES = (
    "gpt-",        # gpt-3.5-turbo, gpt-4, gpt-4o, gpt-4.1, gpt-5, gpt-image-1, ...
    "o1",          # o1, o1-mini, o1-preview
    "o3",          # o3, o3-mini
    "o4",          # o4-mini
    "grok-4-fast-non-reasoning"
)

# litellm 内部参数：不应转发给任何上游 API
_LITELLM_INTERNAL_PARAMS = {
    "max_input_tokens",        # litellm 上下文截断控制，非 OpenAI 参数
    "per_instance_cost_limit", # litellm 费用追踪
    "total_cost_limit",
    "input_cost_per_token",
    "output_cost_per_token",
    "drop_params",
    "cost_tracking",
    "completion_kwargs",       # litellm 嵌套成本配置块
}


def _get_upstream_url(model: str) -> str | None:
    """
    根据 model 名称返回对应的上游端点 URL。
    未知 model 返回 None。
    """
    lower = model.lower()
    if any(lower.startswith(p) for p in _GPT_PREFIXES):
        return GPT_URL
    if any(lower.startswith(p) for p in _KIMI_PREFIXES):
        return KIMI_URL
    if any(lower.startswith(p) for p in _QIANWEN_PREFIXES):
        return QIANWEN_URL
    return None


def _build_chat_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "token": TOKEN,
        "Authorization": TOKEN,
    }


def _as_openai_error(payload: dict, status_code: int) -> JSONResponse:
    message = payload.get("status_msg") or payload.get("message") or "Upstream request failed"
    return JSONResponse(
        {
            "error": {
                "message": message,
                "type": "upstream_error",
                "code": payload.get("status_code", status_code),
            },
            "upstream": payload,
        },
        status_code=status_code,
    )


async def _post_upstream_json(upstream_url: str, body: dict, headers: dict) -> JSONResponse:
    response = await client.post(upstream_url, json=body, headers=headers)
    try:
        payload = response.json()
    except ValueError:
        return JSONResponse(
            {
                "error": {
                    "message": response.text[:1000] or "Upstream returned non-JSON response",
                    "type": "upstream_error",
                    "code": response.status_code,
                }
            },
            status_code=response.status_code if response.status_code >= 400 else 502,
        )

    upstream_status = payload.get("status_code")
    if response.status_code >= 400:
        return _as_openai_error(payload, response.status_code)
    if isinstance(upstream_status, int) and upstream_status >= 400:
        return _as_openai_error(payload, upstream_status)
    if isinstance(payload, dict) and "choices" not in payload and "status_msg" in payload:
        return _as_openai_error(payload, 502)
    return JSONResponse(payload, status_code=response.status_code)


# ── 中间件：记录请求耗时 ─────────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    print(f"[{current_time}] {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    print(f"[{current_time}] 完成 - 状态码: {response.status_code}, 耗时: {process_time:.3f}秒")

    return response


# ── 路由 0：模型列表 ─────────────────────────────────────────────────────────────
_KNOWN_MODELS = [
    # GPT / OpenAI
    "gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo",
    "gpt-5", "o1", "o1-mini", "o1-preview", "o3", "o3-mini", "o4-mini",
    # Qwen / DeepSeek / MiniMax
    "qwen-plus", "qwen-max", "qwen3-235b-a22b", "qwq-32b",
    "deepseek-v3", "deepseek-r1", "minimax-text-01",
    # Kimi
    "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k",
]

@app.get("/v1/models")
async def list_models():
    now = int(time.time())
    data = [
        {"id": m, "object": "model", "created": now, "owned_by": "proxy"}
        for m in _KNOWN_MODELS
    ]
    return JSONResponse({"object": "list", "data": data})


# ── 路由 1：Google GenAI（保留原有逻辑） ──────────────────────────────────────────
@app.post("/v1beta/models/{model}:generateContent")
async def proxy_genai(request: Request, model: str):
    genai_data = await request.json()
    genai_data["model"] = model
    headers = {
        "Content-Type": "application/json",
        "token": TOKEN,
    }

    response = await client.post(GOOGLE_URL, json=genai_data, headers=headers)
    return response.json()


# ── 路由 2：OpenAI 兼容接口 → Qianwen / MiniMax / KIMI / GPT ─────────────────────
@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    body = await request.json()
    model = body.get("model", "")

    # 过滤 litellm 内部参数，防止上游 API 报 unknown parameter 错误
    for param in _LITELLM_INTERNAL_PARAMS:
        body.pop(param, None)

    # parallel_tool_calls 仅在 tools 存在时才合法
    if "tools" not in body and "functions" not in body:
        body.pop("parallel_tool_calls", None)

    upstream_url = _get_upstream_url(model)
    if upstream_url is None:
        all_prefixes = _KIMI_PREFIXES + _QIANWEN_PREFIXES + _GPT_PREFIXES
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported model '{model}'. Supported prefixes: {all_prefixes}",
        )

    is_stream = bool(body.get("stream", False))
    headers = _build_chat_headers()

    if is_stream:
        # 流式：透传 SSE，逐块转发
        async def event_stream():
            async with client.stream("POST", upstream_url, json=body, headers=headers) as upstream:
                async for chunk in upstream.aiter_bytes():
                    yield chunk

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    else:
        return await _post_upstream_json(upstream_url, body, headers)


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=16666)
    parser.add_argument("--print-llm", default=None)  # accepted but unused
    args, _ = parser.parse_known_args()

    uvicorn.run(app, host=args.host, port=args.port)
