# Haiyi.art 闭源模型列表查询

获取平台所有可用的闭源（API）模型列表，按图片模型和视频模型分类，以表格形式展示每个模型名称及其支持的玩法。

对应后端接口：`POST /api/v1/task/v5/closed-source-model/list`

## 输出规范（重要）

1. 需要执行的脚本内容，必须先用 **Write 工具**写入 `/tmp/` 下的临时文件，再用 **Shell 工具**执行 `bash <文件路径>`。绝不要把脚本内容直接写在 Shell 调用中。
2. 执行 Shell 时 description 写当前 Step 名称。
3. 只向用户展示最终的模型列表表格，不展示中间过程和 JSON。

## 查询流程

### Step 1: 请求闭源模型列表

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_model_list.sh`：

```bash
#!/bin/bash
curl -s -o /tmp/haiyi_model_list.json 'https://www.haiyi.art/api/v1/task/v5/closed-source-model/list' \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'x-app-id: web_global_seaart' \
  -H 'x-platform: web' \
  -H "x-page-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H "x-request-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H 'x-timezone: Asia/Shanghai'

python3 << 'PYEOF'
import json, sys

r = json.load(open('/tmp/haiyi_model_list.json'))
if r.get('status', {}).get('code') != 10000:
    print('FAIL:' + r.get('status', {}).get('msg', '未知错误'))
    sys.exit(0)

data = r.get('data', {})
image_models = data.get('image_models', [])
video_models = data.get('video_models', [])

if not image_models and not video_models:
    print('EMPTY')
    sys.exit(0)

print('IMAGE_MODELS:' + json.dumps(image_models, ensure_ascii=False))
print('VIDEO_MODELS:' + json.dumps(video_models, ensure_ascii=False))
PYEOF
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_model_list.sh`

根据输出判断：
- `FAIL:xxx` → 告知用户查询失败并终止
- `EMPTY` → 告知用户「当前暂无可用的闭源模型」并终止
- 成功 → 提取 `IMAGE_MODELS` 和 `VIDEO_MODELS` 的 JSON 数据，继续下一步

### Step 2: 以表格形式展示结果

解析 Step 1 获取的 JSON 数据，按以下格式向用户展示两个 Markdown 表格。

#### 图片模型表格

如果 `image_models` 不为空，展示：

```
## 图片模型

| 序号 | 模型名称 | 支持的玩法 |
|------|---------|-----------|
| 1    | 模型A   | 玩法1、玩法2 |
| 2    | 模型B   | 玩法3      |
| ...  | ...     | ...        |
```

- **模型名称**：取自 `name` 字段
- **支持的玩法**：取自 `play_rule` 数组，用中文顿号 `、` 连接；若为空数组则显示 `-`

#### 视频模型表格

如果 `video_models` 不为空，展示：

```
## 视频模型

| 序号 | 模型名称 | 支持的玩法 |
|------|---------|-----------|
| 1    | 模型C   | 玩法4、玩法5 |
| ...  | ...     | ...        |
```

格式规则同上。

如果某一分类为空数组，则跳过该分类表格，不展示。

### Step 3: 清理临时文件

用 Shell 工具执行：
```
rm -f /tmp/haiyi_model_list.sh /tmp/haiyi_model_list.json
```

## 接口响应结构参考

```json
{
  "data": {
    "image_models": [
      {
        "name": "FLUX.1",
        "play_rule": ["文生图", "图生图"]
      }
    ],
    "video_models": [
      {
        "name": "Kling",
        "play_rule": ["文生视频", "图生视频"]
      }
    ]
  },
  "status": { "code": 10000, "msg": "success" }
}
```
