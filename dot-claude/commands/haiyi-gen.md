# Haiyi.art AI 创作（图片/视频生成）

执行以下创作流程，严格按顺序操作。对应 LangGraph 创作链：
`get_model_id_node → get_task_input_parameters_node → creative_task_v2_node → query_task_progress_node`

## 输出规范（重要）

1. 需要执行的脚本内容，必须先用 **Write 工具**写入 `/tmp/` 下的临时文件，再用 **Shell 工具**执行 `bash <文件路径>`。绝不要把脚本内容直接写在 Shell 调用中。
2. 执行 Shell 时 description 写当前 Step 名称。
3. 只向用户展示最终结果（成功/失败/图片），不展示中间过程和 JSON。

## 公共 Headers 模板

所有 API 脚本中复用以下 headers 函数（TOKEN 变量由各脚本在头部设定）：

```bash
haiyi_headers() {
  echo -H 'Content-Type: application/json' \
       -H "token: $TOKEN" \
       -H 'x-app-id: web_global_seaart' \
       -H 'x-platform: web' \
       -H "x-page-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
       -H "x-request-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
       -H 'x-timezone: Asia/Shanghai'
}
```

## 创作流程

### Step 1: 读取 Token

使用 Read 工具读取本命令同级目录下的 `../haiyi-login/token.md`（即 `haiyi-login` 命令保存的 token 文件）。

- 读取成功 → 将内容赋值给变量 `TOKEN`，继续下一步
- 文件不存在或为空 → 告知用户「请先执行 `/haiyi-login:login` 登录」，然后终止

### Step 2: 询问创作需求

直接向用户发送以下消息，然后**停止并等待用户回复**：

> 🎨 请描述你想生成的图片或视频（例如：「一只橘猫在阳光下打盹，动漫风格」）

用户回复后，记住完整的用户输入 `USER_INPUT`。

根据用户描述判断：
- `IS_VIDEO`：用户是否明确要求生成视频（提到"视频"、"动画"、"video"等）
- `MODEL_NAME`：用户是否指定了模型名称（提到具体模型如 "FLUX"、"SD" 等），未指定则为空

### Step 3: 向量搜索模型（get_model_id_node — 主路径）

通过用户输入的文本向量搜索匹配模型。

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_vector_model.sh`（替换 `<TOKEN>` 和 `<USER_INPUT>`）：

```bash
#!/bin/bash
TOKEN="<TOKEN>"

curl -s -o /tmp/haiyi_vector_model.json 'https://www.haiyi.art/api/v1/task/v5/vector/model' \
  -X POST \
  -H 'Content-Type: application/json' \
  -H "token: $TOKEN" \
  -H 'x-app-id: web_global_seaart' \
  -H 'x-platform: web' \
  -H "x-page-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H "x-request-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H 'x-timezone: Asia/Shanghai' \
  -d '<PAYLOAD>'

python3 << 'PYEOF'
import json, sys
r = json.load(open('/tmp/haiyi_vector_model.json'))
if r.get('status',{}).get('code') != 10000:
    print('EMPTY')
    sys.exit(0)
items = r.get('data', [])
if not items or not items[0].get('model_id'):
    print('EMPTY')
    sys.exit(0)
m = items[0]
print(f"FOUND:{m['model_id']},{m['model_ver_id']}")
PYEOF
```

其中 `<PAYLOAD>` 为 `{"text":"<USER_INPUT>"}` — 将用户的完整输入作为搜索文本（注意 JSON 转义）。

**然后用 Shell 工具**执行：`bash /tmp/haiyi_vector_model.sh`

根据输出判断：
- `FOUND:<model_id>,<model_ver_id>` → 提取 `MODEL_ID` 和 `MODEL_VER_ID`，**跳过 Step 4，直接进入 Step 5**
- `EMPTY` → 向量搜索未匹配到模型，继续执行 Step 4 获取默认模型

### Step 4: 获取默认模型（get_model_id_node — 兜底）

**仅当 Step 3 输出 `EMPTY` 时才执行此步骤。**

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_model.sh`（替换 `<TOKEN>`）：

