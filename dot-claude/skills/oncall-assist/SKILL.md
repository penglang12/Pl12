# Skill: On-call 辅助

## 触发条件
用户说"收到告警"、"堆栈分析"、"紧急 Bug"、"on-call"、"生产事故"或类似表述。

## 执行步骤

### 1. 分析堆栈跟踪
将堆栈通过管道传给分析脚本：
```bash
cat stack_trace.txt | ./scripts/oncall-analyze.sh
```

### 2. 关联代码
自动从堆栈中提取：
- 错误类型和消息
- 涉及的文件和行号
- 最近修改这些文件的提交记录

### 3. 关联 Issue
使用 `/triage-issues` 检查是否有相关的已报告 Issue。

### 4. 实施修复
1. 创建修复分支: `git checkout -b fix/<short-description>`
2. 分析根因（使用 /debug 命令）
3. 编写修复代码
4. 创建 PR 草稿

### 5. 日志记录
将事故复盘写入 memory/ 目录，包含：
- 时间线
- 根因
- 修复方案
- 预防措施

## 自动化监控
仓库根目录的 `.github/workflows/oncall-monitor.yml` 每 2 小时自动检查关键 Issue。
