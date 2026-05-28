# PostToolUse Hook — Token/成本追踪
# 记录每次工具调用的预估 Token 消耗

param(
    [string]$ToolName,
    [string]$Input,
    [string]$Output
)

$logDir = "$env:USERPROFILE\.claude\cost-logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

$date = Get-Date -Format 'yyyy-MM-dd'
$todayLog = "$logDir\$date.csv"
$model = if ($env:ANTHROPIC_MODEL) { $env:ANTHROPIC_MODEL } else { "deepseek-chat" }

# 简单预估：输入 Token ≈ Input 长度 ÷ 4，输出 Token ≈ Output 长度 ÷ 4
$inputTokens = [Math]::Max(1, [Math]::Ceiling($Input.Length / 4))
$outputTokens = [Math]::Max(1, [Math]::Ceiling($Output.Length / 4))

# DeepSeek 定价（近似）
$pricePer1KInput = 0.00014  # $0.14/M tokens → $0.00014/K
$pricePer1KOutput = 0.00028 # $0.28/M tokens
$estimatedCost = ($inputTokens * $pricePer1KInput + $outputTokens * $pricePer1KOutput) / 1000

# CSV 表头（如文件不存在）
if (-not (Test-Path $todayLog)) {
    "Timestamp,Tool,Model,InputTokens,OutputTokens,EstCostUSD" | Out-File $todayLog
}

$entry = "$(Get-Date -Format 'HH:mm:ss'),$ToolName,$model,$inputTokens,$outputTokens,$([Math]::Round($estimatedCost, 6))"
Add-Content -Path $todayLog -Value $entry

# 保留最近 30 天的日志，自动清理旧的
Get-ChildItem $logDir -Filter "*.csv" | Where-Object { $_.Name -lt (Get-Date).AddDays(-30).ToString('yyyy-MM-dd') } | Remove-Item -Force