```bash
#!/bin/bash
TOKEN="<TOKEN>"

curl -s -o /tmp/haiyi_model.json 'https://www.haiyi.art/api/v1/task/v5/config/model' \
  -X POST \
  -H 'Content-Type: application/json' \
  -H "token: $TOKEN" \
  -H 'x-app-id: web_global_seaart' \
  -H 'x-platform: web' \
  -H "x-page-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H "x-request-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H 'x-timezone: Asia/Shanghai'

python3 << 'PYEOF'
import json, sys
r = json.load(open('/tmp/haiyi_model.json'))
if r.get('status',{}).get('code') != 10000:
    print('FAIL:' + r.get('status',{}).get('msg','未知错误'))
    sys.exit(0)
d = r['data']
img = d.get('default_image_model',{}).get('art_model',{})
vid = d.get('default_video_model',{}).get('art_model',{})
print(f"IMAGE:{img.get('id','')},{img.get('model_ver_no','')}")
print(f"VIDEO:{vid.get('id','')},{vid.get('model_ver_no','')}")
PYEOF
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_model.sh`

根据输出和 `IS_VIDEO` 判断：
- `FAIL:xxx` → 告知用户失败并终止
- `IS_VIDEO` 为 true → 从 `VIDEO:` 行提取 `MODEL_ID` 和 `MODEL_VER_ID`（逗号分隔）
- `IS_VIDEO` 为 false → 从 `IMAGE:` 行提取 `MODEL_ID` 和 `MODEL_VER_ID`（逗号分隔）

### Step 5: 获取玩法参数（get_task_input_parameters_node）

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_params.sh`（替换 `<TOKEN>`、`<MODEL_ID>`、`<MODEL_VER_ID>`）：

```bash
#!/bin/bash
TOKEN="<TOKEN>"

curl -s -o /tmp/haiyi_params.json 'https://www.haiyi.art/api/v1/task/v5/model-gen-param' \
  -X POST \
  -H 'Content-Type: application/json' \
  -H "token: $TOKEN" \
  -H 'x-app-id: web_global_seaart' \
  -H 'x-platform: web' \
  -H "x-page-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H "x-request-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H 'x-timezone: Asia/Shanghai' \
  -d '{"model_no":"<MODEL_ID>","model_ver_no":"<MODEL_VER_ID>"}'

python3 << 'PYEOF'
import json, sys
r = json.load(open('/tmp/haiyi_params.json'))
if r.get('status',{}).get('code') != 10000:
    print('FAIL:' + r.get('status',{}).get('msg','未知错误'))
    sys.exit(0)
raw = r['data']
play_rules = []
for rule in raw.get('play_rules', []):
    meta = []
    for opt in rule.get('input_options', []) + rule.get('custom_params', []):
        item = {
            'id': opt.get('id',''),
            'key': opt.get('key',''),
            'name': opt.get('name',''),
            'type': opt.get('type',''),
            'desc': opt.get('desc',''),
        }
        if opt.get('options'):
            item['options'] = opt['options']
        if opt.get('setting'):
            item['setting'] = opt['setting']
        meta.append(item)
    play_rules.append({
        'id': rule.get('id',''),
        'name': rule.get('name',''),
        'intro': rule.get('intro',''),
        'default': rule.get('default', False),
        'vendor': rule.get('vendor',''),
        'meta': meta,
    })
