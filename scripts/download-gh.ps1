param(
    [string]$Destination = "$env:TEMP\gh.zip"
)

Write-Host "=== 下载 GitHub CLI ===" -ForegroundColor Cyan

try {
    $client = New-Object System.Net.WebClient

    # 获取最新版本信息
    Write-Host "获取版本信息..." -ForegroundColor Yellow
    $release = Invoke-RestMethod -Uri 'https://api.github.com/repos/cli/cli/releases/latest' -Headers @{'User-Agent'='powershell'}
    $asset = $release.assets | Where-Object { $_.name -like '*windows_amd64.zip*' }
    Write-Host "找到: $($asset.name) ($([math]::Round($asset.size / 1MB, 2)) MB)"

    # 下载文件
    Write-Host "下载中..." -ForegroundColor Yellow
    $client.DownloadFile($asset.browser_download_url, $Destination)

    $size = (Get-Item $Destination).Length
    Write-Host "下载完成: $([math]::Round($size / 1MB, 2)) MB" -ForegroundColor Green

    # 解压到当前目录
    Write-Host "解压中..." -ForegroundColor Yellow
    Expand-Archive -Path $Destination -DestinationPath "$env:TEMP\gh-cli" -Force

    # 复制到 PATH 目录
    $ghExe = Get-ChildItem -Path "$env:TEMP\gh-cli" -Filter "gh.exe" -Recurse | Select-Object -First 1
    if ($ghExe) {
        $installDir = "$env:USERPROFILE\bin"
        if (-not (Test-Path $installDir)) { New-Item -ItemType Directory -Path $installDir -Force | Out-Null }
        Copy-Item $ghExe.FullName "$installDir\gh.exe" -Force
        Write-Host "已安装到: $installDir\gh.exe" -ForegroundColor Green

        # 添加到 PATH
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($currentPath -notlike "*$installDir*") {
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir", "User")
            Write-Host "已将 $installDir 添加到用户 PATH" -ForegroundColor Green
        }
        Write-Host "安装完成! 请重启终端或执行: `$env:Path += ';$installDir'" -ForegroundColor Green
    } else {
        Write-Host "在解压文件中未找到 gh.exe" -ForegroundColor Red
    }

} catch {
    Write-Host "错误: $_" -ForegroundColor Red
    exit 1
}
