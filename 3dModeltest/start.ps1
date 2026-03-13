# Quick Server Starter (Uses npx - no installation needed!)

Write-Host "🚀 Starting local web server with npx..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Server will run at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "🌐 Opening browser automatically..." -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start server and open browser
Start-Process "http://localhost:8000/index.html"
npx http-server -p 8000 -o
