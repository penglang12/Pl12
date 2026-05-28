# SessionStart Hook — 会话启动环境注入
# 在每次新会话开始时注入项目状态信息

$projectDir = $env:CLAUDE_PROJECT_DIR
if (-not $projectDir) {
    $projectDir = "C:\Users\PC\WorkBuddy\Claw"
}

Write-Host "🔧 Claw 环境注入:"

# Git 状态摘要
if (Test-Path "$projectDir\.git") {
    $gitBranch = & git -C $projectDir branch --show-current 2>$null
    $gitStatus = & git -C $projectDir status --short 2>$null | Measure-Object | Select-Object -ExpandProperty Count
    Write-Host "  Git: $gitBranch ($gitStatus 个未提交变更)"
}

# 项目健康检查
$toolsCount = (Get-ChildItem "$projectDir\tools" -Directory).Count
$skillsCount = (Get-ChildItem "$projectDir\.claude\skills" -Directory).Count
Write-Host "  打手层: $toolsCount 个工具 | 技能库: $skillsCount 个技能"

# 记忆系统状态
$memoryDir = "$projectDir\.workbuddy\memory"
if (Test-Path $memoryDir) {
    $memoryCount = (Get-ChildItem $memoryDir -Filter "*.md").Count
    Write-Host "  记忆系统: $memoryCount 条记录"
}

Write-Host "  模型: $env:ANTHROPIC_MODEL"
Write-Host "✅ Claw 就绪"
