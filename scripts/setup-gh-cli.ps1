param(
    [string]$GithubToken = ""
)

Write-Host "=== GitHub CLI 安装与配置 ===" -ForegroundColor Cyan
Write-Host ""

# 检查 gh 是否已安装
$ghPath = Get-Command "gh" -ErrorAction SilentlyContinue
if ($ghPath) {
    Write-Host "✅ gh CLI 已安装: $($ghPath.Source)" -ForegroundColor Green
    $version = gh --version
    Write-Host "   版本: $version"
} else {
    Write-Host "⚠️  gh CLI 未安装，正在下载..." -ForegroundColor Yellow
    $downloadUrl = "https://github.com/cli/cli/releases/download/v2.67.0/gh_2.67.0_windows_amd64.msi"
    $installerPath = "$env:TEMP\gh.msi"

    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "   下载完成，正在安装..." -ForegroundColor Yellow
        Start-Process msiexec.exe -Wait -ArgumentList "/i `"$installerPath`" /quiet"
        Write-Host "✅ 安装完成" -ForegroundColor Green

        # 刷新 PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } catch {
        Write-Host "❌ 下载失败: $_" -ForegroundColor Red
        Write-Host "   请手动访问 https://github.com/cli/cli/releases/latest 下载安装" -ForegroundColor Yellow
        exit 1
    }
}

# 配置 GitHub Token
if ($GithubToken) {
    Write-Host ""
    Write-Host "配置 GitHub Token..." -ForegroundColor Yellow
    $env:GH_TOKEN = $GithubToken

    try {
        gh auth status | Out-Null
        if ($LASTEXITCODE -ne 0) {
            # 通过环境变量设置 token
            [System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $GithubToken, "User")
            Write-Host "✅ GITHUB_TOKEN 已设置到用户环境变量" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  请手动运行 gh auth login 完成认证" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "未提供 GitHub Token" -ForegroundColor Yellow
    Write-Host "请通过以下方式之一完成认证:" -ForegroundColor Yellow
    Write-Host "  1. 运行 gh auth login (交互式)" -ForegroundColor Yellow
    Write-Host "  2. 运行 .\setup-gh-cli.ps1 -GithubToken your_token_here" -ForegroundColor Yellow
    Write-Host "  3. 设置环境变量 GITHUB_TOKEN" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "完成!" -ForegroundColor Cyan
Write-Host "安装后请确保 gh 在 PATH 中，然后 Claude Code 的 GitHub MCP 即可自动连接。" -ForegroundColor Cyan
