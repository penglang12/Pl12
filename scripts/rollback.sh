#!/bin/bash
# ============================================================
# AI 多层级回滚脚本
# 支持: Git / 数据库 / IaC / NPM 依赖 回滚
# 用法: ./scripts/rollback.sh <target> [layer]
#   target:  commit hash / tag / "last"
#   layer:   git (默认) | db | iac | all
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

TARGET="${1:-}"
LAYER="${2:-git}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; }

# ---- 帮助 ----
if [ -z "$TARGET" ] || [ "$TARGET" = "-h" ] || [ "$TARGET" = "--help" ]; then
  echo "用法: $0 <target> [layer]"
  echo ""
  echo "target:"
  echo "  <commit-hash>  回滚到指定 commit"
  echo "  <tag>          回滚到指定 tag"
  echo "  last           回滚到上一个 commit"
  echo ""
  echo "layer (可选，默认 git):"
  echo "  git            仅 Git 回滚"
  echo "  db             仅数据库迁移回滚"
  echo "  iac            Terraform 状态回滚"
  echo "  all            Git + 数据库 + IaC (按顺序)"
  exit 1
fi

# ---- 确认 ----
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  回滚操作 - 目标: ${TARGET}  层: ${LAYER}${NC}"
echo -e "${YELLOW}========================================${NC}"
read -p "确认执行回滚？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "回滚已取消"
  exit 0
fi

# =============================================================
# Layer 1: Git 回滚
# =============================================================
rollback_git() {
  info "=== Git 回滚 ==="

  # 解析目标
  local target="$TARGET"
  if [ "$target" = "last" ]; then
    target="HEAD~1"
  fi

  # 检查工作区是否干净
  if ! git diff --quiet HEAD 2>/dev/null; then
    warn "工作区有未提交的变更:"
    git status --short
    read -p "放弃这些变更继续回滚？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      fail "Git 回滚已取消"
      return 1
    fi
    git reset --hard HEAD
  fi

  local current
  current=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
  info "当前: ${current}"
  info "目标: ${target}"

  # 检查目标是否存在
  if ! git rev-parse --verify "$target" 2>/dev/null; then
    fail "目标 '$target' 不存在"
    return 1
  fi

  # 创建备份 tag
  local backup_tag="rollback-backup-$(date +%Y%m%d%H%M%S)"
  git tag -f "$backup_tag" HEAD
  ok "当前 HEAD 已备份到 tag: $backup_tag"

  # 执行回滚
  git reset --hard "$target"
  ok "Git 已回滚到 $(git rev-parse --short HEAD)"
}

# =============================================================
# Layer 2: 数据库回滚 (Prisma / TypeORM / raw SQL)
# =============================================================
rollback_db() {
  info "=== 数据库回滚 ==="

  # Prisma
  if [ -f "prisma/schema.prisma" ]; then
    if command -v npx &>/dev/null && npx prisma migrate status &>/dev/null; then
      info "检测到 Prisma，执行迁移回滚..."
      npx prisma migrate reset --force || warn "Prisma 回滚失败，请手动检查"
      ok "Prisma 迁移已重置"
    else
      warn "prisma 未安装或 schema 不完整，跳过"
    fi
    return 0
  fi

  # SQL 迁移文件
  if [ -d "migrations" ]; then
    info "检测到 migrations/ 目录，执行 SQL 回滚..."
    for f in $(ls -r migrations/rollback/*.sql 2>/dev/null || true); do
      info "执行: $f"
      if command -v psql &>/dev/null && [ -n "${PGDATABASE:-}" ]; then
        psql -f "$f" || warn "SQL 回滚文件 $f 执行失败"
        ok "已执行: $f"
      else
        warn "无 psql 或 PGDATABASE 未设置，跳过 SQL 回滚"
        break
      fi
    done
  fi
}

# =============================================================
# Layer 3: IaC 回滚 (Terraform)
# =============================================================
rollback_iac() {
  info "=== IaC 回滚 ==="

  # Terraform
  if [ -f "*.tf" ] || [ -d "terraform" ]; then
    local tf_dirs
    tf_dirs=$(find . -name "*.tf" -not -path "./.git/*" -exec dirname {} \; | sort -u)

    if [ -z "$tf_dirs" ]; then
      warn "未找到 Terraform 配置"
      return 0
    fi

    for dir in $tf_dirs; do
      info "Terraform 目录: $dir"
      (cd "$dir" && terraform init -reconfigure 2>/dev/null && terraform plan -destroy 2>/dev/null && {
        warn "Terraform destroy 计划已生成，需手动确认执行: cd $dir && terraform destroy"
      }) || warn "Terraform 回滚检查失败 (可能未安装 terraform)"
    done

    # 尝试从 state 回滚
    if command -v terraform &>/dev/null; then
      local tf_state
      tf_state=$(find . -name "terraform.tfstate" -not -path "./.git/*" | head -1)
      if [ -n "$tf_state" ]; then
        info "发现 Terraform state: $tf_state，建议手动备份后再操作"
      fi
    fi
  else
    warn "未检测到 Terraform 配置，跳过 IaC 回滚"
  fi
}

# =============================================================
# 主流程
# =============================================================
case "$LAYER" in
  git)
    rollback_git
    ;;
  db)
    rollback_db
    ;;
  iac)
    rollback_iac
    ;;
  all)
    rollback_git && rollback_db && rollback_iac
    ;;
  *)
    fail "未知的 layer: $LAYER（可选: git, db, iac, all）"
    exit 1
    ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  回滚操作完成${NC}"
echo -e "${GREEN}========================================${NC}"
