# start.ps1 - Auto-detect WSL IP, update .env, and start the backend
# Run this script instead of manually starting run.py

Write-Host "🔍 Detecting WSL IP address..." -ForegroundColor Cyan

# Get the WSL IP address (first IPv4 address)
$wslIp = (wsl -- bash -c "hostname -I").Trim().Split(' ')[0]

if (-not $wslIp) {
    Write-Host "❌ Could not detect WSL IP. Is WSL running?" -ForegroundColor Red
    exit 1
}

Write-Host "✅ WSL IP: $wslIp" -ForegroundColor Green

# Update the .env file
$envPath = "$PSScriptRoot\backend\.env"
$envContent = Get-Content $envPath -Raw
$envContent = $envContent -replace 'OLLAMA_BASE_URL=http://[^\r\n]+', "OLLAMA_BASE_URL=http://${wslIp}:11434"
Set-Content $envPath $envContent -NoNewline
Write-Host "✅ Updated .env: OLLAMA_BASE_URL=http://${wslIp}:11434" -ForegroundColor Green

# Ensure firewall rule exists for WSL Ollama port
$rule = Get-NetFirewallRule -DisplayName "WSL Ollama" -ErrorAction SilentlyContinue
if (-not $rule) {
    Write-Host "🔒 Adding firewall rule for Ollama port 11434..." -ForegroundColor Yellow
    New-NetFirewallRule -DisplayName "WSL Ollama" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434 | Out-Null
    Write-Host "✅ Firewall rule added" -ForegroundColor Green
}

# Start the backend
Write-Host "🚀 Starting backend..." -ForegroundColor Cyan
& "C:/Users/SeanTeng/anaconda3/envs/aniChatbot_final/python.exe" "$PSScriptRoot\backend\run.py"
