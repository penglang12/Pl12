# PostToolUse Hook — 写入后密钥扫描
param(
    [string]$ToolName,
    [string]$Input,
    [string]$Output
)

try {
    # 从 Output 中提取文件路径（Write 和 Edit 会返回文件路径）
    $filePath = $null
    if ($Output -match '"file_path":\s*"([^"]+)"') {
        $filePath = $Matches[1]
    } elseif ($Output -match "The file (.+?) has been updated") {
        $filePath = $Matches[1]
    } elseif ($Output -match "File created successfully at: (.+)") {
        $filePath = $Matches[1]
    }

    if (-not $filePath) {
        # 从 Input 中提取
        if ($Input -match '"file_path":\s*"([^"]+)"') {
            $filePath = $Matches[1]
        }
    }

    if ($filePath -and (Test-Path $filePath)) {
        $scanResult = & "C:\Users\PC\WorkBuddy\Claw\.claude\hooks\secret-scanner.ps1" -FilePath $filePath -Mode "scan" 2>&1 | Out-String
        $highCount = 0
        $mediumCount = 0

        if ($scanResult -match "High:\s*(\d+)") { $highCount = [int]$Matches[1] }
        if ($scanResult -match "Medium:\s*(\d+)") { $mediumCount = [int]$Matches[1] }

        if ($highCount -gt 0 -or $mediumCount -gt 0) {
            Write-Warning "=============================================="
            Write-Warning "  [SECURITY] 警告: 文件包含敏感信息!"
            Write-Warning "  文件: $filePath"
            Write-Warning "  High: $highCount | Medium: $mediumCount"
            Write-Warning "  建议: 不要提交含密钥的文件到仓库!"
            Write-Warning "=============================================="
        }

        # 记录到审计日志
        $logDir = "$env:USERPROFILE\.claude\logs"
        $auditEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [POST-SCAN] $filePath | High: $highCount | Medium: $mediumCount"
        Add-Content -Path "$logDir\security-audit.log" -Value $auditEntry
    }
} catch {
    # 静默失败，不阻塞流程
}
