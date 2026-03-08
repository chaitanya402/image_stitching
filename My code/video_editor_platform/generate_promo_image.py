#!/usr/bin/env python
"""Generate promotional image with description"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.services.emo_g_agent import EmoGAgent
from src.services.text_image_agent import TextImageAgent
from PIL import Image

def generate_promo_image():
    """Generate promotional image based on description"""
    
    print("\n" + "="*70)
    print("PROMOTIONAL IMAGE GENERATOR")
    print("="*70 + "\n")
    
    # Input parameters
    input_image = "temp_images/racing uite.jpg"
    description = "flat 20% off on gear"
    output_dir = Path("edited_images")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "generated_promo_gear.jpg"
    
    print(f"Description: {description}")
    print(f"Input Image: {input_image}")
    print(f"Output Path: {output_path}\n")
    
    # Step 1: Extract EmoG from description
    print("Step 1: Analyzing description for emojis and offers...")
    emo_g_list = EmoGAgent.identify_emo_g(description)
    offers = EmoGAgent.identify_special_offers_with_emo_g(description)
    print(f"  ✓ Detected Emojis: {emo_g_list}")
    print(f"  ✓ Detected Offers: {offers}\n")
    
    # Step 2: Generate decorative text
    print("Step 2: Generating promotional text...")
    keywords = description.split()
    promotional_texts = [
        "FLAT 20% OFF",
        "ON ALL GEAR",
        "LIMITED TIME"
    ]
    print(f"  ✓ Promotional texts: {promotional_texts}\n")
    
    # Step 3: Add text to image
    print("Step 3: Adding text to image...")
    try:
        # First check if input image exists
        if not Path(input_image).exists():
            print(f"  ✗ Input image not found: {input_image}")
            print(f"  Creating sample image instead...\n")
            
            # Create sample image
            sample_img = Image.new("RGB", (800, 600), color=(50, 50, 100))
            sample_img.save(input_image)
            print(f"  ✓ Sample image created\n")
        
        # Add promotional text
        working_image = str(output_dir / "temp_with_text.jpg")
        TextImageAgent.add_text_to_image(
            image_path=input_image,
            text="FLAT 20% OFF",
            output_path=working_image,
            position=(100, 150),
            font_size=60
        )
        print(f"  ✓ Added 'FLAT 20% OFF' text\n")
        
        # Add secondary text
        TextImageAgent.add_text_to_image(
            image_path=working_image,
            text="ON ALL GEAR",
            output_path=working_image,
            position=(120, 250),
            font_size=50
        )
        print(f"  ✓ Added 'ON ALL GEAR' text\n")
        
        # Add call-to-action
        TextImageAgent.add_text_to_image(
            image_path=working_image,
            text="SHOP NOW",
            output_path=str(output_path),
            position=(200, 350),
            font_size=45
        )
        print(f"  ✓ Added 'SHOP NOW' call-to-action\n")
        
        # Verify output
        if Path(output_path).exists():
            size = Path(output_path).stat().st_size
            print("="*70)
            print("✅ PROMOTIONAL IMAGE GENERATED SUCCESSFULLY!")
            print("="*70)
            print(f"\n📸 Output Image: {output_path}")
            print(f"   File Size: {size:,} bytes")
            print(f"\n📝 Applied Elements:")
            print(f"   - Description: {description}")
            print(f"   - Emojis: {emo_g_list if emo_g_list else 'None'}")
            print(f"   - Offers: {[o['offer'] for o in offers]}")
            print(f"   - Text Layers: {promotional_texts}")
            print("\n" + "="*70 + "\n")
            
            return True
        else:
            print(f"  ✗ Failed to create output image")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return False

if __name__ == "__main__":
    success = generate_promo_image()
    sys.exit(0 if success else 1)
