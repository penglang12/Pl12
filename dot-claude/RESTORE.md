# 恢复指南

## 恢复配置到新环境

```bash
# 将备份的配置复制回 ~/.claude/
cp -r dot-claude/skills ~/.claude/skills
cp -r dot-claude/agents ~/.claude/agents
cp -r dot-claude/hooks ~/.claude/hooks
cp -r dot-claude/commands ~/.claude/commands
cp dot-claude/CLAUDE.md ~/.claude/CLAUDE.md
cp dot-claude/settings.json ~/.claude/settings.json
cp dot-claude/model-router.json ~/.claude/model-router.json

# 恢复脚本
cp -r scripts ~/scripts
```

## 环境依赖
- GITHUB_TOKEN: 经典 PAT（repo + workflow 权限）
- 需安装 gh CLI、Playwright、Python 3.12+
- Ai头号玩家 API Key 在 model-router.sh 中
