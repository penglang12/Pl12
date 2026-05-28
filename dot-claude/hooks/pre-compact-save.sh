#!/bin/bash
# PreCompact Hook — 在上下文压缩前保存关键状态
# 防止压缩后丢失当前任务目标、修改文件列表和待办事项

OUTPUT_FILE="$HOME/.claude/compaction-state/$(date +%s).md"
mkdir -p "$HOME/.claude/compaction-state"

cat > "$OUTPUT_FILE" << 'STATE'
# 压缩前状态快照

## 当前目标
(由 PreCompact Hook 自动保存)

## 已修改文件
- (Hook 在压缩前保存此状态)

## 未完成的工作
- (压缩后需继续的任务)

## 下一步
- (压缩后的延续向量)
STATE

echo "Context state saved to $OUTPUT_FILE"
