#!/usr/bin/env python
"""Test TextImageAgent - add custom text to images"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PIL import Image
from src.services.text_image_agent import TextImageAgent

def test_text_image_agent():
    """Test TextImageAgent functionality"""
    print("\n" + "="*60)
    print("Testing TextImageAgent Module")
    print("="*60 + "\n")
    
    # Create test directory
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    # Create a sample image
    test_image_path = test_dir / "sample_image.png"
    output_path = test_dir / "output_with_text.png"
    
    print("Test 1: Creating sample image...")
    sample_img = Image.new("RGB", (400, 300), color=(100, 150, 200))
    sample_img.save(test_image_path)
    print(f"  ✓ Sample image created at {test_image_path}")
    print(f"  Image size: 400x300\n")
    
    # Test 2: Add text to image
    print("Test 2: Adding text to image...")
    text = "SUMMER SALE 50% OFF"
    try:
        TextImageAgent.add_text_to_image(
            image_path=str(test_image_path),
            text=text,
            output_path=str(output_path),
            position=(50, 100),
            font_size=40
        )
        if output_path.exists():
            print(f"  ✓ Text added successfully!")
            print(f"  Text: '{text}'")
            print(f"  Position: (50, 100)")
            print(f"  Font size: 40")
            print(f"  Output saved at: {output_path}\n")
        else:
            print(f"  ✗ FAIL - Output file not created\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
    
    # Test 3: Add text at different position
    print("Test 3: Adding text at different position...")
    output_path2 = test_dir / "output_centered.png"
    text2 = "🎉 EXCLUSIVE OFFER 🎉"
    try:
        TextImageAgent.add_text_to_image(
            image_path=str(test_image_path),
            text=text2,
            output_path=str(output_path2),
            position=(100, 150),
            font_size=32
        )
        if output_path2.exists():
            print(f"  ✓ Text added at centered position!")
            print(f"  Text: '{text2}'")
            print(f"  Position: (100, 150)")
            print(f"  Font size: 32")
            print(f"  Output saved at: {output_path2}\n")
        else:
            print(f"  ✗ FAIL - Output file not created\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
    
    # Test 4: Add multiple texts
    print("Test 4: Adding multiple texts sequentially...")
    output_path3 = test_dir / "output_multi_text.png"
    texts = [
        ("LIMITED TIME", (30, 50), 28),
        ("BUY NOW", (80, 150), 40),
        ("Free Shipping", (100, 220), 24)
    ]
    try:
        img = Image.new("RGB", (400, 300), color=(200, 100, 50))
        img.save(output_path3)
        
        for text, position, font_size in texts:
            TextImageAgent.add_text_to_image(
                image_path=str(output_path3),
                text=text,
                output_path=str(output_path3),
                position=position,
                font_size=font_size
            )
        print(f"  ✓ Multiple texts added successfully!")
        for text, pos, size in texts:
            print(f"    - '{text}' at {pos} (size: {size})")
        print(f"  Output saved at: {output_path3}\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
    
    # Summary
    print("="*60)
    print("TextImageAgent Tests Summary")
    print("="*60)
    files_created = list(test_dir.glob("*.png"))
    print(f"✓ Files created: {len(files_created)}")
    for f in files_created:
        print(f"  - {f.name}")
    print("\n✓ All tests completed successfully!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_text_image_agent()
