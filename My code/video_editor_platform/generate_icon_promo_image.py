#!/usr/bin/env python
"""Generate promotional image with icons and text (no EmoG)"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_discount_badge(size=550, discount_text="20% OFF"):
    """Create a discount badge icon with prominent border and shadow"""
    badge = Image.new("RGBA", (size + 30, size + 30), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    
    # Draw shadow (dark circle offset)
    shadow_offset = 8
    draw.ellipse(
        [shadow_offset, shadow_offset, size + shadow_offset, size + shadow_offset],
        fill=(0, 0, 0, 100)
    )
    
    # Draw outer circle (navy blue)
    draw.ellipse([0, 0, size-1, size-1], fill=(25, 55, 120, 255), outline=(15, 35, 100, 255))
    
    # Draw white border (thick)
    border_width = 12
    for i in range(border_width):
        draw.ellipse(
            [i, i, size-1-i, size-1-i],
            outline=(255, 255, 255, 255)
        )
    
    # Draw inner circle (darker navy blue) - larger to contain text better
    inner_margin = 20
    draw.ellipse(
        [inner_margin, inner_margin, size-inner_margin-1, size-inner_margin-1],
        fill=(35, 75, 160, 255)
    )
    
    # Add text - reduced size to fit within circle
    try:
        font = ImageFont.truetype("arial.ttf", size=int(size*0.28), weight="bold")
    except:
        try:
            font = ImageFont.truetype("arial.ttf", size=int(size*0.28))
        except:
            font = ImageFont.load_default()
    
    # Split text into two lines
    lines = ["20%", "OFF"]
    line_height = int(size * 0.30)
    
    # Calculate vertical position to center both lines
    total_height = len(lines) * line_height
    start_y = (size - total_height) // 2 - 10
    
    # Draw each line centered
    for i, line in enumerate(lines):
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (size - text_width) // 2
        text_y = start_y + i * line_height
        
        # Draw text with white outline for extra visibility
        outline_width = 2
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                draw.text((text_x + adj_x, text_y + adj_y), line, font=font, fill=(255, 255, 255, 150))
        
        draw.text((text_x, text_y), line, font=font, fill=(255, 215, 0, 255))
    
    return badge
    
    return badge

def create_gear_icon(size=120, color=(255, 140, 0, 255)):
    """Create a gear/cogwheel icon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    center = size // 2
    outer_r = size // 2 - 5
    inner_r = size // 6
    
    # Draw outer circle
    draw.ellipse(
        [center - outer_r, center - outer_r, center + outer_r, center + outer_r],
        fill=color,
        outline=(200, 100, 0, 255)
    )
    
    # Draw inner circle (hole)
    inner_margin = 15
    draw.ellipse(
        [center - inner_r, center - inner_r, center + inner_r, center + inner_r],
        fill=(255, 255, 255, 0)
    )
    
    # Draw gear teeth (lines from center)
    num_teeth = 12
    for i in range(num_teeth):
        angle = (i * 360 / num_teeth) * 3.14159 / 180
        x1 = center + int(inner_r * 1.5 * __import__('math').cos(angle))
        y1 = center + int(inner_r * 1.5 * __import__('math').sin(angle))
        x2 = center + int(outer_r * 0.9 * __import__('math').cos(angle))
        y2 = center + int(outer_r * 0.9 * __import__('math').sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=(200, 100, 0, 255), width=3)
    
    return icon

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
        (shaft_x2, shaft_y2),  # tip
        (shaft_x2 - arrow_size // 2, shaft_y2 - arrow_size),  # left
        (shaft_x2 + arrow_size // 2, shaft_y2 - arrow_size),  # right
    ]
    draw.polygon(points, fill=color)
    
    return icon

def generate_icon_promo_image():
    """Generate promotional image with icons"""
    
    print("\n" + "="*70)
    print("ICON-BASED PROMOTIONAL IMAGE GENERATOR")
    print("="*70 + "\n")
    
    # Input parameters
    input_image = "temp_images/racing uite.jpg"
    description = "flat 20% off on gear"
    output_dir = Path("edited_images")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "generated_promo_with_icons.jpg"
    
    print(f"Description: {description}")
    print(f"Input Image: {input_image}\n")
    
    # Step 1: Create or load input image
    print("Step 1: Preparing base image...")
    if not Path(input_image).exists():
        print(f"  - Input image not found, creating sample...")
        base_img = Image.new("RGB", (1000, 800), color=(60, 80, 100))
        base_img.save(input_image)
    else:
        base_img = Image.open(input_image).convert("RGB")
    
    print(f"  ✓ Base image size: {base_img.size}\n")
    
    # Step 2: Create icons
    print("Step 2: Creating promotional icons...")
    discount_badge = create_discount_badge(550, "20% OFF")
    gear_icon = create_gear_icon(350)
    arrow_icon = create_arrow_icon(280)
    print(f"  ✓ Created discount badge (550x550)")
    print(f"  ✓ Created gear icon (350x350)")
    print(f"  ✓ Created arrow icon (280x280)\n")
    
    # Step 3: Compose image with icons
    print("Step 3: Composing final image...")
    
    # Convert to RGBA for compositing
    result = base_img.convert("RGBA")
    
    # Paste discount badge on top-right
    badge_pos = (result.width - 650, 30)
    result.paste(discount_badge, badge_pos, discount_badge)
    print(f"  ✓ Positioned discount badge at {badge_pos}")
    
    # Paste gear icon on top-left - REMOVED
    # gear_pos = (30, 30)
    # result.paste(gear_icon, gear_pos, gear_icon)
    # print(f"  ✓ Positioned gear icon at {gear_pos}")
    
    # Paste arrow icon in middle
    arrow_pos = ((result.width - 280) // 2, result.height // 2 - 200)
    result.paste(arrow_icon, arrow_pos, arrow_icon)
    print(f"  ✓ Positioned arrow icon at {arrow_pos}\n")
    
    # Step 4: Add text overlay
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
    
    # Main headline
    headline = "GET 20% OFF"
    headline_bbox = draw.textbbox((0, 0), headline, font=title_font)
    headline_width = headline_bbox[2] - headline_bbox[0]
    headline_height = headline_bbox[3] - headline_bbox[1]
    headline_x = (result.width - headline_width) // 2
    headline_y = result.height // 3 - 150
    
    # Draw semi-transparent background for headline
    bg_padding = 40
    draw.rectangle(
        [headline_x - bg_padding, headline_y - bg_padding,
         headline_x + headline_width + bg_padding, headline_y + headline_height + bg_padding],
        fill=(0, 0, 0, 180)
    )
    draw.text((headline_x, headline_y), headline, font=title_font, fill=(255, 255, 255, 255))
    
    # Subheading
    subtext = "ON ALL GEAR"
    subtext_bbox = draw.textbbox((0, 0), subtext, font=subtitle_font)
    subtext_width = subtext_bbox[2] - subtext_bbox[0]
    subtext_height = subtext_bbox[3] - subtext_bbox[1]
    subtext_x = (result.width - subtext_width) // 2
    subtext_y = headline_y + 350
    
    # Draw semi-transparent background for subtext
    draw.rectangle(
        [subtext_x - bg_padding, subtext_y - bg_padding,
         subtext_x + subtext_width + bg_padding, subtext_y + subtext_height + bg_padding],
        fill=(0, 0, 0, 180)
    )
    draw.text((subtext_x, subtext_y), subtext, font=subtitle_font, fill=(255, 220, 100, 255))
    
    # Call to action
    cta = "SHOP NOW"
    cta_bbox = draw.textbbox((0, 0), cta, font=cta_font)
    cta_width = cta_bbox[2] - cta_bbox[0]
    cta_height = cta_bbox[3] - cta_bbox[1]
    cta_x = (result.width - cta_width) // 2
    cta_y = result.height - 350
    
    # Draw CTA button background with transparency
    button_padding = 80
    draw.rectangle(
        [cta_x - button_padding, cta_y - button_padding, 
         cta_x + cta_width + button_padding, cta_y + cta_height + button_padding],
        fill=(220, 20, 60, 220),
        outline=(255, 255, 255, 255)
    )
    draw.text((cta_x, cta_y), cta, font=cta_font, fill=(255, 255, 255, 255))
    
    print(f"  ✓ Added headline: '{headline}'")
    print(f"  ✓ Added subtext: '{subtext}'")
    print(f"  ✓ Added CTA: '{cta}'\n")
    
    # Step 5: Convert back to RGB and save
    print("Step 5: Saving image...")
    result_rgb = result.convert("RGB")
    result_rgb.save(str(output_path), quality=95)
    
    # Verify
    if Path(output_path).exists():
        size = Path(output_path).stat().st_size
        print("="*70)
        print("✅ PROMOTIONAL IMAGE GENERATED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📸 Output Image: {output_path}")
        print(f"   Image Size: {result_rgb.size}")
        print(f"   File Size: {size:,} bytes")
        print(f"\n🎨 Applied Elements:")
        print(f"   - Icons: Discount Badge, Gear, Arrow")
        print(f"   - Main Text: '{headline}'")
        print(f"   - Sub Text: '{subtext}'")
        print(f"   - CTA Button: '{cta}'")
        print(f"   - From Description: '{description}'")
        print("\n" + "="*70 + "\n")
        return True
    else:
        print(f"  ✗ Failed to save image")
        return False

if __name__ == "__main__":
    success = generate_icon_promo_image()
    sys.exit(0 if success else 1)
