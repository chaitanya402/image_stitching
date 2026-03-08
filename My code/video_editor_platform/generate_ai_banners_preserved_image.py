"""
AI Banner Generator with Preserved Input Image
==============================================
Preserves 100% of input image + adds AI-generated decorative banners + text overlays

Features:
- Input product image preserved entirely in center
- AI-generated decorative banners on top/bottom
- Dynamic text overlays from your description
- Professional composite result

Usage:
    python generate_ai_banners_preserved_image.py <input_image> <description> [--backend sdxl-remote] [--output output_dir]

Example:
    python generate_ai_banners_preserved_image.py "jackets.jpg" "Flat 20% off on motorcycle gear" --backend sdxl-remote
"""

import sys
import os
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
import textwrap
import re

# Add service path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from src.services.description_based_icon_agent import DescriptionBasedIconAgent
from src.services.image_generator_factory import ImageGeneratorFactory
from src.services.banner_content_agent import BannerContentAgent


def generate_banner_prompt(description: str, banner_content: dict, position: str = "top") -> str:
    """
    Build an SDXL prompt for AI banner generation that is informed by the
    LLM-extracted product keywords so the background art matches the product.
    The centre is kept empty — text is rendered over it by PIL.
    """
    # Pull 2-3 keywords from the AI-generated content for contextual styling
    tagline = banner_content.get("banner_tagline", "").lower()
    points = " ".join(banner_content.get("offer_points", [])).lower()
    combined = f"{description} {tagline} {points}"

    # Detect broad product domain for subtle background theming
    style_hint = "premium retail"
    if any(w in combined for w in ["motor", "bike", "riding", "gear", "jacket", "helmet"]):
        style_hint = "premium motorcycle and riding gear"
    elif any(w in combined for w in ["fashion", "cloth", "wear", "apparel", "dress"]):
        style_hint = "luxury fashion and apparel"
    elif any(w in combined for w in ["electron", "phone", "tech", "gadget", "laptop"]):
        style_hint = "high-tech electronics"
    elif any(w in combined for w in ["sport", "athlet", "fitness", "gym"]):
        style_hint = "athletic sportswear"

    if position == "top":
        prompt = (
            f"luxury advertising banner for {style_hint}, "
            "very dark navy to black gradient background, "
            "thin gold geometric border lines along edges only, "
            "subtle carbon-fiber or brushed-metal texture in corners, "
            "large completely empty dark centre — no objects, no symbols, "
            "clean minimal design, absolutely no text, no logos, no people, "
            "8k professional commercial photography"
        )
    else:
        prompt = (
            f"luxury promotional footer for {style_hint}, "
            "deep charcoal black background, "
            "thin gold accent lines along top and bottom edges only, "
            "subtle abstract shapes on far left and right margins only, "
            "large empty dark centre area, "
            "no text, no logos, no people, "
            "8k professional commercial design"
        )
    return prompt


def draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    xy: tuple,
    text: str,
    font,
    fill: str,
    shadow_color: tuple = (0, 0, 0, 200),
    shadow_offset: int = 3,
    stroke_width: int = 2,
) -> None:
    """
    Draw text with a drop shadow and outline stroke for maximum legibility
    on any background.
    """
    x, y = xy
    # Draw shadow (offset dark copy)
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    # Draw stroke by drawing text in black at 8 surrounding offsets
    for ox in range(-stroke_width, stroke_width + 1):
        for oy in range(-stroke_width, stroke_width + 1):
            if ox == 0 and oy == 0:
                continue
            draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0))
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)


