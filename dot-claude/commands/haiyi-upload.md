# Haiyi.art 图片上传

将本地图片上传至 Haiyi 云存储，返回远程 URL。

对应后端接口：`POST /api/upload/image-v2`（multipart/form-data）

## 输出规范

1. 需要执行的脚本内容，必须先用 **Write 工具**写入 `/tmp/` 下的临时文件，再用 **Shell 工具**执行 `bash <文件路径>`。绝不要把脚本内容直接写在 Shell 调用中。
2. 只向用户展示最终结果（成功的远程 URL / 失败原因），不展示中间过程和 JSON。

## 接口参数说明

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `file` | file | 是 | 图片文件二进制数据 |
| `filename` | string | 是 | 原始文件名（用于解析扩展名） |
| `bucket` | string | 否 | 存储桶别名，默认 `image` |
| `category` | string | 否 | 风控场景（例如：`nsfw`） |
| `max_nsfw_level` | int | 否 | 最大 NSFW 级别（> 该值则拦截），固定传 `3` |
| `file_474` | file | 否 | 客户端提供的 474 宽度低码 webp 图（可选优化） |

## 输入参数

调用本 Skill 前，调用方需提供以下变量：

| 变量 | 说明 | 是否必须 |
|------|------|---------|
| `TOKEN` | 用户登录 token | 是 |
| `LOCAL_IMAGE_PATH` | 本地图片的绝对路径 | 是 |

## 上传流程

### Step 1: 校验本地文件

使用 Shell 工具检查文件是否存在、是否为支持的图片格式、是否超过 30MB 限制。

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_upload_check.sh`（替换 `<LOCAL_IMAGE_PATH>`）：

```bash
#!/bin/bash
FILE_PATH="<LOCAL_IMAGE_PATH>"

if [ ! -f "$FILE_PATH" ]; then
  echo "FAIL:文件不存在: $FILE_PATH"
  exit 0
fi

FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH" 2>/dev/null)
if [ "$FILE_SIZE" -gt 31457280 ]; then
  echo "FAIL:文件超过 30MB 限制 (${FILE_SIZE} bytes)"
  exit 0
fi

FILENAME=$(basename "$FILE_PATH")
EXT="${FILENAME##*.}"
EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')

case "$EXT_LOWER" in
  jpg|jpeg|png|gif|webp|bmp|tiff|tif)
    echo "OK:${FILENAME},${FILE_SIZE}"
    ;;
  *)
    echo "FAIL:不支持的图片格式: .${EXT_LOWER}"
    ;;
esac
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_upload_check.sh`

根据输出判断：
- `OK:<filename>,<size>` → 提取 `FILENAME` 和 `FILE_SIZE`，继续下一步
- `FAIL:xxx` → 告知调用方文件校验失败并终止

### Step 2: 上传图片

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_upload.sh`（替换 `<TOKEN>`、`<LOCAL_IMAGE_PATH>`、`<FILENAME>`）：

```bash
#!/bin/bash
TOKEN="<TOKEN>"
FILE_PATH="<LOCAL_IMAGE_PATH>"
FILENAME="<FILENAME>"

HTTP_CODE=$(curl -sS -o /tmp/haiyi_upload_result.json -w "%{http_code}" \
  'https://www.haiyi.art/api/upload/image-v2' \
  -X POST \
  -H "token: $TOKEN" \
  -H 'x-app-id: web_global_seaart' \
  -H 'x-platform: web' \
  -H "x-page-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H "x-request-id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
  -H 'x-timezone: Asia/Shanghai' \
  -F "file=@${FILE_PATH};type=$(file --mime-type -b "${FILE_PATH}")" \
  -F "filename=${FILENAME}" \
  -F "bucket=image" \
  -F "category=nsfw" \
  -F "max_nsfw_level=3")

python3 - "$HTTP_CODE" << 'PYEOF'
import json, sys, os
http_code = sys.argv[1] if len(sys.argv) > 1 else ''
path = '/tmp/haiyi_upload_result.json'

raw = ''
try:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()
except Exception as e:
    print(f"FAIL:读取响应文件失败: {e} (HTTP {http_code})")
    sys.exit(0)

if not raw.strip():
    print(f"FAIL:服务端返回空响应 (HTTP {http_code})")
    sys.exit(0)

try:
    r = json.loads(raw)
except Exception as e:
    snippet = raw[:300].replace('\n', ' ')
    print(f"FAIL:响应非 JSON (HTTP {http_code}): {snippet}")
    sys.exit(0)

code = r.get('status', {}).get('code', 0)
if code == 30005:
    print("FAIL:图片违反 NSFW 安全策略，请更换图片")
    sys.exit(0)
if code != 10000:
    msg = r.get('status', {}).get('msg', '未知错误')
    print(f"FAIL:{msg} (code={code}, HTTP {http_code})")
    sys.exit(0)

data = r.get('data', {})
url = data.get('url', '')
signed = data.get('signed', '')

if not url:
    print("FAIL:响应中缺少 url 字段")
    sys.exit(0)

print(f"URL:{url}")
if signed:
    print(f"SIGNED:{signed}")
PYEOF
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_upload.sh`

根据输出判断：
- `URL:<remote_url>` → 提取 `REMOTE_URL`（即上传后的远程图片地址）
- `SIGNED:<signed_data>` → 提取 `SIGNED_DATA`（图片签名/鉴定数据，可选）
- `FAIL:xxx` → 告知调用方上传失败并终止

### Step 3: 返回结果

上传成功后，返回以下信息给调用方：

| 变量 | 说明 |
|------|------|
| `REMOTE_URL` | 远程图片访问地址（替换原本地路径使用） |
| `SIGNED_DATA` | 图片签名数据（可选，用于后续鉴权场景） |

### Step 4: 清理临时文件

用 Shell 工具执行：
```
rm -f /tmp/haiyi_upload_check.sh /tmp/haiyi_upload.sh /tmp/haiyi_upload_result.json
```
