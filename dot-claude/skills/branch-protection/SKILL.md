# Skill: 分支保护强制

## 触发条件
- 用户说"创建分支"、"提 PR"、"推送代码"
- 分支名不符合 `claude/` 前缀规范时自动触发

## 保护层级

### 第一层: Git pre-push hook（本地）
- 位置: `.git/hooks/pre-push`
- 作用: 推送时检查分支名，不符合规范直接拒绝
- 允许前缀: `claude/`, `feature/`, `fix/`, `hotfix/`, `chore/`, `dependabot/`

### 第二层: GitHub Actions（云端）
- 位置: `.github/workflows/branch-protection.yml`
- 作用: PR 到 main/master/develop 时检查分支名
- 附加: 软检查 REVIEW_DONE 标记

### 第三层: 自动修正
当分支名不合规时，自动生成合规分支名：
```bash
# 自动转换分支名
current_branch=$(git rev-parse --abbrev-ref HEAD)
new_branch="claude/${current_branch//[^a-z0-9-]/-}"
git branch -m "$current_branch" "$new_branch"
```

## 使用说明
1. 创建分支时请使用 `claude/` 前缀
2. 或运行 `git checkout -b claude/your-feature-name`
3. 推送前 pre-push hook 自动验证
4. 提 PR 时 GitHub Actions 二次验证
