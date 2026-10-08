# Script dừng các tiến trình của dự án VIỆT FIT
Write-Host "=== Đang dừng các dịch vụ VIỆT FIT ===" -ForegroundColor Cyan

# Dừng python uvicorn port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Dừng java backend port 8080
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Dừng vite frontend port 5173
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host "Đã dừng các dịch vụ trên các cổng 8000, 8080, 5173." -ForegroundColor Green