result = {
    'success': True,
    'model_cap': raw.get('model_cap',''),
    'play_rules': play_rules,
}
print(json.dumps(result, ensure_ascii=False))
PYEOF
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_params.sh`

- `FAIL:xxx` → 告知用户失败并终止
- 成功 → 将输出的 JSON 赋值给 `PARAMS_JSON`，继续下一步

### Step 6: 构建创作参数（Agent 自行完成，不调用工具）

**这一步由你（Agent）直接分析 `PARAMS_JSON`，为用户构建 `play_rule_id` 和 `meta` 字典。不需要调用任何工具。**

#### 选择玩法

从 `play_rules` 中选择最匹配用户需求的玩法：
- 用户未指定 → 选 `default: true` 的玩法
- 用户指定了（如"文生图"、"图生视频"等）→ 根据 `name` / `intro` 匹配

记录选中的 `PLAY_RULE_ID` = `play_rules[i].id`

#### 构建 meta 字典

遍历选中玩法的 `play_rules[i].meta` 数组，将**每一项**的 `key` 作为 meta 字典的 key（**不可遗漏任何一个 key**），按以下规则赋值：

| 情况 | 赋值规则 |
|------|---------|
| 用户有明确要求 | 按用户要求赋值 |
| 有 `options` 数组，用户未指定 | 取 `default: true` 的选项的 `value` |
| 有 `options` 数组，用户有指定 | 从 `options[].value` 中选最接近用户意图的值（**不可自创值**） |
| 无 `options`，`type` 为 `prompt` | 填入用户描述的提示词内容 |
| 无 `options`，其他类型 | 使用合理默认值 |

**示例**：
- meta 配置 = `[{"key":"prompt","type":"prompt"}, {"key":"aspect_ratio","type":"select","options":[{"value":"1:1","default":true},{"value":"16:9"}]}]`
- 用户输入 = "生成一张横屏猫咪图片"
- → `meta = {"prompt": "猫咪", "aspect_ratio": "16:9"}`

#### 自检

构建完成后自行检查：
1. `PLAY_RULE_ID` 必须是 `play_rules` 中存在的 id
2. meta 的 key 数量必须与对应玩法的 meta 配置项数量**完全一致**
3. 有 `options` 的参数，value 必须在 `options[].value` 范围内

如果自检不通过，修正后重新构建。

### Step 7: 创建任务（creative_task_v2_node）

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_create.sh`（替换 `<TOKEN>` 和 `<PAYLOAD>`）：

```bash
#!/bin/bash
TOKEN="<TOKEN>"

curl -s -o /tmp/haiyi_create.json 'https://www.haiyi.art/api/v1/task/v5/create' \
  -X POST \
  -H 'Content-Type: application/json' \
  -H "token: $TOKEN" \
  -H 'x-app-id: web_global_seaart' \
  -H 'x-platform: web' \
  -H "x-page-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H "x-request-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H 'x-timezone: Asia/Shanghai' \
  -d '<PAYLOAD>'

python3 << 'PYEOF'
import json, sys
r = json.load(open('/tmp/haiyi_create.json'))
if r.get('status',{}).get('code') != 10000:
    print('FAIL:' + r.get('status',{}).get('msg','未知错误'))
    sys.exit(0)
t = r['data']
print(f"TASK_ID:{t.get('id','')}")
print(f"TYPE:{t.get('type',0)}")
PYEOF
```

其中 `<PAYLOAD>` 为 JSON 字符串，结构如下（由 Step 6 构建的值填充）：

```json
{
  "play_rule_id": "<PLAY_RULE_ID>",
  "meta": { ... },
  "model_no": "<MODEL_ID>",
  "model_ver_no": "<MODEL_VER_ID>",
  "speed_type": 2,
  "ss": 52
}
```

**注意**：将 JSON 写入脚本时，确保正确转义。推荐用 heredoc 方式传 payload：
```bash
PAYLOAD='<完整JSON字符串>'
# 然后 -d "$PAYLOAD"
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_create.sh`

- `FAIL:xxx` → 告知用户创建任务失败并终止
- 成功 → 提取 `TASK_ID` 和 `TASK_TYPE`，继续下一步

