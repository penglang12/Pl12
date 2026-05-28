param(
    [string]$FilePath = "",
    [string]$Content = "",
    [string]$Mode = "scan"
)

$foundSecrets = [System.Collections.ArrayList]@()

$patterns = @(
    # HIGH severity
    @{ Pattern = '(?-i)(-----BEGIN\s*(?:RSA|EC|DSA|OPENSSH|PGP|PRIVATE)\s*KEY-----)';  Severity = 'High'; Name = 'Private Key' }
    @{ Pattern = '(?-i)(sk-[a-zA-Z0-9_-]{20,})';                                        Severity = 'High'; Name = 'API Key sk-' }
    @{ Pattern = '(?-i)(pk-[a-zA-Z0-9_-]{20,})';                                        Severity = 'High'; Name = 'API Key pk-' }
    @{ Pattern = '(?-i)(AKIA[0-9A-Z]{16})';                                              Severity = 'High'; Name = 'AWS Access Key' }
    @{ Pattern = '(?-i)(ghp_[a-zA-Z0-9]{36,})';                                          Severity = 'High'; Name = 'GitHub Token' }
    @{ Pattern = '(?-i)(gho_[a-zA-Z0-9]{36,})';                                          Severity = 'High'; Name = 'GitHub OAuth' }
    @{ Pattern = '(?-i)(ghu_[a-zA-Z0-9]{36,})';                                          Severity = 'High'; Name = 'GitHub User Token' }
    @{ Pattern = '(?-i)(xox[baprs]-[0-9a-zA-Z-]{10,})';                                  Severity = 'High'; Name = 'Slack Token' }

    # MEDIUM severity
    @{ Pattern = '(?-i)(AIza[0-9A-Za-z_-]{35})';                                          Severity = 'Medium'; Name = 'Google API Key' }
    @{ Pattern = '(?-i)(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})';  Severity = 'Medium'; Name = 'JWT Token' }
    @{ Pattern = '(?i)(password\s*[=:]\s*\S{3,})';                                          Severity = 'Medium'; Name = 'Plain Password' }
    @{ Pattern = '(?i)(secret\s*[=:]\s*\S{8,})';                                           Severity = 'Medium'; Name = 'Hardcoded Secret' }
    @{ Pattern = '(?i)(api[_-]?key\s*[=:]\s*\S{8,})';                                      Severity = 'Medium'; Name = 'Hardcoded API Key' }
    @{ Pattern = '(?i)(token\s*[=:]\s*\S{8,})';                                            Severity = 'Medium'; Name = 'Hardcoded Token' }
    @{ Pattern = '(?-i)(mongodb(?:\+srv)?://[a-zA-Z0-9_]+:[^@]+@)';                       Severity = 'Medium'; Name = 'MongoDB Conn String' }
    @{ Pattern = '(?-i)(mysql://[a-zA-Z0-9_]+:[^@]+@)';                                    Severity = 'Medium'; Name = 'MySQL Conn String' }
    @{ Pattern = '(?-i)(postgres(?:\+ssl)?://[a-zA-Z0-9_]+:[^@]+@)';                       Severity = 'Medium'; Name = 'PostgreSQL Conn String' }

    # LOW severity
    @{ Pattern = '(?i)(auth_token\s*[=:]\s*\S{10,})';                                      Severity = 'Low'; Name = 'Auth Token Config' }
    @{ Pattern = '(?i)(credential\s*[=:]\s*\S{10,})';                                     Severity = 'Low'; Name = 'Credential Config' }
    @{ Pattern = '(?i)(access_key\s*[=:]\s*\S{10,})';                                     Severity = 'Low'; Name = 'Access Key Config' }
)

