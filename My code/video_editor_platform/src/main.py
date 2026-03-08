"""
FastAPI application entry point for GenAI Video Editor
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
import logging
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_editor_platform.config.base import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
settings = Settings()

# Create FastAPI app
app = FastAPI(
    title="GenAI Video Editor API",
    description="Transform raw videos and descriptions into Instagram-ready content",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# global exception handler to ensure JSON responses on errors
from fastapi.responses import JSONResponse
from fastapi.requests import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and log them, return JSON.

    FastAPI by default returns an HTML page for 500 errors which the
    browser UI was trying to parse as JSON.  A generic JSON response
    prevents the `Unexpected token 'I'` parse errors on the client.
    """
    logger.exception("Unhandled error during request %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "GenAI Video Editor API",
        "version": "0.1.0",
        "docs": "/api/docs",
    }


# Import and include API router
from .api.routes import router as api_router
app.include_router(api_router, prefix="/api")

# Serve the simple UI from src/static at /ui
from fastapi.staticfiles import StaticFiles
from pathlib import Path
static_dir = Path(__file__).parent / "static"
app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")

# also expose uploaded files (including generated video) via /uploads
upload_dir = Path(settings.UPLOAD_TEMP_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")


from .services.emo_g_image_agent import EmoGImageAgent

if __name__ == "__main__":
    # Define the prompt for the Generative AI
    prompt = "A red racing suit on display with a bold '20% SALE' text and emojis 🎉 and 🎁 placed prominently."
    output_path = "video_editor_platform/edited_images/generated_promo_image.jpg"

    # Define the input image path
    input_image_path = "/Users/chy/Desktop/My code/video_editor_platform/temp_images/racing uite.jpg"

    # Generate the image using Generative AI
    EmoGImageAgent.generate_image_with_genai(prompt, input_image_path, output_path)

    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
