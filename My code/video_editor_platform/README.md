# GenAI Video Editor

Transform raw user videos and product descriptions into engaging, Instagram-ready content using AI/GenAI models.  
Supports promotional templates: place user images onto a branded background automatically (see `sample templates/`).   

*Images are normalized to a vertical 9:16 aspect ratio (TikTok/Instagram) with padding or scaling.*

## Overview

A GenAI-powered platform that:
- Accepts raw user-uploaded videos and product/shop descriptions
- Automatically enhances video quality using ESRGAN
- Generates engaging captions using OpenAI GPT-4 Mini
- Creates voiceover using ElevenLabs text-to-speech
- Selects and mixes background music
- Composes final video optimized for Instagram (9:16 or 1:1)
- Exports in social-media-friendly formats

**Target:** Scale to 1M+ video processing requests/month with <60s processing time per video.

---

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (for containerized setup)
- Accounts for:
  - OpenAI (GPT-4 Mini API)
  - ElevenLabs (Text-to-Speech)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd video_editor_platform
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies** (local development)
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

4. **Run with Docker Compose** (recommended)
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

5. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs
   - Database: postgresql://user:password@localhost:5432/video_editor

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# With coverage report
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_validators.py -v
```

---

## Architecture

![System Architecture](docs/diagrams/system_architecture.png)

### Components
- **API Gateway:** FastAPI with authentication & rate limiting
- **Upload Service:** File handling & validation
- **Template Engine:** Optional promotional backgrounds applied to images/videos (configurable via `TEMPLATES_DIR`)
- **Processing Pipeline:** Async job queue using Celery + Redis
- **Enhancement Module:** Video quality upgrade (ESRGAN)
- **Caption Generator:** AI captions (OpenAI GPT-4 Mini)
- **Audio Module:** Text-to-speech & mixing (ElevenLabs)
- **Compositor:** Video assembly (FFmpeg + moviepy)
- **Storage:** AWS S3 for input/output files

---

## Project Structure

```
video_editor_platform/
├── src/
│   ├── api/              # API routes & endpoints
│   ├── services/         # Business logic
│   ├── processing/       # ML/AI modules
│   ├── models/           # Database models
│   └── utils/            # Shared utilities
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── fixtures/         # Test data
├── docker/               # Container configs
├── config/               # Configuration
├── docs/                 # Documentation
└── requirements.txt      # Dependencies
```

See [FOLDER_STRUCTURE.md](video_editor_platform/FOLDER_STRUCTURE.md) for detailed structure.

---

## Development Roadmap

### Sprint 1: MVP Foundation (Week 1)
- [x] File upload endpoint
- [x] Video metadata extraction
- [x] Video quality enhancement (ESRGAN)
- [x] Aspect ratio conversion to Instagram format
- [x] MP4 export with H.264 codec
- [x] Database & caching setup
- [x] Unit & integration tests

### Sprint 2: GenAI Integration (Week 2)
- [ ] Caption generation (OpenAI GPT-4 Mini)
- [ ] Text-to-speech (ElevenLabs)
- [ ] Audio synchronization
- [ ] API fallback mechanisms
- [ ] Integration tests & API mocks

### Sprint 3: Composition & Polish (Week 3)
- [ ] Background music selection & mixing
- [ ] Video composition (FFmpeg)
- [ ] Visual effects & transitions
- [ ] Progress tracking & webhooks
- [ ] E2E testing & manual QA

### Sprint 4: Scale & Deploy (Week 4)
- [ ] Performance optimization
- [ ] Load testing (1M req/month)
- [ ] Security hardening
- [ ] CI/CD pipeline
- [ ] Production deployment

See [SPRINT_PLAN_WITH_TESTING.md](video_editor_platform/SPRINT_PLAN_WITH_TESTING.md) for detailed sprint plan with testing.

---

## Documentation

- **[Architecture Design](video_editor_platform/ARCHITECTURE.md)** - System design, components, data flow
- **[Folder Structure](video_editor_platform/FOLDER_STRUCTURE.md)** - Project organization
- **[Sprint Plan](video_editor_platform/SPRINT_PLAN_WITH_TESTING.md)** - Development timeline with testing
- **[Project Overview](video_editor_platform/PROJECT_OVERVIEW.md)** - High-level overview & roadmap
- **[API Documentation](docs/API.md)** - API endpoints (to be created in Sprint 1)
- **[Setup Guide](docs/SETUP.md)** - Detailed setup instructions (to be created in Sprint 1)
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment (to be created in Sprint 4)

---

## Technology Stack

**Backend:** FastAPI, Python 3.9+
**Async:** Celery + Redis
**Database:** PostgreSQL + SQLAlchemy
**Video Processing:** FFmpeg, OpenCV, moviepy
**AI/ML:** OpenAI GPT-4 Mini, ElevenLabs TTS, ESRGAN
**Infrastructure:** Docker, Kubernetes, AWS (S3, RDS, EC2)
**Testing:** pytest, pytest-asyncio, pytest-cov
**Monitoring:** Prometheus, Grafana, ELK Stack

---

## Model Selection Strategy

| Component | Model | Cost/Month (1M) | Rationale |
|-----------|-------|---|---|
| Video Enhancement | ESRGAN | GPU time (~$0) | Open-source, best quality |
| Captions | OpenAI GPT-4 Mini | $30 | Low-cost, high-quality |
| Text-to-Speech | ElevenLabs | $99 | Natural audio, multilingual |
| Background Music | Pexels API | Free | Royalty-free, free |

**Total Infrastructure Cost:** ~$2,000-2,500/month for 1M requests

---

## API Examples

### Upload Video & Generate Content

```bash
curl -X POST "http://localhost:8000/api/v1/videos/upload" \
  -H "Authorization: Bearer {token}" \
  -F "video=@myvideo.mp4" \
  -F "description=Beautiful handmade jewelry with gold accents, perfect for summer!"

