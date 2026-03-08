# Local Development Setup Guide

## Quick Start (Local Testing - No Docker)

This guide shows how to set up the GenAI Video Editor for **local testing without Docker**, using free open-source models.

### Prerequisites

- **Python 3.9+** (tested on Python 3.9, 3.10, 3.11)
- **FFmpeg** (for video processing)
- **Git**

### Step 1: Setup Python Environment

```bash
# Clone the repository
cd /Users/chy/Desktop/My\ code/video_editor_platform

# Create virtual environment
python3.9 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # macOS/Linux
# OR on Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install core dependencies (without paid APIs)
pip install -r requirements.txt

# Additional dependencies for local LLM
pip install ollama  # For running LLaMA-2 locally
```

### Step 3: Configure Environment

```bash
# Copy local config
cp .env.local .env

# Or create your own .env file
cat > .env << EOF
DEBUG=true
DATABASE_URL=sqlite:///./video_editor_local.db
USE_LOCAL_LLM=true
USE_LOCAL_TTS=true
USE_GPU=false
UPLOAD_TEMP_DIR=./tmp/video_uploads
EOF
```

### Step 4: Create Required Directories

```bash
# Create upload and temp directories
mkdir -p uploads tmp/video_uploads tests/fixtures/sample_videos

# Create database directory
mkdir -p data
```

### Step 5: Test the Setup

```bash
# Check FastAPI is working
python -c "from fastapi import FastAPI; print('FastAPI OK')"

# Check video processing libs
python -c "import cv2, numpy; print('OpenCV OK')"

# Check audio libs  
python -c "import librosa, pydub; print('Audio libs OK')"

# Run a quick health check
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/health

---

## Running Tests Locally

### Install Testing Dependencies

```bash
# Install test tools
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### Run All Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests  
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_validators.py -v

# Run with markers
pytest -m unit           # Only unit tests
pytest -m integration    # Only integration tests
pytest -m "not slow"     # Skip slow tests
```

### Generate Test Report

```bash
# HTML coverage report (opens in browser)
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal report
pytest tests/ --cov=src -v
```

---

## Local Without APIs (Free Models)

### Option 1: Use Local LLaMA-2 (Recommended)

Install Ollama:
```bash
# macOS
brew install ollama

# Or download from https://ollama.ai

# Start Ollama in another terminal
ollama serve

# In another terminal, pull the model
ollama pull llama2
```

Update `.env`:
```env
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Option 2: Use OpenAI (Paid, when ready)

```bash
# Update .env with your API key
USE_LOCAL_LLM=false
OPENAI_API_KEY=sk-your_key_here

# Install OpenAI SDK
pip install openai
```

### Option 3: Use Local TTS (pyttsx3 - Already Installed)

No setup needed! pyttsx3 is pure Python and works offline.

```bash
# Test it
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Hello'); engine.runAndWait()"
```

To use ElevenLabs instead:
```bash
# Update .env
USE_LOCAL_TTS=false
ELEVENLABS_API_KEY=your_key_here
```

---

## Project Structure for Local Testing

```
video_editor_platform/
├── .env.local              # Local config (copy to .env)
├── .env                    # Your config (git ignored)
├── requirements.txt        # Dependencies
│
├── src/
│   ├── main.py            # FastAPI app
│   ├── api/               # API routes
│   ├── services/          # Business logic
│   ├── processing/        # Video processing
│   ├── models/            # Data models
│   └── utils/             # Utilities
│
├── tests/
│   ├── conftest.py        # Pytest configuration
│   ├── unit/              # Unit tests
│   ├── integration/        # Integration tests
│   ├── e2e/               # End-to-end tests
│   └── fixtures/          # Test data
│       ├── sample_videos/
│       └── mock_responses.py
│
├── data/                  # Local database
├── tmp/                   # Temporary files
├── uploads/               # Uploaded files
├── venv/                  # Python virtual environment
└── README.md
```

---

## Running the API Locally

### Start the API

```bash
# In your activated venv
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Or in development mode:
```bash
python src/main.py
```

API available at: http://localhost:8000
Docs: http://localhost:8000/api/docs
Redoc: http://localhost:8000/api/redoc

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Upload a video (create a test video first)
curl -X POST "http://localhost:8000/api/v1/videos/upload" \
  -F "video=@test_video.mp4" \
  -F "description=Test video with product description"

# Check job status
curl "http://localhost:8000/api/v1/videos/job_id/status"
```

---

## Troubleshooting

### Issue: "No module named 'src'"
```bash
# Solution: Ensure you're in the right directory
cd /Users/chy/Desktop/My\ code/video_editor_platform

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Database errors with SQLite
```bash
# SQLite database path might be wrong
# Check .env has: DATABASE_URL=sqlite:///./video_editor_local.db

# Reset database
rm video_editor_local.db

# Let the app recreate it
python -m uvicorn src.main:app
```

### Issue: Ollama not connecting
```bash
# Make sure Ollama is running
ollama serve  # Run in another terminal

# Check it's accessible
curl http://localhost:11434/api/tags
```

### Issue: Tests failing with import errors
```bash
# Ensure you're in the right directory with venv activated
cd /Users/chy/Desktop/My\ code/video_editor_platform
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Run again
pytest tests/unit/ -v
```

### Issue: Permission denied errors
```bash
# Fix file permissions
chmod -R 755 tmp/ uploads/ data/
```

---

## Common Commands

```bash
# Activate venv
source venv/bin/activate

# Deactivate venv
deactivate

# Install new package
pip install package_name

# List installed packages
pip list

# Update requirements file
pip freeze > requirements.txt

# Run tests with coverage
pytest --cov=src

# Run app
python -m uvicorn src.main:app --reload

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

---

## Next Steps

1. **Run tests locally** to ensure setup is correct
2. **Create sample test videos** in `tests/fixtures/sample_videos/`
3. **Implement unit tests** for each module
4. **Test API endpoints** using the FastAPI docs
5. **When satisfied**, move to Docker setup

---

**Setup Complete!** You're ready for local development and testing.
