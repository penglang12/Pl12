#!/bin/bash
# ============================================================
# On-call 辅助脚本
# 功能: 分析堆栈跟踪、关联最近提交、生成修复摘要
# 用法: ./oncall-analyze.sh <stack_trace_file|stdin>
# ============================================================
set -euo pipefail

STACK_TRACE="${1:-/dev/stdin}"
REPO_DIR="${2:-.}"

echo "=== On-call 分析 ==="
echo "堆栈文件: $STACK_TRACE"
echo "仓库目录: $REPO_DIR"
echo ""

# 1. 提取关键信息
echo "--- 提取的堆栈信息 ---"
ERROR_LINE=$(grep -iE 'error|exception|fatal|panic|at\s+.*:' "$STACK_TRACE" | head -10 || true)
echo "$ERROR_LINE"
echo ""

# 2. 找文件名/行号引用
echo "--- 关联文件 ---"
FILES=$(grep -oE '(/[a-zA-Z0-9_./-]+\.[a-z]+):?[0-9]*' "$STACK_TRACE" | sort -u | head -10 || true)
if [ -n "$FILES" ]; then
  echo "$FILES"
  # 在仓库中搜索匹配的文件
  echo ""
  echo "--- 仓库中匹配的文件 ---"
  for f in $FILES; do
    basename_f=$(basename "$f")
    found=$(find "$REPO_DIR" -name "$basename_f" -not -path "./.git/*" 2>/dev/null | head -3)
    if [ -n "$found" ]; then
      echo "  找到: $found"
    fi
  done
fi
echo ""

# 3. 关联最近提交
echo "--- 影响文件最近提交 ---"
cd "$REPO_DIR"
for f in $FILES; do
  basename_f=$(basename "$f")
  found_files=$(find . -name "$basename_f" -not -path "./.git/*" 2>/dev/null | head -1)
  if [ -n "$found_files" ]; then
    echo "文件: $found_files"
    git log --oneline -5 -- "$found_files" 2>/dev/null | sed 's/^/  /' || true
  fi
done

# 4. 建议修复步骤
echo ""
echo "--- 建议修复步骤 ---"
echo "1. 确认错误类型和影响范围"
echo "2. 检查上述文件中的最近变更"
echo "3. 创建修复分支: git checkout -b fix/describe-the-bug"
echo "4. 实现修复并运行测试"
echo "5. 提交并创建 PR"
