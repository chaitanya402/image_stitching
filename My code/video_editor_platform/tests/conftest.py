"""
Pytest configuration and shared fixtures for all tests
"""

import pytest
import os
import sys
from pathlib import Path

# Add both src and root to path for proper imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))


@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        "DEBUG": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
        "MAX_FILE_SIZE_MB": 500,
        "USE_LOCAL_LLM": True,
        "USE_LOCAL_TTS": True,
        "USE_GPU": False,
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for test files"""
    return tmp_path


@pytest.fixture
def sample_video_path(temp_dir):
    """Create a dummy video file for testing"""
    video_file = temp_dir / "test_video.mp4"
    # Create a minimal MP4-like file (just for testing upload validation)
    video_file.write_bytes(b"dummy_video_content")
    return str(video_file)


@pytest.fixture
def sample_description():
    """Sample product description"""
    return "Beautiful handmade jewelry with gold accents, perfect for summer weddings"


@pytest.fixture
def api_client():
    """FastAPI test client"""
    try:
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)
    except Exception as e:
        pytest.skip(f"Could not initialize API client: {e}")


@pytest.fixture
def mock_video_metadata():
    """Mock video metadata"""
    return {
        "duration": 30.5,
        "fps": 24,
        "resolution": (1920, 1080),
        "codec": "h264",
        "bitrate": "5000k",
    }


@pytest.fixture
def mock_caption():
    """Mock AI-generated caption"""
    return "Check out this gorgeous handmade jewelry collection! Perfect for your special day. 💎✨"


@pytest.fixture
def mock_audio_file(temp_dir):
    """Create a dummy audio file for testing"""
    audio_file = temp_dir / "test_audio.wav"
    audio_file.write_bytes(b"dummy_audio_content")
    return str(audio_file)
