#!/usr/bin/env python
"""
Carousel Video Generator - Example Scripts
Demonstrates different use cases and customizations
"""

import sys
import os
from pathlib import Path

# Setup path for imports
platform_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, platform_root)

from batch_carousel_generator import create_carousel_from_descriptions
from generate_carousel_video import CarouselVideoGenerator
from generate_promo_template_system import generate_promotional_image_template


def example_1_simple_carousel():
    """Example 1: Simple carousel from descriptions"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Carousel from Descriptions")
    print("="*70 + "\n")
    
    descriptions = [
        "FLAT 25% off on winter collection",
        "Buy 2 Get 1 Free on selected items",
    ]
    
    create_carousel_from_descriptions(
        descriptions=descriptions,
        output_video_path="edited_videos/example_1_simple.mp4",
        fixed_headline="WINTER SALE",
        fixed_subtext="UP TO 25% OFF",
        fixed_cta="SHOP NOW"
    )


def example_2_custom_images():
    """Example 2: Carousel from pre-generated images"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Carousel from Pre-Generated Images")
    print("="*70 + "\n")
    
    # Generate custom promo images first
    print("Step 1: Generating custom promo images...")
    custom_promos = []
    
    descriptions = [
        "30% off on electronics and gadgets",
        "Special weekend offer - 40% discount on home decor",
        "Exclusive deal - Buy now get 50% off",
    ]
    
    Path("temp_custom_promos").mkdir(exist_ok=True)
    
    for i, desc in enumerate(descriptions):
        promo_path = f"temp_custom_promos/custom_promo_{i}.jpg"
        print(f"  Generating promo {i+1}...")
        
        generate_promotional_image_template(
            input_image_path="temp_images/car rental.jpg",
            description=desc,
            output_path=promo_path
        )
        
        custom_promos.append(promo_path)
    
    # Create carousel from custom images
    print("\nStep 2: Creating carousel from custom images...")
    gen = CarouselVideoGenerator(
        width=1920,
        height=1080,
        fps=30,
        image_duration=4
    )
    
    gen.generate_carousel_video(
        image_paths=custom_promos,
        output_path="edited_videos/example_2_custom.mp4",
        headline="MEGA YEAR-END SALE",
        subtext="EXCLUSIVE ONLINE OFFERS",
        cta="CLICK HERE",
        num_loops=1
    )
    
    # Cleanup
    for img in custom_promos:
        Path(img).unlink()
    Path("temp_custom_promos").rmdir()


def example_3_category_specific():
    """Example 3: Carousel with multiple product categories"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Multi-Category Carousel")
    print("="*70 + "\n")
    
    # Create carousel showcasing different product categories
    descriptions = [
        "30% off on sports equipment and fitness gear",
        "Flash sale - 50% off on beauty and skincare",
        "Exclusive offer - Buy 1 Get 1 on home decor",
        "Limited time - 25% off on electronics",
        "Special deal - $99 spa packages for weekend bookings",
    ]
    
    create_carousel_from_descriptions(
        descriptions=descriptions,
        output_video_path="edited_videos/example_3_multicategory.mp4",
        fixed_headline="FLASH DEALS",
        fixed_subtext="TODAY ONLY",
        fixed_cta="GRAB NOW",
        base_image="temp_images/car rental.jpg"
    )


def example_4_longer_duration():
    """Example 4: Carousel with longer image duration"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Extended Duration Carousel")
    print("="*70 + "\n")
    
    # Create carousel with longer display time per image (6 seconds)
    print("Creating carousel with 6 seconds per image...\n")
    
    descriptions = [
        "Our premium collection - 40% off today",
        "Limited stock available - up to 60% discount",
    ]
    
    # Generate temp promos
    temp_promos = []
    Path("temp_extended").mkdir(exist_ok=True)
    
    for i, desc in enumerate(descriptions):
        promo_path = f"temp_extended/promo_{i}.jpg"
        generate_promotional_image_template(
            input_image_path="temp_images/car rental.jpg",
            description=desc,
            output_path=promo_path
        )
        temp_promos.append(promo_path)
    
    # Create carousel with extended duration
    gen = CarouselVideoGenerator(
        width=1920,
        height=1080,
        fps=30,
        image_duration=6  # 6 seconds instead of default 4
    )
    
    gen.generate_carousel_video(
        image_paths=temp_promos,
        output_path="edited_videos/example_4_extended.mp4",
        headline="PREMIUM COLLECTION",
        subtext="EXCLUSIVE MEMBER PRICING",
        cta="VIEW COLLECTION",
        num_loops=1
    )
    
    # Cleanup
    for img in temp_promos:
        Path(img).unlink()
    Path("temp_extended").rmdir()


