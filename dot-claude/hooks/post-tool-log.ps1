# PostToolUse Hook — 执行后审计日志
# 在工具调用后记录执行结果，用于审计和回溯

param(
    [string]$ToolName,
    [string]$Input,
    [string]$Output
)

$logDir = "$env:USERPROFILE\.claude\logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

$status = "成功"
$outputPreview = $Output.Substring(0, [Math]::Min(100, $Output.Length))

$logEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [完成] $ToolName | 状态: $status | 输出: $outputPreview"
Add-Content -Path "$logDir\tool-calls.log" -Value $logEntry
