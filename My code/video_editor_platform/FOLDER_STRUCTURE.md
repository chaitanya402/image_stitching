# Project Folder Structure

```
video_editor_platform/
│
├── src/                           # Source code
│   ├── static/                    # Static front-end resources (HTML/CSS/JS)
│   ├── api/                       # API endpoints (FastAPI routes)
│   │   ├── __init__.py
│   │   ├── routes.py              # URL routing
│   │   ├── schemas.py             # Request/response models
│   │   └── middleware.py          # Auth, logging, error handling
│   │
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   ├── upload_service.py      # File upload & validation
│   │   ├── processing_service.py  # Orchestrate processing pipeline
│   │   ├── export_service.py      # Video export & format conversion
│   │   └── cache_service.py       # Redis caching
│   │
│   ├── processing/                # Core processing modules
│   │   ├── __init__.py
│   │   ├── enhancement.py         # Video quality enhancement (ESRGAN)
│   │   ├── caption_generator.py   # AI caption generation (GPT-4)
│   │   ├── audio_mixer.py         # Audio synthesis & mixing
│   │   ├── bgm_selector.py        # Background music selection
│   │   └── composer.py            # Video composition (FFmpeg)
│   │
│   ├── models/                    # Data models & schemas
│   │   ├── __init__.py
│   │   ├── video.py               # Video metadata model
│   │   ├── job.py                 # Processing job model
│   │   └── user.py                # User model
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py              # Logging setup
│   │   ├── config.py              # Configuration management
│   │   ├── validators.py          # Input validation
│   │   ├── constants.py           # Constants & enums
│   │   ├── aws_s3.py              # S3 file operations
│   │   └── redis_client.py        # Redis operations
│   │
│   └── main.py                    # FastAPI app entry point
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures & config
│   ├── test_config.py             # Test configuration
│   │
│   ├── unit/                      # Unit tests (isolated)
│   │   ├── test_enhancement.py
│   │   ├── test_caption_generator.py
│   │   ├── test_audio_mixer.py
│   │   ├── test_composer.py
│   │   ├── test_validators.py
│   │   └── test_services.py
│   │
│   ├── integration/               # Integration tests (multiple components)
│   │   ├── test_processing_pipeline.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_database_operations.py
│   │   └── test_redis_caching.py
│   │
│   ├── e2e/                       # End-to-end tests (full workflow)
│   │   ├── test_upload_to_export.py
│   │   ├── test_api_workflow.py
│   │   └── test_error_handling.py
│   │
│   └── fixtures/                  # Test data
│       ├── sample_videos/         # Sample test videos
│       ├── sample_images/         # Sample test images
│       └── mock_responses.py      # Mock API responses
│
├── docker/                        # Docker configuration
│   ├── Dockerfile                 # Production image
│   ├── Dockerfile.test            # Testing image
│   ├── docker-compose.yml         # Local dev setup (API + Redis + DB)
│   └── docker-compose.prod.yml    # Production setup (K8s)
│
├── config/                        # Configuration files
│   ├── __init__.py
│   ├── base.py                    # Base config
│   ├── development.py             # Dev settings
│   ├── production.py              # Prod settings
│   ├── testing.py                 # Test settings
│   └── .env.example               # Environment variables template
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md            # Architecture design doc
│   ├── API.md                     # API documentation
│   ├── SETUP.md                   # Setup instructions
│   ├── TESTING.md                 # Testing guide
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── diagrams/                  # Architecture diagrams
│   │   ├── system_architecture.png
│   │   ├── data_flow.png
│   │   └── processing_pipeline.png
│   └── examples/                  # Usage examples
│       └── sample_requests.py
│
├── .github/                       # GitHub config
│   └── workflows/                 # CI/CD pipelines
│       ├── tests.yml              # Run tests on push
│       ├── deploy.yml             # Deploy on release
│       └── lint.yml               # Code quality checks
│
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Dev dependencies
├── requirements-test.txt          # Test dependencies
├── pytest.ini                     # Pytest configuration
├── .gitignore                     # Git ignore rules
├── README.md                      # Project overview
├── CHANGELOG.md                   # Version history
└── Makefile                       # Useful commands

```

## Folder Purpose Summary

| Folder | Purpose |
|--------|---------|
| `src/api/` | FastAPI routes, request validation, error handling |
| `src/services/` | Business logic, orchestration, external API calls |
| `src/processing/` | ML/AI processing, video enhancement, composition |
| `src/models/` | Database models, data schemas, type hints |
| `src/utils/` | Shared utilities, config, logging, AWS integration |
| `tests/unit/` | Test individual functions/classes in isolation |
| `tests/integration/` | Test multiple components working together |
| `tests/e2e/` | Test complete user workflows end-to-end |
| `tests/fixtures/` | Sample data, mock responses for testing |
| `docker/` | Container definitions for dev/test/prod |
| `config/` | Environment-specific settings and secrets |
| `docs/` | Technical documentation, diagrams, examples |

## Key Design Principles

1. **Separation of Concerns:** Each module has a single responsibility
2. **Testability:** Easy to mock, isolate, and test each component
3. **Scalability:** Async processing, caching, database indexing ready
4. **Maintainability:** Clear structure, consistent naming, comprehensive docs
5. **Security:** Config secrets, input validation, error handling

## Running Tests

```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run integration tests
make test-integration

# Run e2e tests
make test-e2e

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/unit/test_caption_generator.py -v

# Run tests matching pattern
pytest -k "caption" -v
```