def draw_text_with_backing(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    fill: str,
    center_x: int,
    y: int,
    padding_x: int = 30,
    padding_y: int = 10,
    backing_color: tuple = (0, 0, 0, 160),
    radius: int = 12,
) -> int:
    """
    Draw text centred at center_x with a rounded semi-transparent backing
    rectangle for readability. Returns the bottom y of the drawn block.
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = center_x - tw // 2

    # Backing rectangle
    rect = [
        tx - padding_x,
        y - padding_y,
        tx + tw + padding_x,
        y + th + padding_y,
    ]
    # Draw rounded backing on a separate RGBA layer
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rounded_rectangle(rect, radius=radius, fill=backing_color)
    image.paste(Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB'),
                (0, 0))
    # Re-acquire draw after paste
    draw_ref = ImageDraw.Draw(image)
    draw_text_with_shadow(draw_ref, (tx, y), text, font=font, fill=fill)
    return rect[3] + padding_y  # bottom edge


def draw_discount_badge(
    image: Image.Image,
    discount: int,
    cx: int,
    cy: int,
    radius: int,
) -> None:
    """
    Draw a circular gold discount badge centred at (cx, cy) with given radius.
    Layers: outer shadow → dark ring → gold fill → inner highlight → text.
    """
    r = radius
    # Shadow
    shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([cx - r + 4, cy - r + 4, cx + r + 4, cy + r + 4], fill=(0, 0, 0, 120))
    image.paste(Image.alpha_composite(image.convert('RGBA'), shadow).convert('RGB'), (0, 0))

    draw = ImageDraw.Draw(image)
    # Outer dark ring
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 20, 0))
    # Gold fill
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], fill="#DAA520")
    # Bright centre
    draw.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], fill="#FFD700")
    # Top-left highlight
    hl = int(r * 0.45)
    draw.ellipse([cx - r + 14, cy - r + 14, cx - r + 14 + hl, cy - r + 14 + hl],
                 fill=(255, 240, 100, 160))
    # Border
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                 outline="#8B4513", width=3)

    # Text
    pct_text = f"{discount}%"
    off_text = "OFF"
    try:
        pct_font = ImageFont.truetype("arialbd.ttf", int(r * 0.62))
        off_font = ImageFont.truetype("arialbd.ttf", int(r * 0.32))
    except:
        pct_font = ImageFont.load_default()
        off_font = ImageFont.load_default()

    pb = draw.textbbox((0, 0), pct_text, font=pct_font)
    pw, ph = pb[2] - pb[0], pb[3] - pb[1]
    ob = draw.textbbox((0, 0), off_text, font=off_font)
    ow, oh = ob[2] - ob[0], ob[3] - ob[1]
    gap = int(r * 0.04)
    block_h = ph + gap + oh
    py = cy - block_h // 2
    oy = py + ph + gap

    # Shadow + stroke on pct
    draw_text_with_shadow(draw, (cx - pw // 2, py), pct_text, pct_font,
                          fill="#1a0a00", shadow_offset=2, stroke_width=1)
    draw_text_with_shadow(draw, (cx - ow // 2, oy), off_text, off_font,
                          fill="#1a0a00", shadow_offset=1, stroke_width=1)


def composite_image_with_ai_banners(
    input_image_path: str,
    description: str,
    backend: str = "sdxl-remote",
    output_dir: str = "output_images",
    top_banner_height_pct: float = 20.0,
    banner_inference_steps: int = 30,
    banner_guidance_scale: float = 3.0
) -> bool:
    """
    Overlay AI-generated top banner + promo elements onto input image.
    Output dimensions = input dimensions exactly.

    Args:
        input_image_path: Path to input product image
        description: Product description with promotional text
        backend: AI model backend (sdxl-remote, flux-remote, etc)
        output_dir: Output directory for result
        top_banner_height_pct: Height of the top banner as % of input image height (default 20%)
        banner_inference_steps: AI inference steps (higher = better quality, slower)
        banner_guidance_scale: How closely to follow prompts (1-7 typical)
    """
    
    print("\n" + "="*80)
    print("GENERATING COMPOSITED IMAGE: AI BANNERS + PRESERVED INPUT")
    print("="*80)
    
    # ===== STEP 1: Load Input Image =====
    input_path = Path(input_image_path)
    if not input_path.exists():
        print(f"\n[ERROR] Input image not found: {input_path}")
        return False
    
    try:
        input_img = Image.open(input_path).convert('RGB')
        img_width, img_height = input_img.size
        print(f"\n[+] Input image loaded: {input_path}")
        print(f"    Dimensions: {img_width}x{img_height}")
    except Exception as e:
        print(f"\n[ERROR] Failed to load input image: {e}")
        return False
    
    # ===== STEP 2: Parse Description =====
    print("\n[+] Initializing agents...")
    icon_agent = DescriptionBasedIconAgent()
    factory = ImageGeneratorFactory()
    
    parsed_data = icon_agent.parse_description(description)
    discount = parsed_data.get('discount_percent', 0)

    # ---- AI content generation: LLM decides all copy ----
    print("\n[+] Calling BannerContentAgent (LLM)...")
    content_agent = BannerContentAgent()
    banner_content = content_agent.generate(description, discount)

    print(f"\n[AI-GENERATED BANNER CONTENT]:")
    print(f"  Headline  : {banner_content['banner_headline']}")
    print(f"  Tagline   : {banner_content['banner_tagline']}")
    print(f"  Badge     : {banner_content['badge_label']}")
    for i, pt in enumerate(banner_content['offer_points'], 1):
        print(f"  Point {i}   : {pt}")
    
    # ===== STEP 3: Generate AI Top Banner =====
    print("\n" + "-"*80)
    print("STEP 1: Generate AI Top Banner")
    print("-"*80)

    top_banner_height = int(img_height * (top_banner_height_pct / 100.0))

    print(f"\n[GENERATING TOP BANNER]...")
    print(f"  Size: {img_width}x{top_banner_height}")
    top_prompt = generate_banner_prompt(description, banner_content, position="top")
    print(f"  Prompt: {top_prompt[:70]}...")

    try:
        generator = factory.create(backend)
        top_banner = generator.generate_image(
            prompt=top_prompt,
            width=img_width,
            height=top_banner_height,
            num_inference_steps=banner_inference_steps,
            guidance_scale=banner_guidance_scale
        )
        if top_banner is None:
            print("[WARNING] Top banner generation failed, using gradient fallback")
            top_banner = create_gradient_banner(img_width, top_banner_height, "gold")
        else:
            top_banner = top_banner.resize((img_width, top_banner_height), Image.Resampling.LANCZOS)
            print(f"  [OK] Generated: {top_banner.size}")
    except Exception as e:
        print(f"[WARNING] Top banner error: {e}")
        top_banner = create_gradient_banner(img_width, top_banner_height, "gold")

    # ===== STEP 4: Composite — same dimensions as input =====
    print("\n" + "-"*80)
    print("STEP 2: Composite (output = input dimensions)")
    print("-"*80)

    # Start with a full copy of the input image
    final_image = input_img.copy()

    # Blend top banner OVER the top portion of the image using alpha composite
    banner_rgba = top_banner.convert('RGBA')
    # Add a semi-transparent dark overlay on the banner so text is readable
    darkener = Image.new('RGBA', (img_width, top_banner_height), (0, 0, 0, 80))
    banner_rgba = Image.alpha_composite(banner_rgba, darkener)

    # Paste the banner strip over the top of the image
    final_image.paste(banner_rgba.convert('RGB'), (0, 0))
    print(f"\n[COMPOSITING]:")
    print(f"  Output dimensions: {img_width}x{img_height} (unchanged)")
    print(f"  [OK] Top banner overlaid at (0, 0) -> (0, {top_banner_height})")
    print(f"  [OK] Rest of input image preserved")
    
    # ===== STEP 5: Add Text + Badge Overlays directly on image =====
    print("\n" + "-"*80)
    print("STEP 3: Add Text + Badge Overlays")
    print("-"*80)

    center_x = img_width // 2

    # ---- TOP BANNER: headline text centred in banner strip ----
    try:
        disc_font = ImageFont.truetype("arialbd.ttf", int(top_banner_height * 0.26))
    except:
        disc_font = ImageFont.load_default()

    # Badge: large circle straddling the banner/image border
    badge_radius = min(int(top_banner_height * 0.38), 160)
    badge_cx = img_width - badge_radius - int(img_width * 0.03)
    badge_cy = top_banner_height  # centred on the banner/image border

    # Headline centred across the full banner width
    text_center_x = img_width // 2

    headline_text = banner_content['banner_headline']
    draw_tmp = ImageDraw.Draw(final_image)
    db = draw_tmp.textbbox((0, 0), headline_text, font=disc_font)
    disc_h = db[3] - db[1]
    disc_y = (top_banner_height - disc_h) // 2  # centred vertically in banner

    print(f"\n[TOP BANNER TEXT]: '{headline_text}'")
    draw_text_with_backing(
        final_image, ImageDraw.Draw(final_image),
        headline_text, disc_font, fill="#FFD700",
        center_x=text_center_x, y=disc_y,
        padding_x=30, padding_y=10,
        backing_color=(0, 0, 0, 160), radius=14
    )
    print(f"  [OK] Placed in top banner strip")

    # ---- DISCOUNT BADGE: shown only if LLM confirms a badge is warranted ----
    badge_label = banner_content.get('badge_label', '')
    if badge_label and discount > 0:
        print(f"\n[DISCOUNT BADGE]: {badge_label} at ({badge_cx}, {badge_cy})")
        draw_discount_badge(final_image, discount, badge_cx, badge_cy, badge_radius)
        print(f"  [OK] Badge drawn (r={badge_radius})")

    # ---- OFFER TEXT BLOCK: description lines + CTA near bottom of image ----
    offer_zone_h = int(img_height * 0.22)   # bottom 22% of image is the offer zone
    offer_zone_top = img_height - offer_zone_h

    try:
        desc_font = ImageFont.truetype("arial.ttf",   int(offer_zone_h * 0.14))
        cta_font  = ImageFont.truetype("arialbd.ttf", int(offer_zone_h * 0.28))
    except:
        desc_font = ImageFont.load_default()
        cta_font  = ImageFont.load_default()

    # Dark semi-transparent strip over offer zone
    offer_overlay = Image.new('RGBA', (img_width, offer_zone_h), (10, 10, 10, 190))
    final_image.paste(
        Image.alpha_composite(
            final_image.crop((0, offer_zone_top, img_width, img_height)).convert('RGBA'),
            offer_overlay
        ).convert('RGB'),
        (0, offer_zone_top)
    )
    print(f"\n[OFFER ZONE]: bottom {offer_zone_h}px darkened")

    # Use AI-generated offer points — already clean, no discount duplication
    draw_tmp3 = ImageDraw.Draw(final_image)
    sample_bbox = draw_tmp3.textbbox((0, 0), "W", font=desc_font)
    char_w = max(1, sample_bbox[2] - sample_bbox[0])
    max_chars = max(10, (img_width - 80) // char_w)
    # Each LLM point is already a short phrase; wrap only if it somehow exceeds width
    raw_points = banner_content.get('offer_points', [])
    wrapped_lines: list[str] = []
    for pt in raw_points:
        lines = textwrap.wrap(pt, width=max_chars) or [pt]
        wrapped_lines.extend(lines)

    line_h_bbox = draw_tmp3.textbbox((0, 0), "Ag", font=desc_font)
    line_h = (line_h_bbox[3] - line_h_bbox[1]) + int(offer_zone_h * 0.05)
    total_block = len(wrapped_lines) * line_h
    current_y = offer_zone_top + max(10, (offer_zone_h - total_block) // 2)

    for line in wrapped_lines:
        current_y = draw_text_with_backing(
            final_image, ImageDraw.Draw(final_image),
            line, desc_font, fill="white",
            center_x=center_x, y=current_y,
            padding_x=18, padding_y=5,
            backing_color=(0, 0, 0, 0), radius=6   # no extra backing — strip already dark
        ) + 2
    print(f"  [OK] Description: {len(wrapped_lines)} lines")

 
    
    # ===== STEP 6: Save Output =====
    print("\n" + "-"*80)
    print("STEP 4: Save Output")
    print("-"*80)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    keywords = parsed_data.get('keywords', ['promo'])[:2]
    filename = f"ai_banners_{'_'.join(keywords)}_{discount}pct.jpg"
    output_file = output_path / filename
    
    try:
        final_image.save(str(output_file), 'JPEG', quality=95)
        file_size_kb = output_file.stat().st_size / 1024
        print(f"\n[SUCCESS]")
        print(f"  Saved: {output_file}")
        print(f"  Size: {file_size_kb:.1f} KB")
        print(f"  Dimensions: {final_image.size}")
    except Exception as e:
        print(f"\n[ERROR] Failed to save: {e}")
        return False
    
    # ===== Save Metadata =====
    metadata = {
        "method": "AI Top Banner Overlay + Badges (same dimensions)",
        "input_image_path": str(input_path),
        "input_dimensions": f"{img_width}x{img_height}",
        "output_dimensions": f"{final_image.size[0]}x{final_image.size[1]}",
        "description": description,
        "discount_percent": discount,
        "banner_content": banner_content,
        "backend": backend,
        "top_banner_height": top_banner_height,
        "output_file_size_kb": round(file_size_kb, 1),
        "filename": filename,
        "created_at": datetime.now().isoformat(),
        "quality": "Premium AI-Generated Banner Overlay"
    }
    
    metadata_file = output_path / f"{output_file.stem}_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata: {metadata_file}")
    
    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80 + "\n")
    
    return True


def create_gradient_banner(width: int, height: int, color_scheme: str = "gold") -> Image.Image:
    """
    Create a fallback gradient banner if AI generation fails.
    
    Args:
        width: Banner width
        height: Banner height
        color_scheme: "gold", "dark", or "blue"
        
    Returns:
        PIL Image with gradient
    """
    banner = Image.new('RGB', (width, height))
    pixels = banner.load()
    
    if color_scheme == "gold":
        start_color = (218, 165, 32)  # Goldenrod
        end_color = (255, 215, 0)     # Gold
    elif color_scheme == "dark":
        start_color = (40, 40, 40)    # Dark gray
        end_color = (80, 80, 80)      # Light gray
    else:  # blue
        start_color = (25, 55, 109)   # Dark blue
        end_color = (30, 80, 160)     # Blue
    
    # Create gradient
    for y in range(height):
        ratio = y / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        
        for x in range(width):
            pixels[x, y] = (r, g, b)
    
    return banner


def main():
    parser = argparse.ArgumentParser(
        description="Generate composited image with AI banners and preserved input image"
    )
    parser.add_argument("input_image", help="Path to input product image")
    parser.add_argument("description", help="Product description with promotional text")
    parser.add_argument(
        "--backend",
        default="sdxl-remote",
        choices=["sdxl-remote", "flux-remote", "hf-inference"],
        help="AI model backend for banner generation (default: sdxl-remote)"
    )
    parser.add_argument(
        "--output",
        default="output_images",
        help="Output directory (default: output_images)"
    )
    parser.add_argument(
        "--top-banner",
        type=float,
        default=20.0,
        help="Top banner height as %% of input image height (default: 20)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=30,
        help="AI inference steps for banner (higher = better quality; default: 30)"
    )
    parser.add_argument(
        "--guidance",
        type=float,
        default=3.0,
        help="AI guidance scale for banner (1-7; default: 3.0)"
    )

    args = parser.parse_args()

    success = composite_image_with_ai_banners(
        input_image_path=args.input_image,
        description=args.description,
        backend=args.backend,
        output_dir=args.output,
        top_banner_height_pct=args.top_banner,
        banner_inference_steps=args.steps,
        banner_guidance_scale=args.guidance
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
