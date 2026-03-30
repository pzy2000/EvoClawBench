CLAUDE接口文档

CLAUDE接口调用示例
1. CLAUDE的message接口非流式调用（亚马逊平台）
1.1. 请求信息
官方文档参考：https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html?
utm_source=chatgpt.com
(测试环境是mock数据，可在办公外网虚拟机访问http://arsenal-openai.myhexin.com/vtuber/ai_access/claude/model/{modelId}/invoke测试接口得到
真实数据，使用prod申请的app_id和app_secret，这个是prod环境的域名，其他环境只能在自己对应环境的容器里通过curl+环境变量手动测试调用
(euny7aiv集群有一个eip：http://10.217.216.28:8088))
API: http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/model/{modelId}/invoke
ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST
Method: POST
Header: token:${token} Authorization:${token}
Content-Type: application/json
X-Trace-Id: xxx
curl -X POST -d '{"anthropic_version": "bedrock-2023-05-31","max_tokens": 1024,"messages": [{"role": "user","
content": ""}]}' -H "Content-Type: application/json" -H "token: xxx" -H "X-Trace-Id: xxx"
http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/model/{modelId}/invoke
文本请求参数示例：
{
"anthropic_version": "bedrock-2023-05-31",
"max_tokens": 1024,
"messages": [
{
"role": "user",
"content": ""
}
]
}
1.2. 返回结果
非流式返回示例结果
注意
想调用CLAUDE的接口，需要去审批系统申请CLAUDE的资源，和申请的CHAT_GPT的token不共用
CLAUDE模型申请的token以us.anthropic.claude-3-5-sonnet-20241022-v2:0为计费基准
1-5通过亚马逊调用claude，6通过anthropic调用claude，7接口通过谷歌调用claude{
"id": "msg_bdrk_01MbhKVT6miohK8uFVZQYe6Q",
"type": "message",
"role": "assistant",
"model": "claude-3-5-sonnet-20241022",
"content": [
{
"type": "text",
"text": "!?"
}
],
"stop_reason": "end_turn",
"stop_sequence": null,
"usage": {
"input_tokens": 10,
"output_tokens": 30
}
}
1.3. 错误返回
http://cf.myhexin.com/pages/viewpage.action?pageId=1351141369#id-获取Token和账户相关接口文档-错误返回信息
1.4. 可选参数
参考官方文档：https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html?
utm_source=chatgpt.com
字
段
是
否
必
须
说
明
类
型
取值
mod
elId
必须
放在
url上
模型 string 目前只支持us.anthropic.claude-3-5-sonnet-20241022-v2:0、us.anthropic.claude-3-7-sonnet-20250219-v1:0、us.anthropic.claude-sonnet-420250514-v1:0、us.anthropic.claude-opus-4-20250514-v1:0、us.anthropic.claude-sonnet-4-5-20250929-v1:0、global.anthropic.claude-opus-4-520251101-v1:0
其余参数参考上面官方文档
2. CLAUDE的ChatCompletions接口流式调用（亚马逊平台）
2.1. 请求信息
官方文档参考：https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html?
utm_source=chatgpt.com
(测试环境是mock数据，可在办公外网虚拟机访问http://arsenal-openai.myhexin.com/vtuber/ai_access/claude/model/{modelId}/invoke-withresponse-stream测试接口得到真实数据，使用prod申请的app_id和app_secret，这个是prod环境的域名，其他环境只能在自己对应环境的容器里通过
curl+环境变量手动测试调用(euny7aiv集群有一个eip：http://10.217.216.28:8088))
API: http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/model/{modelId}/invoke-withresponse-streamARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST
Method: POST
Header: token:${token} Authorization:${token}
Content-Type: application/json
X-Trace-Id: xxx
curl -X POST -d '{"anthropic_version": "bedrock-2023-05-31","max_tokens": 1024,"messages": [{"role": "user","
content": ""}]}' -H "Content-Type: application/json" -H "token: xxx" -H "X-Trace-Id: xxx"
http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/model/{modelId}/invoke-withresponse-stream
文本请求参数示例：{
"anthropic_version": "bedrock-2023-05-31",
"max_tokens": 1024,
"messages": [
{
"role": "user",
"content": ""
}
]
}
2.2. 返回结果
流式返回示例结果
data:{"type":"message_start","message":{"model":"claude-opus-4-5-20251101","id":"
msg_bdrk_01BEjCCtZ8AR6ZT2NbcVcUQ9","type":"message","role":"assistant","content":[],"stop_reason":null,"
stop_sequence":null,"usage":{"input_tokens":10,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"
cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":8}}}
retry:300
data:{"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}
retry:300
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":""}}
retry:300
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":""}}
retry:300
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":""}}
retry:300
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":""}}
retry:300
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":""}}
retry:300
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":""}}
retry:300
data:{"type":"content_block_stop","index":0}
retry:300
data:{"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":
29}}
retry:300
data:{"type":"message_stop","amazon-bedrock-invocationMetrics":{"inputTokenCount":10,"outputTokenCount":29,"
invocationLatency":2018,"firstByteLatency":1490}}
retry:300
2.3. 错误返回
http://cf.myhexin.com/pages/viewpage.action?pageId=1351141369#id-获取Token和账户相关接口文档-错误返回信息
2.4. 可选参数
参考官方文档：https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html?
utm_source=chatgpt.com字
段
是
否
必
须
说
明
类
型
取值
mod
elId
必须
放在
url上
模型 string 目前只支持us.anthropic.claude-3-5-sonnet-20241022-v2:0、us.anthropic.claude-3-7-sonnet-20250219-v1:0、us.anthropic.claude-sonnet-420250514-v1:0、us.anthropic.claude-opus-4-20250514-v1:0、us.anthropic.claude-sonnet-4-5-20250929-v1:0、global.anthropic.claude-opus-4-520251101-v1:0
其余参数参考上面官方文档
3. CLAUDE的ChatCompletions接口调用（走亚马逊平台提供的代理，下面两个接口的综合接
口，bedrock方式，旧接口，对应源平台接口已不再支持新模型）
3.1. 请求信息
(测试环境是mock数据，可在办公外网虚拟机访问http://arsenal-openai.myhexin.com/vtuber/ai_access/claude/v2/chat/completions测试接口得到真
实数据，使用prod申请的app_id和app_secret，这个是prod环境的域名，其他环境只能在自己对应环境的容器里通过curl+环境变量手动测试调用
(euny7aiv集群有一个eip：http://10.217.216.28:8088))
API: http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/v2/chat/completions
ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST
Method: POST
Header: token:${token} Authorization:${token}
Content-Type: application/json
X-Trace-Id: xxx
curl -X POST -d '{"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0","messages": [{"role": "user","
content": ""}]}' -H "Content-Type: application/json" -H "token: xxx" -H "X-Trace-Id: xxx"
http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/v2/chat/completions
文本请求参数示例：
{
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"messages": [
{
"role": "user",
"content": ""
}
]
}
图片请求参数示例{
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"messages": [
{
"role": "user",
"content": [
{
"type": "text",
"text": "Describe this picture:"
},
{
"type": "image_url",
"image_url": {
"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47
/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
}
}
]
}
]
}
流式请求参数示例
{
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"messages": [
{
"role": "user",
"content": ""
}
],
"stream": true
}
3.2. 返回结果
非流式返回示例结果{
"id": "chatcmpl-58c55e36",
"created": 1742297639,
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"system_fingerprint": "fp",
"choices": [
{
"index": 0,
"finish_reason": "stop",
"logprobs": null,
"message": {
"role": "assistant",
"content": "This image shows four colorful dice arranged together. There's a red die, a blue
die, a green die, and a yellow die. They appear to be translucent or semi-transparent with a glossy, almost
glass-like quality. The dice have white dots (pips) on them showing different numbers, and they're positioned
in a casual arrangement as if they've been tossed or grouped together. The image has a transparent background
and appears to be a 3D rendered illustration rather than a photograph of real dice."
}
}
],
"object": "chat.completion",
"usage": {
"prompt_tokens": 95,
"completion_tokens": 113,
"total_tokens": 208
}
}
流式返回示例结果
data:{"id":"chatcmpl-a8f362c5","created":1742298072,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"role":"
assistant","content":""}}],"object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-a8f362c5","created":1742298072,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":""}}],"
object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-a8f362c5","created":1742298072,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":"Bruce
Lee"}}],"object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-a8f362c5","created":1742298084,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":""}}],"
object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-a8f362c5","created":1742298084,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":"stop","logprobs":null,"delta":{}}],"object":"
chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-a8f362c5","created":1742298084,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[],"object":"chat.completion.chunk","usage":{"prompt_tokens":15,"
completion_tokens":459,"total_tokens":474}}
retry:300
data:[DONE]
retry:300
3.3. 错误返回http://cf.myhexin.com/pages/viewpage.action?pageId=1351141369#id-获取Token和账户相关接口文档-错误返回信息
3.4. 可选参数
字
段
是
否
必
须
说明 类
型
取值
messa
ges
requi
red
包含迄今为止对话的消息列表 List
[Dict]
这是一个结构体的列表，每个元素类似如下：{"role": "user", "content": ""}
model requi
red
Model ID, 可以通过 List Models 获取 string 目前只支持us.anthropic.claude-3-5-sonnet-20241022-v2:0、us.anthropic.claude-37-sonnet-20250219-v1:0、us.anthropic.claude-sonnet-4-20250514-v1:0、us.
anthropic.claude-opus-4-20250514-v1:0
stream 否 响应内容是否流式返回 Boole
an false：模型生成完所有内容后一次性返回结果
true：按 SSE 协议逐块返回模型生成内容，并以一条 消息结束data: [DONE]
max_t
okens
optio
nal
聊天完成时生成的最大 token 数。如果到生成了最大 token 数个结果仍然
没有结束，finish reason 会是 "length", 否则会是 "stop"
int
tempe
rature
optio
nal
使用什么采样温度，介于 0 和 1 之间。较高的值（如 0.7）将使输出更加
随机，而较低的值（如 0.2）将使其更加集中和确定性
float
top_p optio
nal
另一种采样方法，即模型考虑概率质量为 top_p 的标记的结果。因此，0.1
意味着只考虑概率质量最高的 10% 的标记。一般情况下，我们建议改变这
一点或温度，但不建议 同时改变
float
n optio
nal
为每条输入消息生成多少个结果 int
prese
nce_p
enalty
optio
nal
存在惩罚，介于-2.0到2.0之间的数字。正值会根据新生成的词汇是否出现
在文本中来进行惩罚，增加模型讨论新话题的可能性
float
freque
ncy_p
enalty
optio
nal
频率惩罚，介于-2.0到2.0之间的数字。正值会根据新生成的词汇在文本中
现有的频率来进行惩罚，减少模型一字不差重复同样话语的可能性
float
stop optio
nal
停止词，当全匹配这个（组）词后会停止输出，这个（组）词本身不会输
出。
String
, List
[Strin
g]
tools 否 tool calls调用 List
[objec
t]
见下面示例
3.5. tool calls调用示例{
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"messages": [
{
"role": "user",
"content": " Context Caching"
}
],
"tools": [
{
"type": "function",
"function": {
"name": "search",
"description": " query URL",
"parameters": {
"type": "object",
"required": ["query"],
"properties": {
"query": {
"type": "string",
"description": ""
}
}
}
}
}
]
}
结果：
{
"id": "chatcmpl-c94cb9ec",
"created": 1742298326,
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"system_fingerprint": "fp",
"choices": [
{
"index": 0,
"finish_reason": "tool_calls",
"logprobs": null,
"message": {
"role": "assistant",
"content": null,
"tool_calls": [
{
"id": "tooluse_tmhU__aTSgS7dUJr_D_T4w",
"type": "function",
"function": {
"name": "search",
"arguments": "{\"query\": \"Context Caching meaning definition computer science\"}"
}
}
]
}
}
],
"object": "chat.completion",
"usage": {
"prompt_tokens": 990,
"completion_tokens": 80,
"total_tokens": 1070
}
}
4. CLAUDE的ChatCompletions非流式接口调用（亚马逊平台）4.1. 请求信息
(测试环境是mock数据，可在办公外网虚拟机访问http://arsenal-openai.myhexin.com/vtuber/ai_access/claude/v1/chat/completions测试接口得到真
实数据，使用prod申请的app_id和app_secret，这个是prod环境的域名，其他环境只能在自己对应环境的容器里通过curl+环境变量手动测试调用
(euny7aiv集群有一个eip：http://10.217.216.28:8088))
API: http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/v1/chat/completions
ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST
Method: POST
Header: token:${token} Authorization:${token}
Content-Type: application/json
X-Trace-Id: xxx
curl -X POST -d '{"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0","messages": [{"role": "user","
content": ""}]}' -H "Content-Type: application/json" -H "token: xxx" -H "X-Trace-Id: xxx"
http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/v1/chat/completions
请求参数示例：
{
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"messages": [
{
"role": "user",
"content": ""
}
]
}
4.2. 返回结果
{
"data": {
"id": "chatcmpl-974487d7",
"object": "chat.completion",
"created": 1733311301,
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"usage": {
"prompt_tokens": 15,
"completion_tokens": 428,
"total_tokens": 443
},
"choices": [
{
"index": 0,
"message": {
"role": "assistant",
"content": "Bruce Lee19401127-1973720\n\n\n1. \n2. 5\n3. 18\n4. \"\"\n\n\n1. \n- \n- \n\n- ()\n- \n\n\n1. \n2. \n3. \n4. \n\n33\"\""
},
"finish_reason": "stop"
}
],
"system_fingerprint": "fp"
},
"success": true,
"status_code": 0,
"status_msg": "ok"
}
4.3. 可选参数字段 是
否
必
须
说明 类
型
取值
messag
es
requi
red
包含迄今为止对话的消息列表 List
[Dict]
这是一个结构体的列表，每个元素类似如下：{"role": "user",
role 只支持 , , 其一，"content": ""} system user assistant
content 不得为空
model requi
red
Model ID, 可以通过 List Models 获取 string 目前是只支持us.anthropic.claude-3-5-sonnet-20241022-v2:0、us.
anthropic.claude-3-7-sonnet-20250219-v1:0
max_to
kens
optio
nal
聊天完成时生成的最大 token 数。如果到生成了最大 token 数个结果仍然没有结束，
finish reason 会是 "length", 否则会是 "stop"
int
temper
ature
optio
nal
使用什么采样温度，介于 0 和 1 之间。较高的值（如 0.7）将使输出更加随机，而较低
的值（如 0.2）将使其更加集中和确定性
float
top_p optio
nal
另一种采样方法，即模型考虑概率质量为 top_p 的标记的结果。因此，0.1 意味着只考
虑概率质量最高的 10% 的标记。一般情况下，我们建议改变这一点或温度，但不建议
同时改变
float
n optio
nal
为每条输入消息生成多少个结果 int
presenc
e_penal
ty
optio
nal
存在惩罚，介于-2.0到2.0之间的数字。正值会根据新生成的词汇是否出现在文本中来进
行惩罚，增加模型讨论新话题的可能性
float
frequen
cy_pen
alty
optio
nal
频率惩罚，介于-2.0到2.0之间的数字。正值会根据新生成的词汇在文本中现有的频率来
进行惩罚，减少模型一字不差重复同样话语的可能性
float
stop optio
nal
停止词，当全匹配这个（组）词后会停止输出，这个（组）词本身不会输出。 String,
List
[String]
tools 否 tool calls调用 List
[object]
见下面示例
4.4. tool calls调用示例
{
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"messages": [
{
"role": "user",
"content": " Context Caching"
}
],
"tools": [
{
"type": "function",
"function": {
"name": "search",
"description": " query URL",
"parameters": {
"type": "object",
"required": ["query"],
"properties": {
"query": {
"type": "string",
"description": ""
}
}
}
}
}
]
}
结果：{
"data": {
"id": "chatcmpl-25acd6ba",
"object": "chat.completion",
"created": 1733311132,
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"usage": {
"prompt_tokens": 990,
"completion_tokens": 80,
"total_tokens": 1070
},
"choices": [
{
"index": 0,
"message": {
"role": "assistant",
"tool_calls": [
{
"id": "tooluse_1WF5kw7eTRWSGNIi6G8J4g",
"type": "function",
"function": {
"name": "search",
"arguments": "{\"query\": \"Context Caching meaning definition computer
science\"}"
}
}
]
},
"finish_reason": "tool_calls"
}
],
"system_fingerprint": "fp"
},
"success": true,
"status_code": 0,
"status_msg": "ok"
}
5. CLAUDE的ChatCompletions流式接口调用（亚马逊平台）
5.1. 请求信息
(测试环境是mock数据，可在办公外网虚拟机访问http://arsenal-openai.myhexin.com/vtuber/ai_access/claude_stream/v1/chat/completions测试接口
得到真实数据，使用prod申请的app_id和app_secret，这个是prod环境的域名，其他环境只能在自己对应环境的容器里通过curl+环境变量手动测试调用
(euny7aiv集群有一个eip：http://10.217.216.28:8088))
API: http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude_stream/v1/chat/completions
ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST
Method: POST
Header: token:${token} Authorization:${token}
Content-Type: application/json
X-Trace-Id: xxx
curl -X POST -d '{"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0","messages": [{"role": "user","
content": ""}]}' -H "Content-Type: application/json" -H "token: xxx" -H "X-Trace-Id: xxx"
http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude_stream/v1/chat/completions
请求参数示例（不带上下文）：{
"model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
"messages": [
{
"role": "user",
"content": ""
}
]
}
5.2. 返回结果
data:{"id":"chatcmpl-f030be5e","created":1733822303,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"role":"
assistant","content":""}}],"object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-f030be5e","created":1733822303,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":""}}],"
object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-f030be5e","created":1733822303,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":""}}],"
object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-f030be5e","created":1733822303,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":"
Jackie"}}],"object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-f030be5e","created":1733822303,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":"
Chan"}}],"object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-f030be5e","created":1733822303,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":"1"}}],"
object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-f030be5e","created":1733822316,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":null,"logprobs":null,"delta":{"content":""}}],"
object":"chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-f030be5e","created":1733822316,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[{"index":0,"finish_reason":"stop","logprobs":null,"delta":{}}],"object":"
chat.completion.chunk","usage":null}
retry:300
data:{"id":"chatcmpl-f030be5e","created":1733822316,"model":"us.anthropic.claude-3-5-sonnet-20241022-v2:0","
system_fingerprint":"fp","choices":[],"object":"chat.completion.chunk","usage":{"prompt_tokens":14,"
completion_tokens":417,"total_tokens":431}}
retry:300
data:[DONE]
retry:300
6. CLAUDE的ChatCompletions接口调用（anthropic平台）【想使用可咨询曾志武，anthropic
平台账号可能没钱】6.1. 请求信息
官方文档参考：https://docs.anthropic.com/en/api/openai-sdk
(测试环境是mock数据，可在办公外网虚拟机访问http://arsenal-openai.myhexin.com/vtuber/ai_access/claude/v4/chat/completions测试接口得到真
实数据，使用prod申请的app_id和app_secret，这个是prod环境的域名，其他环境只能在自己对应环境的容器里通过curl+环境变量手动测试调用
(euny7aiv集群有一个eip：http://10.217.216.28:8088))
API: http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/v4/chat/completions
ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST
Method: POST
Header: token:${token} Authorization:${token}
Content-Type: application/json
X-Trace-Id: xxx
curl -X POST -d '{"model": "claude-3-7-sonnet-20250219","messages": [{"role": "user","content": ""}]}' -H
"Content-Type: application/json" -H "token: xxx" -H "X-Trace-Id: xxx"
http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/v4/chat/completions
文本请求参数示例：
{
"model": "claude-3-7-sonnet-20250219",
"messages": [
{
"role": "user",
"content": ""
}
]
}
图片请求参数示例
{
"model": "claude-3-7-sonnet-20250219",
"messages": [
{
"role": "user",
"content": [
{
"type": "text",
"text": "Describe this picture:"
},
{
"type": "image_url",
"image_url": {
"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47
/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
}
}
]
}
]
}
流式请求参数示例{
"model": "claude-3-7-sonnet-20250219",
"messages": [
{
"role": "user",
"content": ""
}
],
"stream": true
}
6.2. 返回结果
非流式返回示例结果
{
"id": "msg_01XmYgS9oQ9JRjoDFDpzCb9J",
"choices": [
{
"finish_reason": "stop",
"index": 0,
"message": {
"role": "assistant",
"content": "# \n\n\"\"\"\"\n\n## \n\n1. ****\n2. ****\n3. ****\n4. ****\n5. ****\n6. ****\n\n##
\n\n100\n- 10010,000\n- 808,000100\n- 2,000\n\n## \n\n1. ****\n2. ****\n3. ****\n4. ****\n\n## \n\n- \n- \n\n- \n\n"
}
}
],
"created": 1747809627,
"model": "claude-3-7-sonnet-20250219",
"object": "chat.completion",
"usage": {
"completion_tokens": 586,
"prompt_tokens": 14,
"total_tokens": 600
}
}
流式返回示例结果
data: {"id":"msg_01TLwXCZ8Myb3uS681FpYUr7","choices":[{"index":0,"delta":{"role":"assistant"}}],"created":
1747809739,"model":"claude-3-7-sonnet-20250219","object":"chat.completion.chunk"}
retry:300
data: {"type": "ping"}
retry:300
data: {"id":"msg_01TLwXCZ8Myb3uS681FpYUr7","choices":[{"index":0,"delta":{"content":"# "}}],"created":
1747809739,"model":"claude-3-7-sonnet-20250219","object":"chat.completion.chunk"}
retry:300
......
data: {"id":"msg_01TLwXCZ8Myb3uS681FpYUr7","choices":[{"index":0,"delta":{"content":""}}],"created":1747809739,"
model":"claude-3-7-sonnet-20250219","object":"chat.completion.chunk"}
retry:300
data: {"id":"msg_01TLwXCZ8Myb3uS681FpYUr7","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"created":
1747809739,"model":"claude-3-7-sonnet-20250219","object":"chat.completion.chunk","usage":{"completion_tokens":
650,"prompt_tokens":14,"total_tokens":664}}
retry:300
data: [DONE]
retry:3006.3. 错误返回
http://cf.myhexin.com/pages/viewpage.action?pageId=1351141369#id-获取Token和账户相关接口文档-错误返回信息
6.4. 可选参数
官方文档参考：https://docs.anthropic.com/en/api/openai-sdk
字段 是否必须 说明 类型 取值
messages 是 包含迄今为止对话的消息列表 List[Dict] 这是一个结构体的列表，每个元素类似如下： ，content 不得为空{"role": "user", "content": ""}
model 是 Model ID, 可以通过 List Models 获取 string 目前只支持claude-3-5-sonnet-20241022、claude-3-7-sonnet-20250219
新增：claude-sonnet-4-20250514、claude-opus-4-20250514
max_tokens 是 聊天完成时生成的最大 token 数。 int 不同的模型对此参数有不同的最大值。有关详细信息，请参阅官方文档模型。
stream 否 响应内容是否流式返回 Boolean
false：模型生成完所有内容后一次性返回结果
true：按 SSE 协议逐块返回模型生成内容
更多参数见上面官方文档
7. CLAUDE的ChatCompletions接口调用（谷歌云平台）
7.1. 请求信息
官方文档参考：https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude?hl=zh-cn#use_a_curl_command
(测试环境是mock数据，可在办公外网虚拟机访问http://arsenal-openai.myhexin.com/vtuber/ai_access/claude/v3/chat/completions测试接口得到真
实数据，使用prod申请的app_id和app_secret，这个是prod环境的域名，其他环境只能在自己对应环境的容器里通过curl+环境变量手动测试调用
(euny7aiv集群有一个eip：http://10.217.216.28:8088))
API: http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/v3/chat/completions
ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST
Method: POST
Header: token:${token} Authorization:${token}
Content-Type: application/json
X-Trace-Id: xxx
curl -X POST -d '{"model": "claude-3-7-sonnet@20250219","anthropic_version": "vertex-2023-10-16","max_tokens":
2048,"messages": [{"role":"user","content": ""}]}' -H "Content-Type: application/json" -H "token: xxx" -H "XTrace-Id: xxx" http://${ARSENAL_SVC_ARSENAL_OPENAI_SERVER_HTTP_HOST}/vtuber/ai_access/claude/v3/chat/completions
文本请求参数示例：
{
"model": "claude-3-7-sonnet@20250219",
"anthropic_version": "vertex-2023-10-16",
"max_tokens": 2048,
"messages": [
{
"role": "user",
"content": ""
}
]
}
图片请求参数示例{
"model": "claude-3-7-sonnet@20250219",
"anthropic_version": "vertex-2023-10-16",
"max_tokens": 2048,
"messages": [
{
"role": "user",
"content": [
{
"type": "image",
"source": {
"type": "base64",
"media_type": "image/png",
"data": "iVBORw0KG......" //Base64
}
},
{
"type": "text",
"text": "What is in the above image?"
}
]
}
]
}
流式请求参数示例
{
"model": "claude-3-7-sonnet@20250219",
"anthropic_version": "vertex-2023-10-16",
"max_tokens": 2048,
"messages": [
{
"role": "user",
"content": ""
}
],
"stream": true
}
7.2. 返回结果
非流式返回示例结果
{
"id": "msg_vrtx_015aVQad8WJL1K4c1Et7r3wn",
"type": "message",
"role": "assistant",
"model": "claude-3-7-sonnet-20250219",
"content": [
{
"type": "text",
"text": "# \n\nShort Selling\n\n## \n1. ****\n2. ****\n3. ****\n4. ****\n5. ****\n6. **** = - -
\n\n## \n\n- 100$100$10,000\n- $10,000\n- $70$7,000100\n- \n- $3,000\n\n## \n- ****\n- ****\n- ****\n\n"
}
],
"stop_reason": "end_turn",
"stop_sequence": null,
"usage": {
"input_tokens": 16,
"cache_creation_input_tokens": 0,
"cache_read_input_tokens": 0,
"output_tokens": 492
}
}流式返回示例结果
event:message_start
data:{"type":"message_start","message":{"id":"msg_vrtx_017KKNPUtd6PJZpJQ9mtj9rU","type":"message","role":"
assistant","model":"claude-3-7-sonnet-20250219","content":[],"stop_reason":null,"stop_sequence":null,"usage":
{"input_tokens":16,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":1}} }
retry:300
event:ping
data:{"type": "ping"}
retry:300
event:content_block_start
data:{"type":"content_block_start","index":0,"content_block":{"type":"text","text":""} }
retry:300
event:content_block_delta
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"#"} }
retry:300
event:content_block_delta
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" \n\n"} }
event:content_block_delta
data:{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":""} }
retry:300
event:content_block_stop
data:{"type":"content_block_stop","index":0 }
retry:300
event:message_delta
data:{"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":
435} }
retry:300
event:message_stop
data:{"type":"message_stop" }
retry:300
7.3. 使用thinking示例
{
"model": "claude-3-7-sonnet@20250219",
"messages": [
{
"role": "user",
"content": ""
}
],
"max_tokens": 2048,
"anthropic_version": "vertex-2023-10-16",
"thinking": {
"type": "enabled",
"budget_tokens": 1024
}
}
非流式结果：{
"id": "msg_vrtx_01KaHarkGVTst1GKv4JA1Bqt",
"type": "message",
"role": "assistant",
"model": "claude-3-7-sonnet-20250219",
"content": [
{
"type": "thinking",
"thinking": "\"\"short sellingshorting\n\n\n1. \n2. \n\n\n1. \n2. \n3. \n4. \n5. \n\n\n1. \n2. \n3.
\n4. \"\"\n\n\n1. \n2. \n3. \n\n\n1. \n2. \n3. \n\n",
"signature":
"ErcBCkgIAhACGAIiQAwhwSpSJPrkKKQ0UdFNz5iUzBfS1r+iowHYYC99zSV2e33P1NlBl+EeaZbi8d0cColivLtwoJsoPN3WtCrIOAgSDFHr7bE
YAPNK0akQihoMjtbnobdABeinVUglIjDcRgnxopxFh8kVxajtSgpCX5G79ZbKtBGPgTTtC6Ac+CJYgAAUTCf
/1M+SIhZf6p0qHecIrh7kIe4UqGMkQWtdVXiUMmKHXHvHUzN8t+7b"
},
{
"type": "text",
"text": "# Short Selling\n\n\"\"\"\"\n\n## \n\n1. ****\n2. ****\n3. ****\n4. ****\n5. ****\n\n##
\n\n100\n- 10010,000\n- 808,000100\n- 2,000\n\n## \n\n- ****\n- ****\n- ****\n- ****\n\n"
}
],
"stop_reason": "end_turn",
"stop_sequence": null,
"usage": {
"input_tokens": 42,
"cache_creation_input_tokens": 0,
"cache_read_input_tokens": 0,
"output_tokens": 1024
}
}
流式结果：event:message_start
data:{"type":"message_start","message":{"id":"msg_vrtx_014ydX6sr1TP5Joggd6RwpyC","type":"message","role":"
assistant","model":"claude-3-7-sonnet-20250219","content":[],"stop_reason":null,"stop_sequence":null,"usage":
{"input_tokens":42,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":2}} }
retry:300
event:ping
data:{"type": "ping"}
retry:300
event:content_block_start
data:{"type":"content_block_start","index":0,"content_block":{"type":"thinking","thinking":"","
signature":""} }
retry:300
event:content_block_delta
data:{"type":"content_block_delta","index":0,"delta":{"type":"thinking_delta","thinking":""} }
retry:300
event:content_block_delta
data:{"type":"content_block_delta","index":1,"delta":{"type":"text_delta","text":""} }
retry:300
event:content_block_stop
data:{"type":"content_block_stop","index":1 }
retry:300
event:message_delta
data:{"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":
969} }
retry:300
event:message_stop
data:{"type":"message_stop" }
retry:300
7.4. 错误返回
http://cf.myhexin.com/pages/viewpage.action?pageId=1351141369#id-获取Token和账户相关接口文档-错误返回信息
7.5. 可选参数
官方文档参考：https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude?hl=zh-cn#use_a_curl_command
字段 是否必
须
说明 类型 取值
messages 是 包含迄今为止对话的消息列表 List[Dict] 这是一个结构体的列表，每个元素类似如下： ，content 不得{"role": "user", "content": ""}
为空
model 是 Model ID, 可以通过 List Models 获
取
string 目前只支持claude-3-7-sonnet@20250219、claude-3-5-sonnet-v2@20241022
max_tokens 是 聊天完成时生成的最大 token 数。 int 范围[ 1, 64000 ]
anthropic_version 是 版本 string 可用vertex-2023-10-16
stream 否 响应内容是否流式返回 Boolean
false：模型生成完所有内容后一次性返回结果
true：按 SSE 协议逐块返回模型生成内容
thinking 否 扩展思考 object 见上面thinking示例
tools 否 tool calls调用 List
[object]
见下面示例
7.6. tool calls调用示例{
"model": "claude-3-7-sonnet-20250219",
"anthropic_version": "vertex-2023-10-16",
"max_tokens": 2048,
"tools": [
{
"name": "text_search_places_api",
"description": "Returns information about a set of places based on a string",
"input_schema": {
"type": "object",
"properties": {
"textQuery": {
"type": "string",
"description": "The text string on which to search"
},
"priceLevels": {
"type": "array",
"description": "Price levels to query places, value can be one of
[PRICE_LEVEL_INEXPENSIVE, PRICE_LEVEL_MODERATE, PRICE_LEVEL_EXPENSIVE, PRICE_LEVEL_VERY_EXPENSIVE]"
},
"openNow": {
"type": "boolean",
"description": "Describes whether a place is open for business at the time of the
query."
}
},
"required": [
"textQuery"
]
}
}
],
"messages": [
{
"role": "user",
"content": "What are some affordable and good Italian restaurants that are open now in San
Francisco??"
}
]
}
结果：{
"id": "msg_vrtx_01XYNwEqbUrZRqSkaRSW4oTD",
"type": "message",
"role": "assistant",
"model": "claude-3-7-sonnet-20250219",
"content": [
{
"type": "text",
"text": "I'll help you find affordable Italian restaurants that are open now in San Francisco. Let
me search for that information for you."
},
{
"type": "tool_use",
"id": "toolu_vrtx_01TcbdkCjZE4Vsi8zThN7qzh",
"name": "text_search_places_api",
"input": {
"textQuery": "affordable Italian restaurants in San Francisco",
"openNow": true,
"priceLevels": [
"PRICE_LEVEL_INEXPENSIVE",
"PRICE_LEVEL_MODERATE"
]
}
}
],
"stop_reason": "tool_use",
"stop_sequence": null,
"usage": {
"input_tokens": 517,
"cache_creation_input_tokens": 0,
"cache_read_input_tokens": 0,
"output_tokens": 150
}
}