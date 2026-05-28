# Haiyi.art (SeaArt) SMS Login

执行以下交互式登录流程，严格按顺序操作。

## 输出规范（重要）

**对用户隐藏所有技术细节：**

1. 需要执行的脚本内容，必须先用 **Write 工具**写入 `/tmp/` 下的临时文件，再用 **Shell 工具**执行 `bash <文件路径>`。绝不要把脚本内容直接写在 Shell 调用中。
2. 执行 Shell 时 description 写当前 Step 名称。
3. 只向用户展示最终结果（成功/失败），不展示中间过程。

## 交互流程

### Step 1: 询问手机号

直接向用户发送以下消息（不要使用 AskQuestion 工具），然后**停止并等待用户回复**：

> 📱 请在下方输入您的手机号（无需 86 前缀，例如：180*****717）

用户回复后，拼接为 `86-<手机号>` 格式，赋值给变量 `PHONE`

### Step 2: 发送短信验证码

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_sms.sh`（将 `$PHONE` 替换为实际手机号）：

```bash
#!/bin/bash
PHONE="<用户手机号>"
DEVICE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
BROWSER_ID=$(echo -n "$DEVICE_ID" | md5)
PAGE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
REQUEST_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')

# 保存设备信息供后续步骤使用
cat > /tmp/haiyi_device.env << EOF
DEVICE_ID=$DEVICE_ID
BROWSER_ID=$BROWSER_ID
PAGE_ID=$PAGE_ID
EOF

curl -s -o /tmp/haiyi_sms.json 'https://www.haiyi.art/api/v1/account/login-in/sms' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zhCN' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'origin: https://www.haiyi.art' \
  -H 'pragma: no-cache' \
  -H 'referer: https://www.haiyi.art/' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' \
  -H "x-app-id: web_global_seaart" \
  -H "x-browser-id: $BROWSER_ID" \
  -H "x-device-id: $DEVICE_ID" \
  -H "x-page-id: $PAGE_ID" \
  -H "x-platform: web" \
  -H "x-request-id: $REQUEST_ID" \
  -H "x-timezone: Asia/Shanghai" \
  -b "deviceId=$DEVICE_ID; browserId=$BROWSER_ID; pageId=$PAGE_ID" \
  --data-raw "{\"phone_number\":\"86-$PHONE\"}"

python3 -c "
import json
r = json.load(open('/tmp/haiyi_sms.json'))
if r.get('status',{}).get('code') == 10000:
    print('OK')
else:
    print('FAIL:' + r.get('status',{}).get('msg','未知错误'))
"
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_sms.sh`

根据输出判断：
- 输出 `OK` → 继续下一步
- 输出 `FAIL:xxx` → 告知用户发送失败并终止

### Step 3: 询问验证码

验证码发送成功后，直接向用户发送以下消息（不要使用 AskQuestion 工具），然后**停止并等待用户回复**：

> ✅ 验证码已发送，请在下方输入收到的 6 位验证码

用户回复后赋值给变量 `CAPTCHA`

### Step 4: 提交登录

**先用 Write 工具**将以下脚本写入 `/tmp/haiyi_login.sh`（将 `$PHONE` 和 `$CAPTCHA` 替换为实际值）：

```bash
#!/bin/bash
PHONE="<用户手机号>"
CAPTCHA="<验证码>"
source /tmp/haiyi_device.env

REQUEST_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
TIMESTAMP=$(python3 -c "import time; print(int(time.time()*1000))")
RANDOM_STR=$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | head -c 10)
PROCESS_ID="flow_id_${TIMESTAMP}_${RANDOM_STR}"

curl -s -o /tmp/haiyi_login.json 'https://www.haiyi.art/api/v1/account/login-in/cli' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zhCN' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'origin: https://www.haiyi.art' \
  -H 'pragma: no-cache' \
  -H 'referer: https://www.haiyi.art/' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' \
  -H "x-app-id: web_global_seaart" \
  -H "x-browser-id: $BROWSER_ID" \
  -H "x-device-id: $DEVICE_ID" \
  -H "x-page-id: $PAGE_ID" \
  -H "x-platform: web" \
  -H "x-request-id: $REQUEST_ID" \
  -H "x-timezone: Asia/Shanghai" \
  -b "deviceId=$DEVICE_ID; browserId=$BROWSER_ID; pageId=$PAGE_ID" \
  --data-raw "{\"phone_number\":\"86-$PHONE\",\"captcha\":\"$CAPTCHA\",\"type\":9,\"om5\":\"\",\"source\":\"recommendPage_hot\",\"process_id\":\"$PROCESS_ID\",\"device_code\":\"skill\"}"

python3 << 'PYEOF'
import json
r = json.load(open('/tmp/haiyi_login.json'))
if r.get('status',{}).get('code') == 10000:
    token = r['data']['token']
    name = r['data']['account'].get('name', '')
    print(f'OK:{name}')
    print(f'TOKEN={token}')
else:
    print('FAIL:' + r.get('status',{}).get('msg','未知错误'))
PYEOF
```

**然后用 Shell 工具**执行：`bash /tmp/haiyi_login.sh`

根据输出判断：
- 输出 `OK:xxx` → 提取 name 和 TOKEN，继续下一步
- 输出 `FAIL:xxx` → 告知用户登录失败

### Step 5: 保存 Token

从 Step 4 的输出中提取 TOKEN 值，使用 Write 工具将 token 写入本命令同目录下的 `token.md` 文件。

然后告知用户：「登录成功！欢迎 {name}，token 已保存。」

如果登录失败，告知用户错误信息，提示重新执行 `/haiyi-login:login`。

### Step 6: 清理临时文件

用 Shell 工具执行：`rm -f /tmp/haiyi_sms.sh /tmp/haiyi_login.sh /tmp/haiyi_device.env /tmp/haiyi_sms.json /tmp/haiyi_login.json`

## 登录响应结构参考

```json
{
  "data": {
    "account": {"id": "...", "name": "用户昵称"},
    "token": "eyJhbGciOiJS..."
  },
  "status": {"code": 10000, "msg": "success"}
}
```

## Common Headers 参考

| Header | 说明 |
|--------|------|
| `x-app-id` | 固定 `web_global_seaart` |
| `x-browser-id` | DEVICE_ID 的 MD5 |
| `x-device-id` | UUID v4 |
| `x-page-id` | UUID v4 |
| `x-request-id` | 每次请求重新生成 UUID v4 |
| `x-platform` | 固定 `web` |
| `x-timezone` | `Asia/Shanghai` |

Cookie 中 `deviceId`、`browserId`、`pageId` 需与对应 Header 值一致。
