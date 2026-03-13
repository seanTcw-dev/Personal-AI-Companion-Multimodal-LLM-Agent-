# Simple HTTP Server Starter for VRM Inspector
# This script starts a local web server to avoid CORS issues

Write-Host "🚀 Starting local web server..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
}

if ($pythonCmd) {
    Write-Host "✅ Using Python HTTP server" -ForegroundColor Green
    Write-Host "📂 Server running at: http://localhost:8000" -ForegroundColor Yellow
    Write-Host "🌐 Open this URL in your browser: http://localhost:8000/index.html" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    & $pythonCmd -m http.server 8000
} else {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Or use an alternative method:" -ForegroundColor Yellow
    Write-Host "  1. Install Node.js and run: npx http-server -p 8000" -ForegroundColor Cyan
    Write-Host "  2. Use VS Code Live Server extension" -ForegroundColor Cyan
    Write-Host ""
    pause
}
