#!/bin/bash
# GitHub CLI 包装器 — 如 gh 未安装，给出清晰指引

if command -v gh &> /dev/null; then
  exec gh "$@"
else
  echo "[gh-wrapper] ❌ gh CLI 未安装。"
  echo "[gh-wrapper] 请运行以下命令安装:"
  echo ""
  echo "  Windows (PowerShell 管理员):"
  echo "    winget install --id GitHub.cli"
  echo ""
  echo "  或运行配置脚本:"
  echo "    powershell -File scripts/setup-gh-cli.ps1"
  echo ""
  echo "  手动下载: https://github.com/cli/cli/releases/latest"
  exit 1
fi
