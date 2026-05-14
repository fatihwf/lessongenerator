# Bloom Lesson Generator - Local Starter Script (Corrected)

Write-Host "--- Bloom Lesson Generator Başlatılıyor ---" -ForegroundColor Cyan

# 1. Backend'i Başlat
Write-Host "[1/2] Backend (FastAPI) başlatılıyor (Port 8080)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "pip install -r requirements.txt; cd services/bloom-api; python -m uvicorn main:app --reload --port 8080"

# 2. Frontend'i Başlat
Write-Host "[2/2] Frontend (Vite) başlatılıyor (Port 3000)..." -ForegroundColor Green
# pnpm kurulumu ve başlatma
Start-Process powershell -ArgumentList "-NoExit", "-Command", "pnpm install; pnpm --filter @workspace/bloom-frontend dev --port 3000"

Write-Host "--- Servisler başlatıldı ---" -ForegroundColor Yellow
Write-Host "Arayüz: http://localhost:3000"
Write-Host "API: http://localhost:8080"
