#!/usr/bin/env python
"""
Direct Carousel Video Generator - Create video from input images
No intermediate processing needed - uses images as-is
"""

import sys
import os
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

def create_carousel_video_from_inputs(
    input_dir,
    output_path="carousel_output.mp4",
    image_duration=4,
    fps=30,
    resolution=(1920, 1080),
    loop_count=2
):
    """
    Create carousel video directly from input images
    
    Args:
        input_dir: Directory containing input images
        output_path: Output MP4 file path
        image_duration: Seconds to display each image
        fps: Frames per second
        resolution: Video resolution (width, height)
        loop_count: How many times to loop through all images
    """
    
    input_path = Path(input_dir)
    output_path = Path(output_path)
    
    print("\n" + "="*70)
    print("CAROUSEL VIDEO GENERATOR - INPUT IMAGES")
    print("="*70 + "\n")
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    image_files = sorted([
        f for f in input_path.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ])
    
    if not image_files:
        print(f"[ERROR] No images found in {input_path}")
        return False
    
    print(f"Found {len(image_files)} images:")
    for img in image_files:
        print(f"  - {img.name}")
    print()
    
    # Load and prepare images
    print("Loading and preparing images...")
    images = []
    
    for img_file in image_files:
        try:
            img = cv2.imread(str(img_file))
            if img is None:
                print(f"  [SKIP] Failed to load: {img_file.name}")
                continue
            
            # Resize to fit video dimensions while maintaining aspect ratio
            h, w = img.shape[:2]
            scale = min(resolution[0] / w, resolution[1] / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Resize
            img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            # Create canvas with white background
            canvas = np.ones((resolution[1], resolution[0], 3), dtype=np.uint8) * 255
            
            # Center image on canvas
            x_offset = (resolution[0] - new_w) // 2
            y_offset = (resolution[1] - new_h) // 2
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
            
            images.append(canvas)
            print(f"  [OK] Loaded: {img_file.name} ({new_w}x{new_h})")
            
        except Exception as e:
            print(f"  [ERROR] {img_file.name}: {e}")
            continue
    
    if not images:
        print("\n[ERROR] No images loaded successfully")
        return False
    
    print(f"\n[OK] Prepared {len(images)} images\n")
    
    # Create video writer
    print("Creating video...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, resolution)
    
    if not out.isOpened():
        print("[ERROR] Failed to create video writer")
        return False
    
    frame_count = 0
    frames_per_image = fps * image_duration
    transition_frames = 30  # ~1 second transition at 30fps
    
    # Generate frames
    for loop in range(loop_count):
        print(f"  Loop {loop + 1}/{loop_count}:")
        
        for idx, img in enumerate(images):
            # Static frames for this image
            for _ in range(frames_per_image):
                out.write(img)
                frame_count += 1
            
            # Sliding transition to next image
            if idx < len(images) - 1:
                next_img = images[idx + 1]
                
                for t in range(transition_frames):
                    progress = t / transition_frames
                    slide_dist = int(resolution[0] * progress)
                    
                    # Create transition frame
                    trans_frame = np.ones((resolution[1], resolution[0], 3), dtype=np.uint8) * 255
                    
                    # Current image slides left
                    if resolution[0] - slide_dist > 0:
                        trans_frame[:, :resolution[0]-slide_dist] = img[:, slide_dist:]
                    
                    # Next image slides from right
                    if slide_dist > 0:
                        trans_frame[:, resolution[0]-slide_dist:] = next_img[:, :slide_dist]
                    
                    out.write(trans_frame)
                    frame_count += 1
            
            # After last image in loop, transition back to first
            elif loop < loop_count - 1 and len(images) > 1:
                next_img = images[0]
                
                for t in range(transition_frames):
                    progress = t / transition_frames
                    slide_dist = int(resolution[0] * progress)
                    
                    trans_frame = np.ones((resolution[1], resolution[0], 3), dtype=np.uint8) * 255
                    
                    if resolution[0] - slide_dist > 0:
                        trans_frame[:, :resolution[0]-slide_dist] = img[:, slide_dist:]
                    
                    if slide_dist > 0:
                        trans_frame[:, resolution[0]-slide_dist:] = next_img[:, :slide_dist]
                    
                    out.write(trans_frame)
                    frame_count += 1
            
            print(f"    Image {idx+1}/{len(images)}: {frame_count} frames total")
    
    out.release()
    
    # Summary
    video_size = output_path.stat().st_size / (1024*1024)
    video_duration = frame_count / fps
    
    print("\n" + "="*70)
    print("[SUCCESS] CAROUSEL VIDEO CREATED!")
    print("="*70)
    print(f"\nOutput: {output_path}")
    print(f"Resolution: {resolution[0]}x{resolution[1]} @ {fps}fps")
    print(f"Duration: {video_duration:.2f} seconds")
    print(f"Frames: {frame_count}")
    print(f"File Size: {video_size:.2f} MB")
    print(f"\nImages: {len(images)}")
    print(f"Loops: {loop_count}")
    print(f"Transition: Sliding ({transition_frames} frames per transition)")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create carousel video from input images")
    parser.add_argument("--input", default=r"C:\Users\ASUS\Desktop\Repos\image_stitching\input images",
                       help="Input directory with images")
    parser.add_argument("--output", default=r"C:\Users\ASUS\Desktop\Repos\image_stitching\carousel_video.mp4",
                       help="Output MP4 file path")
    parser.add_argument("--duration", type=int, default=4,
                       help="Seconds per image (default 4)")
    parser.add_argument("--fps", type=int, default=30,
                       help="Frames per second (default 30)")
    parser.add_argument("--loops", type=int, default=2,
                       help="Number of loops (default 2)")
    parser.add_argument("--width", type=int, default=1920,
                       help="Video width (default 1920)")
    parser.add_argument("--height", type=int, default=1080,
                       help="Video height (default 1080)")
    
    args = parser.parse_args()
    
    success = create_carousel_video_from_inputs(
        input_dir=args.input,
        output_path=args.output,
        image_duration=args.duration,
        fps=args.fps,
        resolution=(args.width, args.height),
        loop_count=args.loops
    )
    
    sys.exit(0 if success else 1)
