#!/bin/bash
# ============================================================
# 跨模型路由脚本（Ai头号玩家 聚合平台版）
# 通过统一 API 调用 GPT / Claude / Gemini / 媒体模型
# 用法: ./model-router.sh <model> <prompt|file|stdin>
# 模型: gpt, claude, gemini, deepseek, list
# ============================================================
set -euo pipefail

API_KEY="sk-e58f7e4321ba405a405802bf13282fb7f283ac753a182f41"
BASE="https://api.lk888.ai/api"
PY="/c/Users/PC/AppData/Local/Programs/Python/Python312/python.exe"
MODEL="${1:-}"
PROMPT="${2:-/dev/stdin}"

[ -z "$MODEL" ] && { echo "用法: $0 <gpt|claude|gemini|deepseek|list|media> [prompt]"; exit 1; }

if [ "$PROMPT" = "/dev/stdin" ]; then
  PROMPT_TEXT=$(cat)
else
  PROMPT_TEXT=$(cat "$PROMPT" 2>/dev/null || echo "$PROMPT")
fi

case "$MODEL" in
  list)
    echo "=== 聊天模型 ==="
    curl -s --max-time 15 -H "Authorization: Bearer $API_KEY" \
      "$BASE/v1/skills/models?type=chat" \
      | "$PY" -c "
import sys, json
d = json.load(sys.stdin)
models = d.get('models') or d.get('data', {}).get('models') or []
for m in models:
    print(f\"{m.get('name','?')} | {m.get('display_name','?')} | {m.get('api_format','?')}\")
"
    echo ""
    echo "=== 媒体模型 ==="
    curl -s --max-time 15 -H "Authorization: Bearer $API_KEY" \
      "$BASE/v1/skills/models" \
      | "$PY" -c "
import sys, json
d = json.load(sys.stdin)
models = d.get('models') or []
for m in models:
    if m.get('type') != 'chat':
        print(f\"{m.get('name','?')} | {m.get('display_name','?')} | {m.get('type','?')}\")
"
    ;;

  gpt|gpt5|gpt4|openai)
    [ -z "$PROMPT_TEXT" ] && PROMPT_TEXT="你好"
    "$PY" -c "
import json
p = '''${PROMPT_TEXT//\'/\\x27}'''
print(json.dumps({'model':'gpt-5.5','messages':[{'role':'user','content':p}],'stream':False}))
" | curl -s --max-time 120 -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d @- "$BASE/v1/chat/completions" \
    | "$PY" -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('choices',[{}])[0].get('message',{}).get('content') or d.get('error',{}).get('message') or '未知响应')
"
    ;;

  claude|sonnet|opus)
    [ -z "$PROMPT_TEXT" ] && PROMPT_TEXT="你好"
    "$PY" -c "
import json
p = '''${PROMPT_TEXT//\'/\\x27}'''
print(json.dumps({'model':'claude-sonnet-4-6','max_tokens':4096,'messages':[{'role':'user','content':p}]}))
" | curl -s --max-time 120 -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d @- "$BASE/v1/messages" \
    | "$PY" -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('content',[{}])[0].get('text') or d.get('error',{}).get('message') or '未知响应')
"
    ;;

  gemini|gemini3)
    [ -z "$PROMPT_TEXT" ] && PROMPT_TEXT="你好"
    "$PY" -c "
import json
p = '''${PROMPT_TEXT//\'/\\x27}'''
print(json.dumps({'contents':[{'parts':[{'text':p}],'role':'user'}]}))
" | curl -s --max-time 120 -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d @- "$BASE/v1beta/models/gemini-3.1-pro-preview:generateContent" \
    | "$PY" -c "
import sys, json
d = json.load(sys.stdin)
candidates = d.get('candidates',[{}])
parts = candidates[0].get('content',{}).get('parts',[{}]) if candidates else [{}]
print(parts[0].get('text') or d.get('error',{}).get('message') or '未知响应')
"
    ;;

  deepseek)
    DS_KEY="${DEEPSEEK_API_KEY:-${ANTHROPIC_AUTH_TOKEN:-}}"
    [ -z "$DS_KEY" ] && { echo "[ERROR] 请设置 DEEPSEEK_API_KEY"; exit 1; }
    [ -z "$PROMPT_TEXT" ] && PROMPT_TEXT="你好"
    "$PY" -c "
import json
p = '''${PROMPT_TEXT//\'/\\x27}'''
print(json.dumps({'model':'deepseek-chat','messages':[{'role':'user','content':p}],'stream':False}))
" | curl -s --max-time 120 -H "Authorization: Bearer $DS_KEY" \
      -H "Content-Type: application/json" \
      -d @- "https://api.deepseek.com/chat/completions" \
    | "$PY" -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('choices',[{}])[0].get('message',{}).get('content') or d.get('error',{}).get('message') or '未知响应')
"
    ;;

  media|video|image)
    echo "=== 媒体模型 ==="
    curl -s --max-time 15 -H "Authorization: Bearer $API_KEY" \
      "$BASE/v1/skills/models" \
      | "$PY" -c "
import sys, json
d = json.load(sys.stdin)
models = d.get('models') or []
for m in models:
    if m.get('type') != 'chat':
        print(f\"{m.get('name','?')} | {m.get('display_name','?')} | {m.get('type','?')} | {m.get('tags',[])}\")
"
    echo ""
    echo "用法举例: echo '描述内容' | ./model-router.sh generate <model_name>"
    ;;

  generate)
    MEDIA_MODEL="${3:-}"
    [ -z "$MEDIA_MODEL" ] && { echo "[ERROR] 请指定媒体模型名称"; exit 1; }
    [ -z "$PROMPT_TEXT" ] && { echo "[ERROR] 请输入提示词"; exit 1; }
    "$PY" -c "
import json
print(json.dumps({'model':'$MEDIA_MODEL','prompt':'''${PROMPT_TEXT//\'/\\x27}''','params':{},'count':1}))
" | curl -s --max-time 30 -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d @- "$BASE/v1/media/generate" \
    | "$PY" -m json.tool
    ;;

  balance)
    curl -s --max-time 10 -H "Authorization: Bearer $API_KEY" \
      "$BASE/v1/skills/balance" | "$PY" -m json.tool
    ;;

  *)
    echo "[ERROR] 未知模型: $MODEL"
    echo "可用: gpt, claude, gemini, deepseek, list, media, generate, balance"
    exit 1
    ;;
esac
