#!/usr/bin/env python
"""
Carousel Video Generator with GenAI Banners
=============================================
Creates a social-media-ready carousel video from multiple product images.

Key design:
- Input images are shown clean (no per-image editing)
- One AI-generated banner background is produced once and composited into
  every frame at runtime via OpenCV, keeping generation fast
- Gold discount badge + offer text overlaid on the final video frames
- Smooth slide-left transition between images
- Portrait 9:16 output (1080x1920) by default, configurable

Usage:
    python generate_carousel_with_banners.py
        "img1.jpg" "img2.jpg" ...
        --description "flat 20% off on motorcycle gear, customization available"
        --output "output_video.mp4"
        [--backend sdxl-remote]
        [--width 1080] [--height 1920]
        [--fps 30] [--duration 4]
        [--steps 30]

Example:
    python generate_carousel_with_banners.py
        "C:/input images/jackets.jpg" "C:/input images/helmet.jpg"
        --description "flat 20% off on motor cycle gear, customization available"
        --output "C:/output/carousel_promo.mp4"
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List
import numpy as np

# PIL
from PIL import Image, ImageDraw, ImageFont

# OpenCV
try:
    import cv2
except ImportError:
    print("[ERROR] OpenCV not installed. Run: pip install opencv-python")
    sys.exit(1)

# Project imports
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from src.services.description_based_icon_agent import DescriptionBasedIconAgent
from src.services.image_generator_factory import ImageGeneratorFactory
from src.services.banner_content_agent import BannerContentAgent


# ---------------------------------------------------------------------------
# Reuse PIL text helpers from generate_ai_banners_preserved_image
# ---------------------------------------------------------------------------

def draw_text_with_shadow(draw, xy, text, font, fill,
                          shadow_color=(0, 0, 0, 200), shadow_offset=3, stroke_width=2):
    x, y = xy
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    for ox in range(-stroke_width, stroke_width + 1):
        for oy in range(-stroke_width, stroke_width + 1):
            if ox == 0 and oy == 0:
                continue
            draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)


def draw_text_centered(image, text, font, fill, center_x, y,
                       padding_x=30, padding_y=10,
                       backing_color=(0, 0, 0, 160), radius=12):
    """Draw text with semi-transparent rounded backing. Returns bottom y."""
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = center_x - tw // 2
    rect = [tx - padding_x, y - padding_y, tx + tw + padding_x, y + th + padding_y]
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rounded_rectangle(rect, radius=radius, fill=backing_color)
    image.paste(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    draw_text_with_shadow(ImageDraw.Draw(image), (tx, y), text, font, fill)
    return rect[3] + padding_y


def draw_discount_badge(image, discount, cx, cy, radius):
    """Gold circular discount badge."""
    r = radius
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([cx - r + 4, cy - r + 4, cx + r + 4, cy + r + 4], fill=(0, 0, 0, 120))
    image.paste(Image.alpha_composite(image.convert("RGBA"), shadow).convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(image)
    draw.ellipse([cx - r,     cy - r,     cx + r,     cy + r],     fill=(30, 20, 0))
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], fill="#DAA520")
    draw.ellipse([cx - r + 10,cy - r + 10,cx + r - 10,cy + r - 10],fill="#FFD700")
    hl = int(r * 0.45)
    draw.ellipse([cx - r + 14, cy - r + 14,
                  cx - r + 14 + hl, cy - r + 14 + hl], fill=(255, 240, 100, 160))
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                 outline="#8B4513", width=3)

    pct_text, off_text = f"{discount}%", "OFF"
    try:
        pct_font = ImageFont.truetype("arialbd.ttf", int(r * 0.62))
        off_font = ImageFont.truetype("arialbd.ttf", int(r * 0.32))
    except:
        pct_font = off_font = ImageFont.load_default()

    d = ImageDraw.Draw(image)
    pb = d.textbbox((0, 0), pct_text, font=pct_font)
    pw, ph = pb[2] - pb[0], pb[3] - pb[1]
    ob = d.textbbox((0, 0), off_text, font=off_font)
    ow, oh = ob[2] - ob[0], ob[3] - ob[1]
    gap = int(r * 0.04)
    block_h = ph + gap + oh
    py = cy - block_h // 2
    oy = py + ph + gap
    draw_text_with_shadow(d, (cx - pw // 2, py), pct_text, pct_font,
                          fill="#1a0a00", shadow_offset=2, stroke_width=1)
    draw_text_with_shadow(d, (cx - ow // 2, oy), off_text, off_font,
                          fill="#1a0a00", shadow_offset=1, stroke_width=1)


# ---------------------------------------------------------------------------
# Banner generation
# ---------------------------------------------------------------------------

def generate_banner_background(description, banner_content, width, height, backend,
                                inference_steps, guidance_scale, position="top"):
    """
    Generate a single AI banner background image (PIL Image).
    position: "top" (header banner) or "bottom" (footer/offer banner).
    Falls back to a dark gradient if generation fails.
    """
    style_hint = "premium retail"
    combined = description.lower() + " " + " ".join(banner_content.get("offer_points", []))
    if any(w in combined for w in ["motor", "bike", "riding", "gear", "jacket", "helmet"]):
        style_hint = "premium motorcycle and riding gear"
    elif any(w in combined for w in ["fashion", "cloth", "wear", "apparel"]):
        style_hint = "luxury fashion and apparel"
    elif any(w in combined for w in ["electron", "phone", "tech", "laptop"]):
        style_hint = "high-tech electronics"
    elif any(w in combined for w in ["sport", "athlet", "fitness"]):
        style_hint = "athletic sportswear"

    if position == "bottom":
        prompt = (
            f"luxury advertising footer banner for {style_hint}, "
            "deep charcoal to black horizontal gradient background, "
            "thin gold horizontal accent lines along top edge only, "
            "subtle dark leather or carbon-fiber texture, "
            "completely empty flat dark centre — no objects, no symbols, "
            "clean minimal design, absolutely no text, no logos, no people, "
            "8k professional commercial photography"
        )
    else:
        prompt = (
            f"luxury advertising banner for {style_hint}, "
            "very dark navy to black gradient background, "
            "thin gold geometric border lines along edges only, "
            "subtle carbon-fiber or brushed-metal texture in corners, "
            "large completely empty dark centre — no objects, no symbols, "
            "clean minimal design, absolutely no text, no logos, no people, "
            "8k professional commercial photography"
        )

    factory = ImageGeneratorFactory()
    try:
        generator = factory.create(backend)
        banner = generator.generate_image(
            prompt=prompt, width=width, height=height,
            num_inference_steps=inference_steps, guidance_scale=guidance_scale
        )
        if banner:
            return banner.resize((width, height), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"  [WARNING] Banner generation failed ({e}), using gradient fallback")

    # Gradient fallback
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        t = y / height
        r = int(10 + 5 * t)
        g = int(10 + 10 * t)
        b = int(30 + 20 * t)
        arr[y, :] = [r, g, b]
    return Image.fromarray(arr)


def build_banner_frame(banner_bg, width, banner_height, banner_content, discount):
    """
    Composite text + badge onto the AI banner background.
    Returns a PIL Image of size (width, banner_height).
    """
    banner = banner_bg.copy().convert("RGB")

    # Darken slightly for text legibility
    overlay = Image.new("RGBA", (width, banner_height), (0, 0, 0, 80))
    banner = Image.alpha_composite(banner.convert("RGBA"), overlay).convert("RGB")

    # Badge geometry
    badge_radius = min(int(banner_height * 0.38), 160)
    badge_cx = width - badge_radius - int(width * 0.03)
    badge_cy = banner_height  # straddles the banner/image border

    headline = banner_content.get("banner_headline", "")
    if headline:
        # Available horizontal space: left margin → left edge of badge with a gap
        margin_left   = int(width * 0.03)
        badge_left_x  = badge_cx - badge_radius - int(width * 0.02)
        available_w   = badge_left_x - margin_left

        # Auto-shrink font until text fits in available_w
        max_fs = int(banner_height * 0.30)
        min_fs = int(banner_height * 0.11)
        headline_font = None
        for fsize in range(max_fs, min_fs - 1, -2):
            try:
                f = ImageFont.truetype("arialbd.ttf", fsize)
            except Exception:
                f = ImageFont.load_default()
                headline_font = f
                break
            bb_tmp = ImageDraw.Draw(banner).textbbox((0, 0), headline, font=f)
            if (bb_tmp[2] - bb_tmp[0]) + 56 <= available_w:
                headline_font = f
                break
        if headline_font is None:
            try:
                headline_font = ImageFont.truetype("arialbd.ttf", min_fs)
            except Exception:
                headline_font = ImageFont.load_default()

        # Centre text in the left zone only (not the full width)
        center_x = margin_left + available_w // 2
        d = ImageDraw.Draw(banner)
        bb = d.textbbox((0, 0), headline, font=headline_font)
        hh = bb[3] - bb[1]
        hy = (banner_height - hh) // 2
        draw_text_centered(banner, headline, headline_font, "#FFD700",
                           center_x=center_x, y=hy,
                           padding_x=24, padding_y=10,
                           backing_color=(0, 0, 0, 160), radius=14)

    # Badge (drawn on the full composited image, centred on the bottom edge)
    if discount > 0:
        # Extend canvas to include badge overflow below banner
        extended_h = banner_height + badge_radius
        extended = Image.new("RGB", (width, extended_h), (0, 0, 0, 0))
        # paste banner background on top
        # We'll return just the banner strip — badge must be drawn on the frame later
        # Return badge params separately
        pass

    return banner, badge_cx, badge_cy, badge_radius


def build_bottom_banner_frame(banner_bg, width, bottom_height, offer_points):
    """
    Composite offer-point text onto the AI bottom banner background.
    Returns a PIL Image of size (width, bottom_height).
    """
    banner = banner_bg.copy().convert("RGB")

    # Darken slightly for text legibility
    overlay = Image.new("RGBA", (width, bottom_height), (0, 0, 0, 90))
    banner = Image.alpha_composite(banner.convert("RGBA"), overlay).convert("RGB")

    # Thin gold separator line at the very top
    draw = ImageDraw.Draw(banner)
    draw.rectangle([0, 0, width, 3], fill="#DAA520")

    if not offer_points:
        return banner

    try:
        pt_font = ImageFont.truetype("arialbd.ttf", int(bottom_height * 0.22))
    except:
        pt_font = ImageFont.load_default()

    # Distribute bullets vertically
    n = len(offer_points)
    slot_h = bottom_height // n
    for idx, pt in enumerate(offer_points):
        slot_top = idx * slot_h
        slot_cy = slot_top + slot_h // 2
        d = ImageDraw.Draw(banner)
        bb = d.textbbox((0, 0), pt, font=pt_font)
        th = bb[3] - bb[1]
        ty = slot_cy - th // 2
        draw_text_centered(banner, pt, pt_font, "#FFD700",
                           center_x=width // 2, y=ty,
                           padding_x=28, padding_y=8,
                           backing_color=(0, 0, 0, 140), radius=12)

    return banner


# ---------------------------------------------------------------------------
# Frame composer: merge product image + top banner + bottom banner + badge
# ---------------------------------------------------------------------------

def compose_frame(product_img_cv2, banner_pil, bottom_banner_pil,
                  width, height, banner_height, bottom_height,
                  badge_cx, badge_cy, badge_radius, discount):
    """
    Build a single video frame (numpy BGR) — clean 3-zone layout:
      [top banner  : banner_height px]   AI background + headline  
      [product zone: height - banner_height - bottom_height px]  clean image
      [bottom banner: bottom_height px]  AI background + offer bullets
    """
    # --- Product zone (middle strip only) ---
    h, w = product_img_cv2.shape[:2]
    product_zone_h = height - banner_height - bottom_height
    scale = max(width / w, product_zone_h / h)
    rw, rh = int(w * scale), int(h * scale)
    resized = cv2.resize(product_img_cv2, (rw, rh), interpolation=cv2.INTER_LANCZOS4)

    # Centre-crop to the clean middle zone
    x0 = (rw - width) // 2
    y0 = (rh - product_zone_h) // 2
    product_zone = resized[y0:y0 + product_zone_h, x0:x0 + width]

    # Build frame: black canvas, paste product in the middle
    frame_np = np.zeros((height, width, 3), dtype=np.uint8)
    frame_np[banner_height: banner_height + product_zone_h, :] = product_zone

    # Convert to PIL
    frame_pil = Image.fromarray(cv2.cvtColor(frame_np, cv2.COLOR_BGR2RGB))

    # --- Top AI banner ---
    frame_pil.paste(banner_pil, (0, 0))

    # --- Bottom AI banner ---
    frame_pil.paste(bottom_banner_pil, (0, height - bottom_height))

    # --- Discount badge (straddles top banner / product border) ---
    if discount > 0:
        draw_discount_badge(frame_pil, discount, badge_cx, badge_cy, badge_radius)

    return cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------------------
# Main carousel generator
# ---------------------------------------------------------------------------

def generate_carousel(image_paths, description, backend, output_path,
                      width=1080, height=1920, fps=30,
                      image_duration=4, transition_frames=25,
                      num_loops=2, inference_steps=30, guidance_scale=3.0):

    print("\n" + "=" * 80)
    print("CAROUSEL VIDEO GENERATOR WITH GENAI BANNERS")
    print("=" * 80)

    # ── Step 1: Parse description ──────────────────────────────────────────
    print("\n[STEP 1] Parsing description...")
    icon_agent = DescriptionBasedIconAgent()
    parsed = icon_agent.parse_description(description)
    discount = parsed.get("discount_percent", 0)

    print("[STEP 1b] Generating banner content (LLM)...")
    content_agent = BannerContentAgent()
    banner_content = content_agent.generate(description, discount)

    print(f"\n  Headline  : {banner_content['banner_headline']}")
    print(f"  Badge     : {banner_content['badge_label']}")
    for i, pt in enumerate(banner_content['offer_points'], 1):
        print(f"  Point {i}   : {pt}")

    # ── Step 2: Load product images ────────────────────────────────────────
    print("\n[STEP 2] Loading product images...")
    images_cv2 = []
    for p in image_paths:
        img = cv2.imread(str(p))
        if img is None:
            print(f"  [WARNING] Could not load: {p}")
            continue
        images_cv2.append(img)
        print(f"  ✓ {Path(p).name}  ({img.shape[1]}x{img.shape[0]})")

    if not images_cv2:
        print("[ERROR] No valid images loaded.")
        return False

    # ── Step 3: Generate AI top banner background ─────────────────────────
    print("\n[STEP 3] Generating AI top banner background (SDXL)...")
    banner_height  = int(height * 0.18)   # top 18%
    bottom_height  = int(height * 0.18)   # bottom 18% (same height = matching pair)

    top_bg = generate_banner_background(
        description, banner_content,
        width=width, height=banner_height,
        backend=backend,
        inference_steps=inference_steps,
        guidance_scale=guidance_scale,
        position="top"
    )
    print(f"  ✓ Top banner background: {top_bg.size}")

    banner_pil, badge_cx, badge_cy, badge_radius = build_banner_frame(
        top_bg, width, banner_height, banner_content, discount
    )
    print(f"  ✓ Top banner composed (headline + badge r={badge_radius})")

    # ── Step 3b: Generate AI bottom banner background ──────────────────────
    print("\n[STEP 3b] Generating AI bottom banner background (SDXL)...")
    bottom_bg = generate_banner_background(
        description, banner_content,
        width=width, height=bottom_height,
        backend=backend,
        inference_steps=inference_steps,
        guidance_scale=guidance_scale,
        position="bottom"
    )
    print(f"  ✓ Bottom banner background: {bottom_bg.size}")

    offer_points = banner_content.get("offer_points", [])
    bottom_banner_pil = build_bottom_banner_frame(
        bottom_bg, width, bottom_height, offer_points
    )
    print(f"  ✓ Bottom banner composed ({len(offer_points)} offer point(s))")

    # ── Step 4: Write video ────────────────────────────────────────────────
    print("\n[STEP 4] Writing video frames...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    if not writer.isOpened():
        print("[ERROR] Could not open video writer.")
        return False

    frames_per_image = fps * image_duration
    total_frames = 0

    def write_frame(img_cv2):
        nonlocal total_frames
        f = compose_frame(img_cv2, banner_pil, bottom_banner_pil,
                          width, height, banner_height, bottom_height,
                          badge_cx, badge_cy, badge_radius, discount)
        writer.write(f)
        total_frames += 1

    easing = lambda t: t * t * (3 - 2 * t)  # smoothstep

    for loop in range(num_loops):
        print(f"\n  Loop {loop + 1}/{num_loops}")
        for i, img in enumerate(images_cv2):
            # Static hold
            for _ in range(frames_per_image):
                write_frame(img)

            # Slide-left transition to next
            next_img = images_cv2[(i + 1) % len(images_cv2)]
            if i < len(images_cv2) - 1 or loop < num_loops - 1:
                for t_idx in range(transition_frames):
                    progress = easing(t_idx / transition_frames)
                    offset = int(width * progress)

                    curr_frame = compose_frame(img, banner_pil, bottom_banner_pil,
                                               width, height, banner_height, bottom_height,
                                               badge_cx, badge_cy, badge_radius, discount)
                    next_frame = compose_frame(next_img, banner_pil, bottom_banner_pil,
                                               width, height, banner_height, bottom_height,
                                               badge_cx, badge_cy, badge_radius, discount)

                    # Slide only the product zone; banners stay pinned
                    blended = np.zeros((height, width, 3), dtype=np.uint8)
                    if offset < width:
                        blended[:, :width - offset] = curr_frame[:, offset:]
                    blended[:, width - offset:] = next_frame[:, :offset]

                    # Re-pin both AI banners so they never slide
                    blended_pil = Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))
                    blended_pil.paste(banner_pil, (0, 0))
                    blended_pil.paste(bottom_banner_pil, (0, height - bottom_height))

                    if discount > 0:
                        draw_discount_badge(blended_pil, discount, badge_cx, badge_cy, badge_radius)

                    writer.write(cv2.cvtColor(np.array(blended_pil), cv2.COLOR_RGB2BGR))
                    total_frames += 1

            print(f"    ✓ Image {i + 1}/{len(images_cv2)} — {frames_per_image} hold + "
                  f"{'0' if (i == len(images_cv2)-1 and loop == num_loops-1) else str(transition_frames)} transition frames")

    writer.release()

    duration = total_frames / fps
    size_mb = Path(output_path).stat().st_size / (1024 * 1024)

    print("\n" + "=" * 80)
    print("✓ CAROUSEL VIDEO COMPLETE")
    print("=" * 80)
    print(f"  Output   : {output_path}")
    print(f"  Duration : {duration:.1f}s  ({total_frames} frames @ {fps}fps)")
    print(f"  Size     : {size_mb:.1f} MB")
    print(f"  Res      : {width}x{height}")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate carousel video with GenAI banners from multiple product images"
    )
    parser.add_argument("images", nargs="+",
                        help="Input image paths (or pass 'all' to use all images from input dir)")
    parser.add_argument("--description", "-d", required=True,
                        help="Promotional description, e.g. 'flat 20%% off on motorcycle gear'")
    parser.add_argument("--output", "-o",
                        default=r"C:\Users\ASUS\Desktop\Repos\image_stitching\output images\carousel_promo.mp4",
                        help="Output video path (.mp4)")
    parser.add_argument("--backend", default="sdxl-remote",
                        choices=["sdxl-remote", "flux-remote", "hf-inference"],
                        help="AI image generation backend")
    parser.add_argument("--width",    type=int, default=1080)
    parser.add_argument("--height",   type=int, default=1920)
    parser.add_argument("--fps",      type=int, default=30)
    parser.add_argument("--duration", type=int, default=4,
                        help="Seconds each image is shown")
    parser.add_argument("--loops",    type=int, default=2,
                        help="Number of times to loop through all images")
    parser.add_argument("--steps",    type=int, default=30,
                        help="AI inference steps")
    parser.add_argument("--input-dir", default=None,
                        help="Directory to scan for images when 'all' is passed")

    args = parser.parse_args()

    # Resolve image paths — allow 'all' shorthand
    if args.images == ["all"]:
        input_dir = Path(args.input_dir or
                         r"C:\Users\ASUS\Desktop\Repos\image_stitching\input images")
        image_paths = sorted(input_dir.glob("*.jpg")) + \
                      sorted(input_dir.glob("*.jpeg")) + \
                      sorted(input_dir.glob("*.png"))
        if not image_paths:
            print(f"[ERROR] No images found in {input_dir}")
            sys.exit(1)
        print(f"[INFO] Found {len(image_paths)} images in {input_dir}")
    else:
        image_paths = [Path(p) for p in args.images]

    success = generate_carousel(
        image_paths=image_paths,
        description=args.description,
        backend=args.backend,
        output_path=args.output,
        width=args.width,
        height=args.height,
        fps=args.fps,
        image_duration=args.duration,
        num_loops=args.loops,
        inference_steps=args.steps,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