$skipPatterns = @(
    'node_modules[\\/]', '\.git[\\/]', '\.venv[\\/]', '__pycache__[\\/]',
    '\.next[\\/]', 'dist[\\/]', 'build[\\/]', '\.vscode[\\/]', '\.workbuddy[\\/]',
    'package-lock\.json', 'yarn\.lock', '\.log$',
    '\.exe$', '\.dll$', '\.bin$', '\.jpg$', '\.png$', '\.svg$', '\.ico$', '\.webm$',
    '\.woff2?$', '\.ttf$', '\.eot$', '\.mp4$', '\.mp3$', '\.wav$',
    '\.env\.template$', '\.env\.example$', '\.env\.sample$'
)

function Should-Skip($path) {
    foreach ($sp in $skipPatterns) {
        if ($path -match $sp) { return $true }
    }
    return $false
}

function Scan-Text {
    param([string]$text, [string]$source, [int]$lineOffset = 0)

    $lines = $text -split "`n"
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $lineNum = $i + 1 + $lineOffset
        foreach ($p in $patterns) {
            if ($line -match $p.Pattern) {
                $matched = $Matches[0]
                if ($matched.Length -gt 60) {
                    $matched = $matched.Substring(0, 40) + "..."
                }
                [void]$foundSecrets.Add([PSCustomObject]@{
                    Severity    = $p.Severity
                    Name        = $p.Name
                    Match       = $matched
                    Line        = $lineNum
                    Source      = $source
                    LineContent = $line.Trim().Substring(0, [Math]::Min(80, $line.Trim().Length))
                })
            }
        }
    }
}

if ($Content) {
    Scan-Text -text $Content -source "(inline)"
} elseif ($FilePath -and (Test-Path $FilePath) -and -not (Should-Skip $FilePath)) {
    $content = Get-Content -Path $FilePath -Raw -ErrorAction SilentlyContinue
    if ($content) { Scan-Text -text $content -source $FilePath }
} else {
    $scanRoot = "C:\Users\PC\WorkBuddy\Claw"
    Write-Host "[secret-scanner] Scanning: $scanRoot"

    $files = Get-ChildItem -Path $scanRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { -not (Should-Skip $_.FullName) -and $_.Length -lt 500KB } |
        Where-Object { $_.Extension -in '.py','.js','.ts','.jsx','.tsx','.json','.yaml','.yml','.env','.ini','.cfg','.conf','.sh','.ps1','.md','.txt','.xml','.html','.css','.toml','.rb','.go','.rs','.java','.cs','.php','.swift','.kt' }

    $total = 0
    foreach ($f in $files) {
        $content = Get-Content -Path $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) {
            $total++
            Scan-Text -text $content -source $f.FullName
        }
    }
    Write-Host "[secret-scanner] Scanned $total files, found $($foundSecrets.Count) potential secrets"
}

# OUTPUT
if ($foundSecrets.Count -gt 0) {
    Write-Host "`n============================================"
    Write-Host "  SECURITY SCANNER REPORT"
    Write-Host "============================================"

    $grouped = $foundSecrets | Group-Object Severity
    foreach ($g in $grouped) {
        Write-Host "`n[$($g.Name)] $($g.Count) findings:"
        Write-Host "----------------------------------------"
        foreach ($s in $g.Group) {
            Write-Host "  [$($s.Name)] Line $($s.Line)"
            Write-Host "    Match: $($s.Match)"
            Write-Host "    File: $($s.Source)"
        }
    }

    $highCount = ($foundSecrets | Where-Object { $_.Severity -eq 'High' }).Count
    $mediumCount = ($foundSecrets | Where-Object { $_.Severity -eq 'Medium' }).Count

    Write-Host "`n============================================"
    Write-Host "  Total: $($foundSecrets.Count) | High: $highCount | Medium: $mediumCount | Low: $($foundSecrets.Count - $highCount - $mediumCount)"
    Write-Host "============================================"

    if ($Mode -eq 'block' -and ($highCount -gt 0 -or $mediumCount -gt 0)) {
        Write-Host "[SECURITY] BLOCKED: $highCount high + $mediumCount medium severity secrets detected"
        exit 1
    }

    return $foundSecrets.Count
}

return 0
