#!/usr/bin/env bash
# setup.sh — Linux/macOS setup script for GenAI Carousel Video Generator
# Run once after cloning:  bash setup.sh

set -e

echo ""
echo "========================================"
echo " GenAI Carousel Video Generator Setup  "
echo "========================================"
echo ""

# --- 1. Check Python ---
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found. Install Python 3.10+ first."
    exit 1
fi
echo "[OK] $(python3 --version) found"

# --- 2. Create .venv ---
if [ -d ".venv" ]; then
    echo "[SKIP] .venv already exists"
else
    echo "[...] Creating virtual environment (.venv)..."
    python3 -m venv .venv
    echo "[OK] .venv created"
fi

# --- 3. Install dependencies ---
echo "[...] Installing dependencies from requirements.txt..."
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -r requirements.txt
echo "[OK] Dependencies installed"

# --- 4. Config check ---
if [ ! -f "config/config.json" ]; then
    echo ""
    echo "[ACTION REQUIRED] Add your HuggingFace API token to config/config.json"
    echo "  Get a free token at: https://huggingface.co/settings/tokens"
    echo '  Format: { "hf_api_token": "hf_your_token_here" }'
else
    echo "[OK] config/config.json found"
fi

echo ""
echo "========================================"
echo " Setup complete! Activate the venv:    "
echo "   source .venv/bin/activate           "
echo ""
echo " Then run:                             "
echo '   python generate_carousel_with_banners.py "img1.jpg" "img2.jpg" \'
echo '     --description "20% off on gear"   '
echo "========================================"