def example_5_no_text_overlay():
    """Example 5: Carousel with minimal text (using template text only)"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Carousel with Template Text Only")
    print("="*70 + "\n")
    
    descriptions = [
        "20% off on fashion",
        "Buy 1 Get 1 on accessories",
        "30% off on footwear",
    ]
    
    # Create carousel with minimal fixed overlay
    create_carousel_from_descriptions(
        descriptions=descriptions,
        output_video_path="edited_videos/example_5_template_only.mp4",
        fixed_headline="",      # Empty - use generated text
        fixed_subtext="",       # Empty - use generated text
        fixed_cta="",           # Empty - use generated text
        base_image="temp_images/car rental.jpg"
    )


def example_6_high_fps():
    """Example 6: High frame rate carousel (60fps for smooth video)"""
    print("\n" + "="*70)
    print("EXAMPLE 6: High FPS Carousel (60fps)")
    print("="*70 + "\n")
    
    print("Creating smooth 60fps carousel...\n")
    
    descriptions = [
        "Smooth transitions at 60fps",
        "Professional quality video",
    ]
    
    # Generate temp promos
    temp_promos = []
    Path("temp_60fps").mkdir(exist_ok=True)
    
    for i, desc in enumerate(descriptions):
        promo_path = f"temp_60fps/promo_{i}.jpg"
        generate_promotional_image_template(
            input_image_path="temp_images/car rental.jpg",
            description=desc,
            output_path=promo_path
        )
        temp_promos.append(promo_path)
    
    # Create high-fps carousel
    gen = CarouselVideoGenerator(
        width=1920,
        height=1080,
        fps=60,  # High frame rate
        image_duration=4
    )
    
    gen.generate_carousel_video(
        image_paths=temp_promos,
        output_path="edited_videos/example_6_60fps.mp4",
        headline="PREMIUM VIDEO",
        subtext="60 FPS SMOOTH",
        cta="EXPERIENCE IT",
        num_loops=1
    )
    
    # Cleanup
    for img in temp_promos:
        Path(img).unlink()
    Path("temp_60fps").rmdir()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Carousel Video Examples")
    parser.add_argument("--example", type=int, choices=[1, 2, 3, 4, 5, 6],
                       help="Run specific example (1-6)")
    parser.add_argument("--all", action="store_true", help="Run all examples")
    
    args = parser.parse_args()
    
    examples = {
        1: example_1_simple_carousel,
        2: example_2_custom_images,
        3: example_3_category_specific,
        4: example_4_longer_duration,
        5: example_5_no_text_overlay,
        6: example_6_high_fps,
    }
    
    if args.all:
        for i, func in examples.items():
            try:
                func()
            except Exception as e:
                print(f"\n[ERROR] Example {i} failed: {e}")
    elif args.example:
        try:
            examples[args.example]()
        except Exception as e:
            print(f"\n[ERROR] Example {args.example} failed: {e}")
    else:
        print("\n" + "="*70)
        print("CAROUSEL VIDEO GENERATOR - EXAMPLES")
        print("="*70)
        print("\nUsage:")
        print("  python carousel_examples.py --example <1-6>   # Run specific example")
        print("  python carousel_examples.py --all              # Run all examples")
        print("\nAvailable Examples:")
        print("  1. Simple carousel from descriptions")
        print("  2. Carousel from pre-generated images")
        print("  3. Multi-category carousel")
        print("  4. Extended duration carousel (6s per image)")
        print("  5. Template text only carousel")
        print("  6. High FPS carousel (60fps)")
        print("\nOutput videos will be saved to: edited_videos/")
        print("="*70 + "\n")
        
        # Run example 1 by default if no args
        print("Running Example 1...\n")
        example_1_simple_carousel()
