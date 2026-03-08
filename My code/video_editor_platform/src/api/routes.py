from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
from pathlib import Path
import shutil
from config.base import Settings

# image / video imports
import io
import base64
from fastapi.responses import JSONResponse
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
except Exception:
    Image = ImageDraw = ImageFilter = ImageEnhance = ImageFont = None

# imageio for slideshow video generation
try:
    import imageio
except Exception:
    imageio = None

router = APIRouter()
settings = Settings()


def _save_files(files) -> list:
    """Save UploadFile objects to disk and return metadata list."""
    upload_dir = Path(settings.UPLOAD_TEMP_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for f in files:
        filename = Path(f.filename).name
        suffix = filename.split('.')[-1].lower()
        if suffix not in settings.ALLOWED_VIDEO_FORMATS + ["jpg", "jpeg", "png", "gif"]:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")
        dest = upload_dir / filename
        with dest.open("wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved.append({"filename": filename, "path": str(dest), "size": dest.stat().st_size})
    return saved


def _generate_slideshow(saved: list, description: Optional[str]) -> Optional[str]:
    """Try to build a slideshow video or gif from saved image paths.

    Uses DescriptionAgent to parse the text, CreativeAgent to choose
    decorations, and EditAgent to draw those decorations on each frame.
    """
    upload_dir = Path(settings.UPLOAD_TEMP_DIR)
    video_url = None
    mp4_created = False

    # compute decoration list once
    decorations = []
    if description:
        # import using full package path so it works when running as module
        from src.services.description_agent import DescriptionAgent
        from src.services.creative_agent import CreativeAgent
        from src.services.edit_agent import EditAgent

        kw = DescriptionAgent.extract_keywords(description)
        sent = DescriptionAgent.sentiment(description)
        decorations = CreativeAgent.generate_decorations(kw, sent)

    def _prepare_images(paths, max_width=640):
        # load and resize images, then pad them to uniform size
        loaded = []
        for p in paths:
            try:
                im = Image.open(p).convert("RGB")
                if im.width > max_width:
                    ratio = max_width / im.width
                    im = im.resize((max_width, int(im.height * ratio)), Image.LANCZOS)
                if decorations:
                    # apply drawn decorations
                    from src.services.edit_agent import EditAgent
                    im = EditAgent.apply_decorations(im, decorations)
                loaded.append(im)
            except Exception:
                continue
        if not loaded:
            return []
        # determine target dimensions (maximum found among images)
        max_w = max(im.width for im in loaded)
        max_h = max(im.height for im in loaded)
        normalized = []
        for im in loaded:
            if im.width != max_w or im.height != max_h:
                new = Image.new("RGB", (max_w, max_h), (0, 0, 0))
                new.paste(im, (0, 0))
                im = new
            normalized.append(im)
        # enforce 9:16 aspect ratio by padding (or cropping if necessary)
        frames = []
        for im in normalized:
            # compute desired size based on height to keep orientation vertical
            target_h = im.height
            target_w = int(target_h * 9 / 16)
            if im.width > target_w:
                # too wide: scale down to fit width
                im = im.resize((target_w, target_h), Image.LANCZOS)
            elif im.width < target_w:
                # pad sides with black
                new = Image.new("RGB", (target_w, target_h), (0, 0, 0))
                x = (target_w - im.width) // 2
                new.paste(im, (x, 0))
                im = new
            # convert to array
            try:
                import numpy as np
                arr = np.array(im)
            except ImportError:
                arr = im
            frames.append(imageio.core.util.Array(arr))
        return frames

    image_paths = [f["path"] for f in saved if f["path"].lower().endswith(("jpg","jpeg","png","gif"))]

    if imageio is not None and image_paths:
        try:
            frames = _prepare_images(image_paths)
            if frames:
                ffmpeg_exe = shutil.which("ffmpeg")
                if ffmpeg_exe:
                    vid_dest = upload_dir / "slideshow.mp4"
                    imageio.mimwrite(str(vid_dest), frames, fps=1, codec="libx264")
                    video_url = f"/uploads/{vid_dest.name}"
                    mp4_created = True
                else:
                    # no ffmpeg, write a gif directly using imageio
                    gif_dest = upload_dir / "slideshow.gif"
                    # duration in seconds per frame
                    imageio.mimsave(str(gif_dest), frames, duration=1)
                    video_url = f"/uploads/{gif_dest.name}"
        except Exception:
            # any failure leaves video_url as None
            mp4_created = False

    return video_url


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...), description: Optional[str] = Form(None)
):
    """Accept multiple files and save them to the upload temp dir, generating
    a simple slideshow video/gif from image uploads and overlaying the
    optional description text."""

    saved = _save_files(files)
    video_url = _generate_slideshow(saved, description)
    return {"uploaded": saved, "description": description, "video_url": video_url}


@router.post("/edit")
async def edit_image(image: UploadFile = File(...), description: Optional[str] = Form(None)):
    """Accept a single image and a description, apply a simple edit (enhance + watermark text), return a base64 PNG."""
    if Image is None:
        raise HTTPException(status_code=500, detail="Pillow is not installed. Install with `pip install pillow`.")

    content = await image.read()
    try:
        img = Image.open(io.BytesIO(content)).convert("RGBA")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")

    # Simple edits: enhance color and sharpen
    try:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.2)
    except Exception:
        pass

    try:
        img = img.filter(ImageFilter.SHARPEN)
    except Exception:
        pass

    # Overlay description text at bottom if provided
    if description:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size=24)
        except Exception:
            font = ImageFont.load_default()

        text = description.strip()
        # compute text size and position (robust across Pillow versions)
        margin = 8
        try:
            text_w, text_h = font.getsize(text)
        except Exception:
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except Exception:
                text_w, text_h = (0, 20)
        x = margin
        y = img.height - text_h - margin
        # semi-transparent rectangle
        rectangle_y0 = y - margin
        rectangle_y1 = img.height
        try:
            draw.rectangle([(0, rectangle_y0), (img.width, rectangle_y1)], fill=(0, 0, 0, 160))
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        except Exception:
            # fallback: ignore drawing issues
            pass

    # return as base64 PNG data URI
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return JSONResponse({"edited_image": f"data:image/png;base64,{b64}"})
