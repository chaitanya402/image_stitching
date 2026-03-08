"""Icon generator functions for promotional images - offer-specific icons."""

from PIL import Image, ImageDraw
import math


def create_shopping_bag_icon(size=150, color=(25, 55, 120, 255)):
    """Create a shopping bag icon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Bag body
    bag_top = int(size * 0.25)
    bag_bottom = int(size * 0.85)
    bag_left = int(size * 0.2)
    bag_right = int(size * 0.8)
    
    # Draw rounded rectangle for bag
    draw.rectangle(
        [bag_left, bag_top, bag_right, bag_bottom],
        fill=color,
        outline=color
    )
    
    # Handle
    handle_top = int(size * 0.15)
    handle_mid = int(size * 0.5)
    handle_left = int(size * 0.35)
    handle_right = int(size * 0.65)
    
    draw.arc(
        [handle_left, handle_top, handle_right, handle_mid],
        0, 180,
        fill=color,
        width=int(size * 0.08)
    )
    
    return icon


def create_gift_box_icon(size=150, color=(25, 55, 120, 255)):
    """Create a gift box icon with ribbon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Box
    box_margin = int(size * 0.15)
    draw.rectangle(
        [box_margin, box_margin, size - box_margin, size - box_margin],
        fill=color,
        outline=color,
        width=2
    )
    
    # Ribbon horizontal
    ribbon_y = int(size * 0.5)
    draw.line(
        [(box_margin, ribbon_y), (size - box_margin, ribbon_y)],
        fill=(255, 215, 0, 255),
        width=int(size * 0.1)
    )
    
    # Ribbon vertical
    ribbon_x = int(size * 0.5)
    draw.line(
        [(ribbon_x, box_margin), (ribbon_x, size - box_margin)],
        fill=(255, 215, 0, 255),
        width=int(size * 0.1)
    )
    
    # Bow
    bow_size = int(size * 0.12)
    bow_y = int(size * 0.4)
    draw.ellipse(
        [ribbon_x - bow_size, bow_y, ribbon_x + bow_size, bow_y + bow_size],
        fill=(255, 215, 0, 255)
    )
    
    return icon


def create_megaphone_icon(size=150, color=(25, 55, 120, 255)):
    """Create a megaphone/promotion icon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Horn (trapezoid)
    horn_left = int(size * 0.6)
    horn_right = int(size * 0.95)
    horn_top = int(size * 0.25)
    horn_bottom = int(size * 0.75)
    
    points = [
        (horn_left, int(size * 0.35)),
        (horn_left, int(size * 0.65)),
        (horn_right, horn_bottom),
        (horn_right, horn_top),
    ]
    draw.polygon(points, fill=color, outline=color)
    
    # Handle/grip
    grip_x = int(size * 0.45)
    grip_top = int(size * 0.3)
    grip_bottom = int(size * 0.7)
    
    draw.rectangle(
        [grip_x - int(size * 0.08), grip_top, grip_x + int(size * 0.08), grip_bottom],
        fill=color,
        outline=color
    )
    
    # Speaker circle
    speaker_r = int(size * 0.12)
    speaker_x = int(size * 0.35)
    speaker_y = int(size * 0.5)
    
    draw.ellipse(
        [speaker_x - speaker_r, speaker_y - speaker_r, speaker_x + speaker_r, speaker_y + speaker_r],
        fill=color,
        outline=color,
        width=2
    )
    
    return icon


def create_star_icon(size=150, color=(25, 55, 120, 255)):
    """Create a star icon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    center_x = size // 2
    center_y = size // 2
    outer_r = size // 2 - 10
    inner_r = int(outer_r * 0.4)
    
    points = []
    for i in range(10):
        angle = (i * 36 - 90) * 3.14159 / 180
        if i % 2 == 0:
            r = outer_r
        else:
            r = inner_r
        x = center_x + int(r * math.cos(angle))
        y = center_y + int(r * math.sin(angle))
        points.append((x, y))
    
    draw.polygon(points, fill=color, outline=color)
    
    return icon


def create_percent_icon(size=150, color=(25, 55, 120, 255)):
    """Create a percent sign icon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    stroke_width = int(size * 0.08)
    
    # Top circle
    circle_r = int(size * 0.12)
    top_y = int(size * 0.25)
    draw.ellipse(
        [int(size * 0.2) - circle_r, top_y - circle_r, 
         int(size * 0.2) + circle_r, top_y + circle_r],
        outline=color,
        width=stroke_width
    )
    
    # Bottom circle
    bottom_y = int(size * 0.75)
    draw.ellipse(
        [int(size * 0.8) - circle_r, bottom_y - circle_r,
         int(size * 0.8) + circle_r, bottom_y + circle_r],
        outline=color,
        width=stroke_width
    )
    
    # Diagonal line
    draw.line(
        [(int(size * 0.35), int(size * 0.2)), (int(size * 0.65), int(size * 0.8))],
        fill=color,
        width=stroke_width
    )
    
    return icon


def create_plus_icon(size=150, color=(25, 55, 120, 255)):
    """Create a plus/add icon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    center_x = size // 2
    center_y = size // 2
    line_width = int(size * 0.15)
    line_length = int(size * 0.5)
    
    # Horizontal line
    draw.line(
        [(center_x - line_length, center_y), (center_x + line_length, center_y)],
        fill=color,
        width=line_width
    )
    
    # Vertical line
    draw.line(
        [(center_x, center_y - line_length), (center_x, center_y + line_length)],
        fill=color,
        width=line_width
    )
    
    return icon


def create_crown_icon(size=150, color=(25, 55, 120, 255)):
    """Create a crown/luxury icon"""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Base
    base_y = int(size * 0.7)
    base_left = int(size * 0.2)
    base_right = int(size * 0.8)
    
    draw.rectangle(
        [base_left, base_y, base_right, size - int(size * 0.1)],
        fill=color,
        outline=color
    )
    
    # Crown peaks
    peak_height = int(size * 0.3)
    peak_y = base_y - peak_height
    
    # Create crown peaks
    center_x = size // 2
    peak_size = int(size * 0.15)
    
    # Left peak
    left_peak = [
        (int(size * 0.3), base_y),
        (int(size * 0.25), peak_y),
        (int(size * 0.4), peak_y + int(size * 0.15))
    ]
    draw.polygon(left_peak, fill=color, outline=color)
    
    # Center peak (tallest)
    center_peak = [
        (center_x - peak_size, base_y),
        (center_x, peak_y - int(size * 0.1)),
        (center_x + peak_size, base_y)
    ]
    draw.polygon(center_peak, fill=color, outline=color)
    
    # Right peak
    right_peak = [
        (int(size * 0.7), base_y),
        (int(size * 0.6), peak_y + int(size * 0.15)),
        (int(size * 0.75), peak_y)
    ]
    draw.polygon(right_peak, fill=color, outline=color)
    
    # Add gems
    gem_color = (255, 215, 0, 255)
    gem_positions = [
        (int(size * 0.3), int(size * 0.5)),
        (center_x, int(size * 0.4)),
        (int(size * 0.7), int(size * 0.5))
    ]
    
    for gx, gy in gem_positions:
        draw.ellipse(
            [gx - int(size * 0.05), gy - int(size * 0.05),
             gx + int(size * 0.05), gy + int(size * 0.05)],
            fill=gem_color
        )
    
    return icon
