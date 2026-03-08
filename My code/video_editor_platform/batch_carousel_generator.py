#!/usr/bin/env python
"""
Batch Carousel Video Generator - Creates carousel videos from multiple promo images.
Generates promo images from descriptions, then combines them into carousel video.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple

# Setup path for imports
platform_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, platform_root)

from generate_promo_template_system import generate_promotional_image_template
from generate_carousel_video import CarouselVideoGenerator


def create_carousel_from_descriptions(descriptions: List[str], 
                                     output_video_path: str,
                                     fixed_headline: str = "",
                                     fixed_subtext: str = "",
                                     fixed_cta: str = "",
                                     base_image: str = "temp_images/car rental.jpg"):
    """
    Generate carousel video from product descriptions.
    
    Args:
        descriptions: List of product descriptions
        output_video_path: Path for output MP4 video
        fixed_headline: Fixed text for all frames (optional)
        fixed_subtext: Fixed text for all frames (optional)
        fixed_cta: Fixed CTA text for all frames (optional)
        base_image: Base product image to use
    """
    
    print("\n" + "="*70)
    print("BATCH CAROUSEL VIDEO GENERATOR")
    print("="*70 + "\n")
    
    print(f"Input Descriptions: {len(descriptions)}")
    for i, desc in enumerate(descriptions, 1):
        print(f"   {i}. {desc[:60]}...")
    print()
    
    # Ensure temp directories exist
    Path("temp_promo_carousel").mkdir(exist_ok=True)
    Path(output_video_path).parent.mkdir(exist_ok=True)
    
    # Step 1: Generate promo images from descriptions
    print("Step 1: Generating promotional images from descriptions...\n")
    
    promo_images = []
    for i, description in enumerate(descriptions):
        promo_path = f"temp_promo_carousel/promo_{i:03d}.jpg"
        
        print(f"  Generating promo {i+1}/{len(descriptions)}...")
        success = generate_promotional_image_template(
            input_image_path=base_image,
            description=description,
            output_path=promo_path
        )
        
        if success:
            promo_images.append(promo_path)
            print(f"  [OK] Generated: {promo_path}\n")
        else:
            print(f"  [FAIL] Failed to generate: {promo_path}\n")
    
    if not promo_images:
        print("[ERROR] No promotional images generated!")
        return False
    
    print(f"\n[SUCCESS] Generated {len(promo_images)} promotional images\n")
    
    # Step 2: Create carousel video
    print("Step 2: Creating carousel video with sliding transitions...\n")
    
    # Resize carousel to 1080p
    carousel_gen = CarouselVideoGenerator(width=1920, height=1080, fps=30, image_duration=4)
    
    success = carousel_gen.generate_carousel_video(
        image_paths=promo_images,
        output_path=output_video_path,
        headline=fixed_headline,
        subtext=fixed_subtext,
        cta=fixed_cta,
        num_loops=1  # One complete pass through all images
    )
    
    if success:
        print("[SUCCESS] Carousel video created successfully!")
        print(f"\nVideo saved to: {output_video_path}")
        
        # Cleanup temp files
        print("\nCleaning up temporary files...")
        for img in promo_images:
            try:
                Path(img).unlink()
            except:
                pass
        Path("temp_promo_carousel").rmdir()
        print("[OK] Cleanup complete")
        
        return True
    else:
        print("[FAIL] Failed to create carousel video")
        return False


if __name__ == "__main__":
    # Example usage with different product types
    product_descriptions = [
        "FLAT 20% off on all clothing and apparel",
        "Buy one get one free on all sports gear",
        "30% discount on electronics this week only",
        "50% off on first booking , car rentals",
    ]
    
    print("\n" + "="*70)
    print("CREATING CAROUSEL VIDEO FROM MULTIPLE PRODUCTS")
    print("="*70 + "\n")
    
    create_carousel_from_descriptions(
        descriptions=product_descriptions,
        output_video_path="edited_videos/carousel_from_descriptions.mp4",
        fixed_headline="MEGA SALE EVENT",
        fixed_subtext="LIMITED TIME OFFERS",
        fixed_cta="SHOP NOW",
        base_image="temp_images/car rental.jpg"
    )
