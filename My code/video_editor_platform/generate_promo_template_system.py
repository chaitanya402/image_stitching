#!/usr/bin/env python
"""
Template-based promotional image generator with offer-specific icons.
Uses DescriptionBasedIconAgent to select templates and icons.
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Setup path for imports
platform_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, platform_root)

from src.services.description_based_icon_agent import DescriptionBasedIconAgent
from src.utils.icon_factory import (
    create_shopping_bag_icon,
    create_gift_box_icon,
    create_megaphone_icon,
    create_star_icon,
    create_percent_icon,
    create_plus_icon,
    create_crown_icon
)


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


def get_offer_icon(icon_name: str, size: int, color) -> Image.Image:
    """Get icon image based on icon name."""
    icon_factory = {
        "badge": lambda: create_discount_badge(size, "OFFER", {"primary": color, "accent": (255, 215, 0)}),
        "shopping_bag": lambda: create_shopping_bag_icon(size, color),
        "gift_box": lambda: create_gift_box_icon(size, color),
        "megaphone": lambda: create_megaphone_icon(size, color),
        "star": lambda: create_star_icon(size, color),
        "percent": lambda: create_percent_icon(size, color),
        "plus": lambda: create_plus_icon(size, color),
        "crown": lambda: create_crown_icon(size, color),
    }
    
    factory_func = icon_factory.get(icon_name)
    if factory_func:
        try:
            return factory_func()
        except:
            pass
    
    # Fallback - return a simple colored circle
    fallback = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(fallback)
    draw.ellipse([0, 0, size-1, size-1], fill=color)
    return fallback


def apply_template_badge_top_right(base_img, badge, icons_list, color_scheme):
    """Template: Badge top-right, NO secondary icons (keep text area clean)"""
    result = base_img.convert("RGBA")
    
    # Paste discount badge on top-right only
    badge_pos = (result.width - 650, 30)
    result.paste(badge, badge_pos, badge)
    
    # Don't paste secondary icons to avoid overlapping with text
    return result, [(result.width - 650, 30)]


def apply_template_badge_center(base_img, badge, icons_list, color_scheme):
    """Template: Large badge centered (for luxury/minimal products)"""
    result = base_img.convert("RGBA")
    
    # Paste badge in center
    badge_pos = ((result.width - 580) // 2, (result.height - 580) // 2)
    result.paste(badge, badge_pos, badge)
    
    return result, [badge_pos]


def apply_template_badge_left_side(base_img, badge, icons_list, color_scheme):
    """Template: Badge left side (for comparison/buy1get1)"""
    result = base_img.convert("RGBA")
    
    # Paste badge on left
    badge_pos = (50, 100)
    result.paste(badge, badge_pos, badge)
    
    # Paste secondary icon on right if available
    if icons_list and len(icons_list) > 0:
        secondary_icon = icons_list[0]
        icon_pos = (result.width - 350, 150)
        result.paste(secondary_icon, icon_pos, secondary_icon)
    
    return result, [badge_pos]


def apply_template_stacked(base_img, badge, icons_list, color_scheme):
    """Template: Badge on top, secondary icons stacked below"""
    result = base_img.convert("RGBA")
    
    # Paste badge at top center
    badge_pos = ((result.width - 580) // 2, 50)
    result.paste(badge, badge_pos, badge)
    
    # Paste secondary icons below in a row
    if icons_list:
        icon_size = 200
        y_pos = badge_pos[1] + 600
        num_icons = len(icons_list)
        total_width = num_icons * icon_size
        start_x = (result.width - total_width) // 2
        
        for i, icon in enumerate(icons_list):
            x_pos = start_x + i * icon_size
            resized = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            result.paste(resized, (x_pos, y_pos), resized)
    
    return result, [badge_pos]


def generate_promotional_image_template(input_image_path, description, output_path="edited_images/generated_promo.jpg"):
    """
    Generate promotional image based on template system and offer-specific icons.
    
    Args:
        input_image_path: Path to product image
        description: Product description
        output_path: Output file path
    """
    
    print("\n" + "="*70)
    print("TEMPLATE-BASED PROMOTIONAL IMAGE GENERATOR")
    print("="*70 + "\n")
    
    print(f"📝 Description: {description}")
    
    # Parse description using agent
    print("🤖 Analyzing with DescriptionBasedIconAgent...")
    content = DescriptionBasedIconAgent.parse_description(description)
    
    print(f"  ✓ Product Type: {content['product_type']}")
    print(f"  ✓ Offer Type: {content['offer_type']}")
    print(f"  ✓ Template: {content['template']}")
    print(f"  ✓ Icons: {content['suggested_icons']}\n")
    
    # Load base image
    print("Step 1: Preparing base image...")
    if not Path(input_image_path).exists():
        print(f"  ✗ Input image not found: {input_image_path}")
        return False
    
    base_img = Image.open(input_image_path).convert("RGB")
    
    # Enhance image quality - use high-quality resampling
    # Apply slight sharpening to prevent blurriness from upscaling
    from PIL import ImageEnhance, ImageFilter
    
    # Enhance contrast and color vibrancy
    enhancer = ImageEnhance.Contrast(base_img)
    base_img = enhancer.enhance(1.15)  # +15% contrast
    
    enhancer = ImageEnhance.Color(base_img)
    base_img = enhancer.enhance(1.10)  # +10% color saturation
    
    enhancer = ImageEnhance.Sharpness(base_img)
    base_img = enhancer.enhance(1.3)  # +30% sharpness
    
    print(f"  ✓ Base image size: {base_img.size}")
    print(f"  ✓ Applied quality enhancement (contrast, color, sharpness)\n")
    
    # Create icons
    print("Step 2: Creating offer-specific icons...")
    color_scheme = content["color_scheme"]
    primary_color = color_scheme["primary"]
    
    # Main badge
    discount_badge = create_discount_badge(550, content["discount_text"], color_scheme)
    print(f"  ✓ Created discount badge (550x550)")
    
    # Secondary icons based on offer type
    secondary_icons = []
    for icon_name in content["suggested_icons"][1:]:  # Skip first (badge)
        if icon_name != "badge":
            try:
                icon = get_offer_icon(icon_name, 280, primary_color + (255,))
                secondary_icons.append(icon)
                print(f"  ✓ Created {icon_name} icon (280x280)")
            except Exception as e:
                print(f"  - Skipped {icon_name}: {str(e)}")
    print()
    
    # Apply template
    print("Step 3: Applying template layout...")
    template_name = content["template"]
    
    template_map = {
        "badge_top_right": apply_template_badge_top_right,
        "badge_center": apply_template_badge_center,
        "badge_left_side": apply_template_badge_left_side,
        "stacked": apply_template_stacked,
    }
    
    apply_template = template_map.get(template_name, apply_template_badge_top_right)
    result, badge_positions = apply_template(base_img, discount_badge, secondary_icons, color_scheme)
    print(f"  ✓ Applied template: {template_name}\n")
    
    # Add text overlays
    print("Step 4: Adding text overlays...")
    draw = ImageDraw.Draw(result)
    
    try:
        # Use bold variants for better visibility
        title_font = ImageFont.truetype("arial.ttf", size=180, weight="bold")
        subtitle_font = ImageFont.truetype("arial.ttf", size=120)
        cta_font = ImageFont.truetype("arial.ttf", size=140, weight="bold")
    except:
        try:
            title_font = ImageFont.truetype("arial.ttf", size=180)
            subtitle_font = ImageFont.truetype("arial.ttf", size=120)
            cta_font = ImageFont.truetype("arial.ttf", size=140)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            cta_font = ImageFont.load_default()
    
    # Headline with improved text rendering
    headline = content["headline"]
    headline_bbox = draw.textbbox((0, 0), headline, font=title_font)
    headline_width = headline_bbox[2] - headline_bbox[0]
    headline_height = headline_bbox[3] - headline_bbox[1]
    headline_x = (result.width - headline_width) // 2
    headline_y = result.height // 3 + 50  # Moved down to avoid badge overlap
    
    bg_color = color_scheme.get("background", (0, 0, 0, 200))
    bg_padding = 40
    
    # Draw background with slight shadow for depth
    draw.rectangle(
        [headline_x - bg_padding - 3, headline_y - bg_padding - 3,
         headline_x + headline_width + bg_padding + 3, headline_y + headline_height + bg_padding + 3],
        fill=(0, 0, 0, 100)  # Shadow
    )
    draw.rectangle(
        [headline_x - bg_padding, headline_y - bg_padding,
         headline_x + headline_width + bg_padding, headline_y + headline_height + bg_padding],
        fill=bg_color
    )
    
    # Draw text with outline for better visibility
    outline_range = 3
    for adj_x in range(-outline_range, outline_range + 1):
        for adj_y in range(-outline_range, outline_range + 1):
            if adj_x != 0 or adj_y != 0:
                draw.text((headline_x + adj_x, headline_y + adj_y), headline, font=title_font, fill=(0, 0, 0, 150))
    draw.text((headline_x, headline_y), headline, font=title_font, fill=(255, 255, 255, 255))
    print(f"  ✓ Added headline: '{headline}'")
    
    # Subheading with improved rendering
    subtext = content["subtext"]
    subtext_bbox = draw.textbbox((0, 0), subtext, font=subtitle_font)
    subtext_width = subtext_bbox[2] - subtext_bbox[0]
    subtext_height = subtext_bbox[3] - subtext_bbox[1]
    subtext_x = (result.width - subtext_width) // 2
    subtext_y = headline_y + 350
    
    # Draw background with shadow
    draw.rectangle(
        [subtext_x - bg_padding - 3, subtext_y - bg_padding - 3,
         subtext_x + subtext_width + bg_padding + 3, subtext_y + subtext_height + bg_padding + 3],
        fill=(0, 0, 0, 100)
    )
    draw.rectangle(
        [subtext_x - bg_padding, subtext_y - bg_padding,
         subtext_x + subtext_width + bg_padding, subtext_y + subtext_height + bg_padding],
        fill=bg_color
    )
    
    # Draw text with outline
    for adj_x in range(-outline_range, outline_range + 1):
        for adj_y in range(-outline_range, outline_range + 1):
            if adj_x != 0 or adj_y != 0:
                draw.text((subtext_x + adj_x, subtext_y + adj_y), subtext, font=subtitle_font, fill=(0, 0, 0, 150))
    draw.text((subtext_x, subtext_y), subtext, font=subtitle_font, fill=(255, 255, 255, 255))
    print(f"  ✓ Added subtext: '{subtext}'")
    
    # CTA Button - positioned higher up from bottom
    cta_text = content["cta"]
    cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    cta_width = cta_bbox[2] - cta_bbox[0]
    cta_height = cta_bbox[3] - cta_bbox[1]
    cta_x = (result.width - cta_width) // 2
    cta_y = result.height - 250  # Moved higher
    
    # CTA button background - use primary color (red for automotive)
    primary = color_scheme["primary"]
    cta_bg_padding = 40
    draw.rectangle(
        [cta_x - cta_bg_padding, cta_y - cta_bg_padding,
         cta_x + cta_width + cta_bg_padding, cta_y + cta_height + cta_bg_padding],
        fill=primary + (220,)  # Use primary color with transparency
    )
    draw.rectangle(
        [cta_x - cta_bg_padding, cta_y - cta_bg_padding,
         cta_x + cta_width + cta_bg_padding, cta_y + cta_height + cta_bg_padding],
        outline=(255, 255, 255, 255),
        width=3
    )
    draw.text((cta_x, cta_y), cta_text, font=cta_font, fill=(255, 255, 255, 255))
    print(f"  ✓ Added CTA: '{cta_text}'\n")
    
    # Save image
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
    print(f"   - Template: {template_name}")
    print(f"   - Icons: {', '.join(content['suggested_icons'])}")
    print(f"   - Main Text: '{headline}'")
    print(f"   - Sub Text: '{subtext}'")
    print(f"   - CTA Button: '{cta_text}'")
    print(f"   - From Description: '{description}'")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    input_image = "temp_images/racing uite.jpg"
    
    # Test different offers
    descriptions = [
        "flat 20% off on gear",  # discount
        "buy 1 get 1 on luxury home decor",  # buy1get1
        "promotion - 50% off on all electronics",  # promotion
    ]
    
    for i, desc in enumerate(descriptions):
        generate_promotional_image_template(
            input_image,
            desc,
            f"edited_images/template_demo_{i}.jpg"
        )
