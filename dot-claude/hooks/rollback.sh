#!/bin/bash
# rollback.sh — 一键回滚部署
# 被 /deploy-release 命令调用
# 用法: ./rollback.sh <target-tag>

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TARGET_TAG="${1:-}"
if [ -z "$TARGET_TAG" ]; then
    echo -e "${RED}[ROLLBACK] 错误: 请指定回滚目标版本${NC}"
    echo "用法: $0 <target-tag>"
    exit 1
fi

echo -e "${YELLOW}[ROLLBACK] 开始回滚到 $TARGET_TAG${NC}"

# ============================================
# 1. 验证目标标签存在
# ============================================
if ! git rev-parse "$TARGET_TAG" >/dev/null 2>&1; then
    echo -e "${RED}[ROLLBACK] 错误: 标签 $TARGET_TAG 不存在${NC}"
    exit 1
fi

# ============================================
# 2. 记录当前状态
# ============================================
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${YELLOW}[ROLLBACK] 当前分支: $CURRENT_BRANCH${NC}"

# ============================================
# 3. 创建备份分支
# ============================================
BACKUP_BRANCH="rollback/backup-$(date +%Y%m%d%H%M%S)"
echo -e "${YELLOW}[ROLLBACK] 创建备份分支: $BACKUP_BRANCH${NC}"
git branch "$BACKUP_BRANCH"

# ============================================
# 4. 执行回滚
# ============================================
echo -e "${YELLOW}[ROLLBACK] 回滚到 $TARGET_TAG...${NC}"
git reset --hard "$TARGET_TAG"

# 如果是主分支，强制推送到远程
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    echo -e "${YELLOW}[ROLLBACK] 推送回滚到远程 $CURRENT_BRANCH...${NC}"
    git push --force-with-lease origin "$CURRENT_BRANCH"
fi

echo -e "${GREEN}[ROLLBACK] 回滚完成。当前 HEAD: $(git rev-parse --short HEAD)${NC}"
echo -e "${GREEN}[ROLLBACK] 备份分支: $BACKUP_BRANCH (如需恢复)$NC}"

exit 0
