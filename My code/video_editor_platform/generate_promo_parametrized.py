#!/usr/bin/env python
"""
Parametrized promotional image generator using DescriptionBasedIconAgent.
Removes hardcoding and uses description to drive content generation.
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Setup path for imports
platform_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, platform_root)

from src.services.description_based_icon_agent import DescriptionBasedIconAgent


def create_discount_badge(size=550, discount_text="20% OFF", color_scheme=None):
    """Create a discount badge icon with premium styling"""
    if color_scheme is None:
        color_scheme = {"primary": (25, 55, 120), "accent": (255, 215, 0)}
    
    badge = Image.new("RGBA", (size + 30, size + 30), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    
    # Draw shadow
    shadow_offset = 8
    draw.ellipse(
        [shadow_offset, shadow_offset, size + shadow_offset, size + shadow_offset],
        fill=(0, 0, 0, 100)
    )
    
    # Draw outer circle (primary color)
    primary = color_scheme["primary"]
    draw.ellipse([0, 0, size-1, size-1], fill=primary + (255,), outline=(max(0, primary[0]-10), max(0, primary[1]-10), max(0, primary[2]-10), 255))
    
    # Draw white border
    border_width = 12
    for i in range(border_width):
        draw.ellipse(
            [i, i, size-1-i, size-1-i],
            outline=(255, 255, 255, 255)
        )
    
    # Draw inner circle (darker shade)
    inner_margin = 20
    inner_color = (max(0, primary[0]+10), max(0, primary[1]+20), min(255, primary[2]+40))
    draw.ellipse(
        [inner_margin, inner_margin, size-inner_margin-1, size-inner_margin-1],
        fill=inner_color + (255,)
    )
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", size=int(size*0.28), weight="bold")
    except:
        try:
            font = ImageFont.truetype("arial.ttf", size=int(size*0.28))
        except:
            font = ImageFont.load_default()
    
    # Split text into two lines
    lines = discount_text.split() if " " in discount_text else [discount_text[:3], discount_text[3:]]
    if len(lines) == 1:
        lines = [discount_text, "OFF"]
    
    line_height = int(size * 0.30)
    total_height = len(lines) * line_height
    start_y = (size - total_height) // 2 - 10
    
    # Draw each line centered
    accent = color_scheme["accent"]
    for i, line in enumerate(lines):
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (size - text_width) // 2
        text_y = start_y + i * line_height
        
        # Draw text with white outline
        outline_width = 2
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                draw.text((text_x + adj_x, text_y + adj_y), line, font=font, fill=(255, 255, 255, 150))
        
        draw.text((text_x, text_y), line, font=font, fill=accent + (255,))
    
    return badge


def create_arrow_icon(size=100, color=(0, 150, 200, 255)):
    """Create an arrow pointing down icon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw arrow shaft
    shaft_x1 = size // 2
    shaft_y1 = size // 4
    shaft_x2 = size // 2
    shaft_y2 = 3 * size // 4
    draw.line([(shaft_x1, shaft_y1), (shaft_x2, shaft_y2)], fill=color, width=8)
    
    # Draw arrowhead
    arrow_size = 20
    points = [
        (shaft_x2, shaft_y2),
        (shaft_x2 - arrow_size // 2, shaft_y2 - arrow_size),
        (shaft_x2 + arrow_size // 2, shaft_y2 - arrow_size),
    ]
    draw.polygon(points, fill=color)
    
    return icon


def generate_promotional_image(input_image_path, description, output_path="edited_images/generated_promo.jpg"):
    """
    Generate promotional image based on product description.
    
    Args:
        input_image_path: Path to product image
        description: Product description (e.g., "flat 20% off on gear")
        output_path: Output file path
    """
    
    print("\n" + "="*70)
    print("PARAMETRIZED PROMOTIONAL IMAGE GENERATOR")
    print("="*70 + "\n")
    
    print(f"📝 Description: {description}")
    
    # Parse description using agent
    print("🤖 Analyzing description with DescriptionBasedIconAgent...")
    content = DescriptionBasedIconAgent.parse_description(description)
    
    print(f"  ✓ Product Type: {content['product_type']}")
    print(f"  ✓ Discount: {content['discount_text']}")
    print(f"  ✓ Headline: {content['headline']}")
    print(f"  ✓ Suggested Icons: {content['suggested_icons']}\n")
    
    # Step 1: Load input image
    print("Step 1: Preparing base image...")
    if not Path(input_image_path).exists():
        print(f"  ✗ Input image not found: {input_image_path}")
        return False
    
    base_img = Image.open(input_image_path).convert("RGB")
    print(f"  ✓ Base image size: {base_img.size}\n")
    
    # Step 2: Create icons
    print("Step 2: Creating promotional icons...")
    color_scheme = content["color_scheme"]
    
    discount_badge = create_discount_badge(550, content["discount_text"], color_scheme)
    arrow_icon = create_arrow_icon(280)
    print(f"  ✓ Created discount badge (550x550)")
    print(f"  ✓ Created arrow icon (280x280)\n")
    
    # Step 3: Compose image
    print("Step 3: Composing final image...")
    result = base_img.convert("RGBA")
    
    # Paste discount badge on top-right
    badge_pos = (result.width - 650, 30)
    result.paste(discount_badge, badge_pos, discount_badge)
    print(f"  ✓ Positioned discount badge at {badge_pos}")
    
    # Paste arrow icon in middle
    arrow_pos = ((result.width - 280) // 2, result.height // 2 - 200)
    result.paste(arrow_icon, arrow_pos, arrow_icon)
    print(f"  ✓ Positioned arrow icon at {arrow_pos}\n")
    
    # Step 4: Add text overlays
    print("Step 4: Adding text overlays...")
    draw = ImageDraw.Draw(result)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", size=180)
        subtitle_font = ImageFont.truetype("arial.ttf", size=120)
        cta_font = ImageFont.truetype("arial.ttf", size=140)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        cta_font = ImageFont.load_default()
    
    # Headline
    headline = content["headline"]
    headline_bbox = draw.textbbox((0, 0), headline, font=title_font)
    headline_width = headline_bbox[2] - headline_bbox[0]
    headline_height = headline_bbox[3] - headline_bbox[1]
    headline_x = (result.width - headline_width) // 2
    headline_y = result.height // 3 - 150
    
    bg_color = color_scheme.get("background", (0, 0, 0, 180))
    bg_padding = 40
    draw.rectangle(
        [headline_x - bg_padding, headline_y - bg_padding,
         headline_x + headline_width + bg_padding, headline_y + headline_height + bg_padding],
        fill=bg_color
    )
    draw.text((headline_x, headline_y), headline, font=title_font, fill=(255, 255, 255, 255))
    print(f"  ✓ Added headline: '{headline}'")
    
    # Subheading
    subtext = content["subtext"]
    subtext_bbox = draw.textbbox((0, 0), subtext, font=subtitle_font)
    subtext_width = subtext_bbox[2] - subtext_bbox[0]
    subtext_height = subtext_bbox[3] - subtext_bbox[1]
    subtext_x = (result.width - subtext_width) // 2
    subtext_y = headline_y + 350
    
    draw.rectangle(
        [subtext_x - bg_padding, subtext_y - bg_padding,
         subtext_x + subtext_width + bg_padding, subtext_y + subtext_height + bg_padding],
        fill=bg_color
    )
    draw.text((subtext_x, subtext_y), subtext, font=subtitle_font, fill=(255, 255, 255, 255))
    print(f"  ✓ Added subtext: '{subtext}'")
    
    # CTA Button
    cta_text = content["cta"]
    cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    cta_width = cta_bbox[2] - cta_bbox[0]
    cta_height = cta_bbox[3] - cta_bbox[1]
    cta_x = (result.width - cta_width) // 2
    cta_y = subtext_y + 400
    
    # CTA button background (semi-transparent primary color)
    primary = color_scheme["primary"]
    cta_bg_padding = 50
    draw.rectangle(
        [cta_x - cta_bg_padding, cta_y - cta_bg_padding,
         cta_x + cta_width + cta_bg_padding, cta_y + cta_height + cta_bg_padding],
        fill=primary + (200,)
    )
    draw.rectangle(
        [cta_x - cta_bg_padding, cta_y - cta_bg_padding,
         cta_x + cta_width + cta_bg_padding, cta_y + cta_height + cta_bg_padding],
        outline=(255, 255, 255, 255),
        width=3
    )
    draw.text((cta_x, cta_y), cta_text, font=cta_font, fill=(255, 255, 255, 255))
    print(f"  ✓ Added CTA: '{cta_text}'\n")
    
    # Step 5: Save image
    print("Step 5: Saving image...")
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    result_rgb = result.convert("RGB")
    result_rgb.save(output_path, quality=95)
    file_size = Path(output_path).stat().st_size
    
    print("="*70)
    print("✅ PROMOTIONAL IMAGE GENERATED SUCCESSFULLY!")
    print("="*70)
    print(f"\n📸 Output Image: {output_path}")
    print(f"   Image Size: {result_rgb.size}")
    print(f"   File Size: {file_size:,} bytes")
    print(f"\n🎨 Applied Elements:")
    print(f"   - Icons: Discount Badge, Arrow")
    print(f"   - Main Text: '{headline}'")
    print(f"   - Sub Text: '{subtext}'")
    print(f"   - CTA Button: '{cta_text}'")
    print(f"   - From Description: '{description}'")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    # Example usage with different descriptions
    input_image = "temp_images/racing uite.jpg"
    
    # Test with original description
    generate_promotional_image(input_image, "flat 20% off on gear")
    
    # Uncomment to test with other descriptions:
    # generate_promotional_image(input_image, "50% discount on all electronics")
    # generate_promotional_image(input_image, "luxury collection - 30% off")
