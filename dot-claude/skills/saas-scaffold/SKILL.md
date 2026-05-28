# Skill: SaaS 项目脚手架

## 触发条件
用户说"创建 SaaS 项目"、"新建全栈项目"或类似表述。

## 前置条件
确认用户已安装 Node.js 18+ 和 Git。

## 执行步骤
1. 询问用户项目名称和核心功能列表。
2. 使用 `npx create-next-app@latest` 初始化 Next.js 项目。
3. 安装核心依赖：next-auth, stripe, prisma, tailwindcss。
4. 创建基础目录结构：`src/app`, `src/components`, `src/lib`, `prisma`, `docs`。
5. 生成 `.env.example` 文件，包含必要的环境变量模板。
6. 创建 `docker-compose.yml` 用于本地数据库。
7. 初始化 Git 并完成首次提交。
8. 告知用户后续需要配置的具体步骤（Stripe Key、OAuth等）。
