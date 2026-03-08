# setup.ps1 — Windows setup script for GenAI Carousel Video Generator
# Run once after cloning:  .\setup.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GenAI Carousel Video Generator Setup  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- 1. Check Python ---
try {
    $pyVersion = python --version 2>&1
    Write-Host "[OK] $pyVersion found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}

# --- 2. Create .venv ---
if (Test-Path ".venv") {
    Write-Host "[SKIP] .venv already exists" -ForegroundColor Yellow
} else {
    Write-Host "[...] Creating virtual environment (.venv)..."
    python -m venv .venv
    Write-Host "[OK] .venv created" -ForegroundColor Green
}

# --- 3. Install dependencies ---
Write-Host "[...] Installing dependencies from requirements.txt..."
.\.venv\Scripts\pip install --upgrade pip --quiet
.\.venv\Scripts\pip install -r requirements.txt
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# --- 4. Config check ---
if (-not (Test-Path "config\config.json")) {
    Write-Host ""
    Write-Host "[ACTION REQUIRED] Add your HuggingFace API token to config\config.json" -ForegroundColor Yellow
    Write-Host "  Get a free token at: https://huggingface.co/settings/tokens" -ForegroundColor Yellow
    Write-Host "  Format: { ""hf_api_token"": ""hf_your_token_here"" }" -ForegroundColor Yellow
} else {
    Write-Host "[OK] config\config.json found" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup complete! Activate the venv:    " -ForegroundColor Cyan
Write-Host "   .\.venv\Scripts\Activate.ps1        " -ForegroundColor White
Write-Host ""
Write-Host " Then run:                             " -ForegroundColor Cyan
Write-Host "   python generate_carousel_with_banners.py `"img1.jpg`" `"img2.jpg`" \" -ForegroundColor White
Write-Host "     --description `"20% off on gear`"  " -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
