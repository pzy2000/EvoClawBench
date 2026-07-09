import os
import time

import requests
from openai import OpenAI

API_KEY = os.environ.get("OPENAI_API_KEY")
BASE = os.environ.get("OPENAI_BASE_URL", "").rstrip("/")
END_USER = os.environ.get("OPENAI_END_USER")

if not API_KEY or not BASE:
    raise RuntimeError(
        "Set OPENAI_API_KEY and OPENAI_BASE_URL in the environment before testing models."
    )

client = OpenAI(
    base_url=BASE + "/",
    api_key=API_KEY,
    default_headers={"X-End-User": END_USER} if END_USER else {},
)


def list_models():
    headers = {"Authorization": "Bearer " + API_KEY}
    if END_USER:
        headers["X-End-User"] = END_USER
    resp = requests.get(f"{BASE}/models", headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def test_chat(model: str):
    start = time.time()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=16,
        )
        elapsed = time.time() - start
        content = ""
        if resp.choices:
            content = (resp.choices[0].message.content or "").strip()
        return ("OK", elapsed, content[:40].replace("\n", " "))
    except Exception as exc:
        elapsed = time.time() - start
        name = type(exc).__name__
        msg = str(exc)
        status = name
        if "429" in msg or "RateLimit" in name or "Budget" in msg:
            status = "429"
        return (status, elapsed, msg[:120].replace("\n", " "))


def main():
    data = list_models()
    models = data if isinstance(data, list) else data.get("data", data)

    chat_models = [m for m in models if m.get("mode") == "chat" and not m.get("hidden")]
    print(f"共 {len(models)} 个模型，其中 chat 且未隐藏的: {len(chat_models)}\n")

    results = []
    for m in chat_models:
        mid = m["id"]
        status, elapsed, info = test_chat(mid)
        print(f"[{status:10}] {elapsed:6.2f}s  {mid}  | {info}")
        results.append((mid, status, elapsed, info, m.get("vendor")))

    print("\n\n## Markdown 结果\n")
    print("| 模型 ID | vendor | 状态 | 耗时 | 备注 |")
    print("|---|---|---|---|---|")
    for mid, status, elapsed, info, vendor in results:
        print(f"| `{mid}` | {vendor} | {status} | {elapsed:.2f}s | {info} |")


if __name__ == "__main__":
    main()