### Step 8: 轮询进度（query_task_progress_node）

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_poll.sh`（替换 `<TOKEN>` 和 `<TASK_ID>`）：

```bash
#!/bin/bash
TOKEN="<TOKEN>"
TASK_ID="<TASK_ID>"
MAX_POLL=900
INTERVAL=3
START=$(date +%s)

while true; do
  NOW=$(date +%s)
  ELAPSED=$((NOW - START))
  if [ $ELAPSED -ge $MAX_POLL ]; then
    echo "FAIL:轮询超时（${MAX_POLL}秒）"
    exit 0
  fi

  curl -s -o /tmp/haiyi_progress.json 'https://www.haiyi.art/api/v1/task/batch-progress' \
    -X POST \
    -H 'Content-Type: application/json' \
    -H "token: $TOKEN" \
    -H 'x-app-id: web_global_seaart' \
    -H 'x-platform: web' \
    -H "x-page-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
    -H "x-request-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
    -H 'x-timezone: Asia/Shanghai' \
    -d "{\"task_ids\":[\"$TASK_ID\"],\"ss\":52}"

  RESULT=$(python3 << 'PYEOF'
import json, sys
try:
    r = json.load(open('/tmp/haiyi_progress.json'))
except:
    print("RETRY")
    sys.exit(0)
if r.get('status',{}).get('code') != 10000:
    print("FAIL:" + r.get('status',{}).get('msg','接口异常'))
    sys.exit(0)
items = r.get('data',{}).get('items',[])
if not items:
    print("FAIL:任务不存在")
    sys.exit(0)
item = items[0]
status = item.get('status', 0)
progress = item.get('process', 0)
task_type = item.get('type', 0)
if status == 3:
    media = []
    is_video = task_type in (2,3,5,6)
    for img in item.get('img_uris') or []:
        e = {"url": img.get("url",""), "width": img.get("width",0), "height": img.get("height",0)}
        if is_video:
            e["type"] = "video"
        media.append(e)
    for vid in item.get('video_uris') or []:
        media.append({"url": vid.get("url",""), "type": "video", "poster": vid.get("cover_url","")})
    for vid in item.get('videos') or []:
        media.append({"url": vid.get("url",""), "type": "video", "poster": vid.get("cover_url","")})
    print("DONE:" + json.dumps(media, ensure_ascii=False))
elif status == 4:
    print("FAIL:" + item.get('status_desc','任务失败'))
else:
    print(f"PROGRESS:{progress}")
PYEOF
  )

  case "$RESULT" in
    DONE:*)  echo "$RESULT"; exit 0 ;;
    FAIL:*)  echo "$RESULT"; exit 0 ;;
    RETRY)   ;;
    PROGRESS:*) echo "$RESULT" ;;
  esac

  sleep $INTERVAL
done
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_poll.sh`

**注意**：该脚本会持续运行直到任务完成，设置 Shell 的 `block_until_ms` 为 **920000**（略大于 900 秒超时）。

根据最后一行输出判断：
- `DONE:[...]` → 解析 JSON 数组，提取所有 media URL，进入 Step 8
- `FAIL:xxx` → 告知用户任务失败

### Step 9: 展示结果

向用户展示生成结果：

**图片任务**：用 Markdown 图片语法展示每张图：
```
🎨 生成完成！

![生成的图片](url)
```

**视频任务**：展示视频链接：
```
🎬 视频生成完成！

[点击查看视频](url)
```

### Step 10: 清理临时文件

用 Shell 工具执行：
```
rm -f /tmp/haiyi_vector_model.sh /tmp/haiyi_vector_model.json /tmp/haiyi_model.sh /tmp/haiyi_model.json /tmp/haiyi_params.sh /tmp/haiyi_params.json /tmp/haiyi_create.sh /tmp/haiyi_create.json /tmp/haiyi_poll.sh /tmp/haiyi_progress.json
```
