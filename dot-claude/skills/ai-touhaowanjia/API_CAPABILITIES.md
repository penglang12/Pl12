# Ai头号玩家 平台能力文档

## 平台信息
- 平台名称：Ai头号玩家
- 官网：https://findanai.co
- API 基础地址：https://api.lk888.ai/api
- API Key：sk-e58f7e4321ba405a405802bf13282fb7f283ac753a182f41
- 认证方式：Authorization: Bearer {API_KEY}

## 接口总览

### 一、模型查询（/v1/skills/*）

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取模型列表 | GET | /v1/skills/models | 按类型查询所有可用模型，?type=chat/image/video/audio |
| 模型详情 | GET | /v1/skills/models/{name} | 查询单个模型参数 |
| 模型价格 | GET | /v1/skills/models/{name}/pricing | 查询完整价格，?status=active |
| 通用调用指南 | GET | /v1/skills/guide | 所有模型调用方式说明 |

### 二、语言模型调用

| 格式 | 端点 | 适用模型 | SDK |
|------|------|---------|-----|
| OpenAI | POST /v1/chat/completions | gpt/o1/o3/chatgpt 前缀 | OpenAI SDK，改 base_url |
| OpenAI Responses | POST /v1/responses | gpt/o1/o3/chatgpt 前缀 | OpenAI SDK |
| Anthropic | POST /v1/messages | claude 前缀 | Anthropic SDK，改 base_url |
| Gemini | POST /v1beta/models/{model}:generateContent | gemini 前缀 | Google AI SDK |

### 三、媒体生成（异步轮询）

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 提交任务 | POST | /v1/media/generate | 提交生成任务，返回 task_id |
| 查询状态 | GET | /v1/skills/task-status?task_id={id} | 轮询任务结果 |
| 音色列表 | GET | /v1/skills/voices | 查询 TTS 音色 |
| 克隆音色 | POST | /v1/skills/voices/clone | 克隆自定义音色 |

### 四、账户管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 查询余额 | GET | /v1/skills/balance | 查询算力余额 |
| 消费明细 | GET | /v1/skills/usage | 查询消费记录 |
| 提交反馈 | POST | /v1/skills/feedback | BUG/建议提交 |
| 查询反馈 | GET | /v1/skills/feedback?id={id} | 查询反馈处理结果 |

## 可用模型类型

- **chat**: 语言模型（GPT/Claude/Gemini 系列）
- **image**: 图片生成（GPT Image、Gemini Image 等）
- **video**: 视频生成（Grok Video、Seedance、Wan2.6 等）
- **audio**: 音频/TTS/音乐（speech-2.8、music-2.5 等）

## 调用方式

### 语言模型（实时）
直接 POST 到对应端点，支持 stream=true 流式输出。

### 媒体模型（异步轮询）
1. POST /v1/media/generate 提交任务 → 获取 task_id
2. 每 5 秒 GET /v1/skills/task-status?task_id=xxx 轮询
3. is_final=true 时从 result_url 获取结果
4. 最长等待：大多数任务 5-30 分钟，视频类最长数小时

## 价格计算
- 按次计费：最终价格 = 基础价格 × 所有选项系数乘积 + 所有选项加成总和
- 按 token 计费：(输入 tokens × 输入单价 + 输出 tokens × 输出单价) ÷ 1,000,000
- 按秒计费：时长秒数 × 每秒价格

## 错误码
| 状态码 | error.type | 说明 |
|--------|-----------|------|
| 400 | invalid_request_error | 参数错误 |
| 401/403 | authentication_error | API Key 无效 |
| 402 | insufficient_balance | 余额不足 |
| 404 | not_found | 资源不存在 |
| 429 | rate_limit_exceeded | 频率限制 |
| 5xx | upstream_error | 上游故障 |
| 500 | server_error | 平台内部错误 |

## 渠道策略
用户在 API Key 设置中选择，调用时自动路由：
- 价格优先：选最便宜的渠道
- 速度优先：选响应最快的渠道
- 成功率优先：选成功率最高的渠道
- 自定义：用户预设的渠道顺序