# Response
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "video_id": "video_123",
  "created_at": "2024-03-01T10:00:00Z",
  "estimated_completion": "2024-03-01T10:01:00Z"
}
```

### Check Processing Status

```bash
curl -X GET "http://localhost:8000/api/v1/videos/550e8400-e29b-41d4-a716-446655440000/status" \
  -H "Authorization: Bearer {token}"

# Response
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "output_url": "https://s3.amazonaws.com/video-editor-outputs/video_123.mp4",
  "processing_time_seconds": 45,
  "metadata": {
    "duration": 30,
    "resolution": "1080x1920",
    "captions": "Beautiful handmade jewelry with premium gold....",
    "music": "Cheerful Background Vol.3"
  }
}
```

---

## Configuration

Create a `.env` file (see `.env.example`):

```env
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/video_editor

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=video-editor-uploads

# API Keys
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...

# Processing
USE_GPU=true
VIDEO_ENHANCEMENT_ENABLED=true
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Please ensure:**
- All tests pass (`pytest`)
- Code coverage ≥ 85%
- Code is formatted with black (`black src/`)
- No linting issues (`flake8 src/`)

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific category
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end tests only

# Run with verbose output
pytest -v

# Run specific file
pytest tests/unit/test_validators.py
```

---

## Performance & Scalability

### Current Targets
- **Processing Time:** <60 seconds per video
- **Throughput:** 1M requests/month
- **API Latency:** <5s for health check
- **Uptime:** 99.5%

### Scaling Architecture
1. **MVP:** Single server + managed DB
2. **Growth:** Multiple API servers + dedicated GPU workers
3. **Scale:** Kubernetes cluster with auto-scaling, regional GPUs

See [ARCHITECTURE.md](video_editor_platform/ARCHITECTURE.md) for scalability details.

---

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'src'`
```bash
# Solution: Add current directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

**Issue:** GPU out of memory during processing
```bash
# Solution: Reduce video resolution or batch size in config
# Or: Use CPU-only mode (slower but works)
USE_GPU=false
```

**Issue:** Database connection failed
```bash
# Solution: Ensure PostgreSQL is running
docker-compose -f docker/docker-compose.yml up postgres
```

---

## License

[MIT License](LICENSE)

---

## Support

For issues, questions, or suggestions:
- **GitHub Issues:** https://github.com/your/repo/issues
- **Email:** support@videoeditai.com
- **Discord:** [Join our community](https://discord.gg/videoeditai)

---

**Made with ❤️ by the GenAI Video Editor Team**
