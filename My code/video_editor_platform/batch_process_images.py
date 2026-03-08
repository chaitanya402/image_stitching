#!/usr/bin/env python
"""
Batch AI Banner Processor - Process all images from input folder
"""

import sys
import os
from pathlib import Path
import argparse
import subprocess

def process_all_images(input_dir, output_dir, backend="sdxl-remote"):
    """Process all images in input directory"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"Error: Input directory not found: {input_path}")
        return False
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    images = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not images:
        print(f"No images found in {input_path}")
        return False
    
    print("\n" + "="*70)
    print("BATCH AI BANNER PROCESSOR")
    print("="*70 + "\n")
    print(f"Found {len(images)} images to process:")
    for img in images:
        print(f"  - {img.name}")
    print()
    
    # Process each image
    success_count = 0
    
    for idx, image_file in enumerate(images, 1):
        print("-" * 70)
        print(f"Processing {idx}/{len(images)}: {image_file.name}")
        print("-" * 70)
        
        # Generate description based on filename
        filename_lower = image_file.stem.lower()
        
        if "helmet" in filename_lower:
            description = "Premium motorcycle helmets with 25% discount available now"
        elif "jacket" in filename_lower:
            description = "Flat 20% off on all motorcycle accessories and jackets"
        elif "boot" in filename_lower:
            description = "Professional riding boots with 30% special offer"
        elif "gear" in filename_lower:
            description = "Complete motorcycle gear collection on sale"
        else:
            description = "Premium motorcycle products with special discount"
        
        # Build command
        cmd = [
            "python",
            "generate_ai_banners_preserved_image.py",
            str(image_file),
            description,
            "--backend", backend,
            "--output", str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                print(f"[OK] Successfully processed: {image_file.name}\n")
                success_count += 1
            else:
                print(f"[ERROR] Error processing: {image_file.name}")
                if result.stderr:
                    print(f"Details: {result.stderr}\n")
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] Timeout processing: {image_file.name}\n")
        except Exception as e:
            print(f"[ERROR] Error: {e}\n")
    
    # Summary
    print("\n" + "="*70)
    print("BATCH PROCESSING COMPLETE")
    print("="*70)
    print(f"\nProcessed: {success_count}/{len(images)} images")
    print(f"Output directory: {output_path}")
    
    # List output files
    output_files = list(output_path.glob("*.*"))
    if output_files:
        print(f"\nGenerated files ({len(output_files)}):")
        for f in sorted(output_files)[-10:]:  # Show last 10
            size_mb = f.stat().st_size / (1024*1024)
            print(f"  - {f.name} ({size_mb:.2f} MB)")
    
    return success_count == len(images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process all images with AI banners")
    parser.add_argument("--input", default=r"C:\Users\ASUS\Desktop\Repos\image_stitching\input images",
                       help="Input directory with images")
    parser.add_argument("--output", default=r"C:\Users\ASUS\Desktop\Repos\image_stitching\output images",
                       help="Output directory for results")
    parser.add_argument("--backend", default="sdxl-remote", 
                       help="Backend: sdxl-remote, flux-pro, or sdxl-lightning")
    
    args = parser.parse_args()
    
    success = process_all_images(args.input, args.output, args.backend)
    sys.exit(0 if success else 1)
