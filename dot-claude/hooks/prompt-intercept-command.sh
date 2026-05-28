#!/bin/bash
# UserPromptSubmit Hook — 零 API 轮次命令拦截模式
# 拦截以 ! 开头的命令，本地执行不消耗 API
# 参考: https://github.com/kylesnowschwartz/prompt-intercept-pattern

INPUT="$1"
COMMAND="${INPUT#!}"

case "$INPUT" in
    !status)
        echo "📊 Claw 项目状态"
        echo "  启动时间: $(date)"
        echo "  工作目录: $(pwd)"
        echo "  模型: $ANTHROPIC_MODEL"
        echo "  缓存: ${CLAUDE_CODE_ATTRIBUTION_HEADER:-disabled}"
        exit 2
        ;;
    !memory)
        echo "📝 读取最新记忆..."
        cat .workbuddy/memory/MEMORY.md 2>/dev/null || echo "⚠️ 无记忆文件"
        exit 2
        ;;
    !tools)
        echo "🔧 可用工具列表:"
        ls tools/ 2>/dev/null || echo "⚠️ tools/ 目录为空"
        exit 2
        ;;
esac

exit 0
