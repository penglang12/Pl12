# PreToolUse Hook — 安全守卫 + 密钥检测 + 分支保护
param(
    [string]$ToolName,
    [string]$Input,
    [string]$Output
)

$RED = "Red"; $YELLOW = "Yellow"; $GREEN = "Green"

# ===============================================
# 1. 分支保护 — 禁止直接操作 main/master
# ===============================================
try {
    $branch = git rev-parse --abbrev-ref HEAD 2>$null
    if ($branch -eq 'main' -or $branch -eq 'master') {
        Write-Warning "==============================================" -ForegroundColor $RED
        Write-Warning "  分支保护: 禁止在 '$branch' 分支上直接操作" -ForegroundColor $RED
        Write-Warning "  请使用 claude/xxx 分支开发，提 PR 合并" -ForegroundColor $YELLOW
        Write-Warning "=============================================="
        exit 1
    }
} catch {
    # 非 git 目录，跳过
}

# ===============================================
# 2. 危险命令拦截
# ===============================================
$dangerousPatterns = @(
    'rm\s+-rf',
    'Remove-Item\s+-Recurse\s+-Force',
    'del\s+/[fqs]',
    'format-volume',
    'Clear-Content',
    'Stop-Computer',
    'Restart-Computer',
    'git\s+push\s+--force',
    'git\s+push\s+-f\s+origin\s+main',
    'git\s+push\s+-f\s+origin\s+master'
)

foreach ($pattern in $dangerousPatterns) {
    if ($Input -match $pattern) {
        Write-Warning "==============================================" -ForegroundColor $RED
        Write-Warning "  拦截危险操作: 匹配模式 '$pattern'" -ForegroundColor $RED
        Write-Warning "  命令: $Input" -ForegroundColor $YELLOW
        Write-Warning "  如需放行请明确确认 (danger: true)" -ForegroundColor $YELLOW
        Write-Warning "=============================================="
        exit 1
    }
}

# ===============================================
# 3. 密钥扫描 — 拦截写入敏感信息
# ===============================================
if ($ToolName -in @('Write', 'Edit')) {
    # 从 Input 中提取内容部分
    $scanContent = $null
    if ($Input -match '"content":\s*"([^"]+)"') {
        $scanContent = $Matches[1]
    } elseif ($Input -match "new_string = '([^']+)'") {
        $scanContent = $Matches[1]
    } else {
        $scanContent = $Input
    }

    if ($scanContent) {
        # 调用 secret-scanner 检查内容
        $scanResult = & "C:\Users\PC\WorkBuddy\Claw\.claude\hooks\secret-scanner.ps1" -Content "$scanContent" -Mode "scan" 2>&1
        $highMatch = $scanResult | Select-String -Pattern "High: (\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }

        if ($highMatch -and [int]$highMatch -gt 0) {
            Write-Warning "==============================================" -ForegroundColor $RED
            Write-Warning "  [SECURITY] 检测到高风险密钥泄露！" -ForegroundColor $RED
            Write-Warning "  已阻止写入操作。请移除密钥后重试。" -ForegroundColor $YELLOW
            Write-Warning "=============================================="
            exit 1
        }
    }
}

# ===============================================
# 4. 提交前审查提醒 — 检测 git commit
# ===============================================
if ($ToolName -eq 'Bash' -and $Input -match 'git\s+commit') {
    Write-Warning "==============================================" -ForegroundColor $YELLOW
    Write-Warning "  [审查护航] 检测到 git commit 操作" -ForegroundColor $YELLOW
    Write-Warning "  请确保已执行代码审查后再提交" -ForegroundColor $YELLOW
    Write-Warning "  运行 /review-deep 进行多维度审查" -ForegroundColor $YELLOW
    Write-Warning "  运行 /debug 进行调试复盘（如适用）" -ForegroundColor $YELLOW
    Write-Warning "  如确认跳过审查，请忽略此提醒" -ForegroundColor $GREEN
    Write-Warning "=============================================="
}

# ===============================================
# 5. 审计日志
# ===============================================
$logDir = "$env:USERPROFILE\.claude\logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}
$logEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Tool: $ToolName | Branch: $branch | Input: $($Input.Substring(0, [Math]::Min(150, $Input.Length)))"
Add-Content -Path "$logDir\tool-calls.log" -Value $logEntry

exit 0
