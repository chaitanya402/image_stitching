#!/usr/bin/env python
"""
Carousel Video Generator - Creates sliding carousel video from multiple promo images.
Combines images with fixed text overlay and infinite loop.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple
import numpy as np
import cv2

# Setup path for imports
platform_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, platform_root)


class CarouselVideoGenerator:
    """Generates carousel videos from multiple images with sliding transition"""
    
    def __init__(self, width=1920, height=1080, fps=30, image_duration=4):
        """
        Initialize carousel video generator
        
        Args:
            width: Video width (default 1080p width)
            height: Video height (default 1080p height)
            fps: Frames per second
            image_duration: How long each image displays (seconds)
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.image_duration = image_duration
        self.frames_per_image = fps * image_duration  # frames each image shows
        
    def resize_image_to_fit(self, image, target_width, target_height):
        """
        Resize image to fit video dimensions while maintaining aspect ratio.
        Centers image if needed.
        """
        h, w = image.shape[:2]
        
        # Calculate scaling factor
        scale = min(target_width / w, target_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Create canvas and center image
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        canvas.fill(255)  # White background
        
        # Calculate centering offsets
        x_offset = (target_width - new_w) // 2
        y_offset = (target_height - new_h) // 2
        
        # Place image on canvas
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return canvas
    
    def create_sliding_transition(self, image1, image2, transition_frames=30):
        """
        Create sliding transition frames between two images.
        Image1 slides out to the left, Image2 slides in from the right.
        
        Args:
            image1: Current image
            image2: Next image
            transition_frames: Number of frames for transition
            
        Returns:
            List of transition frames
        """
        frames = []
        
        for i in range(transition_frames):
            progress = i / transition_frames  # 0 to 1
            
            # Create blended frame
            frame = np.zeros_like(image1)
            
            # Calculate slide positions
            slide_distance = int(self.width * progress)
            
            # Image1 slides left (exits)
            x1_start = -slide_distance
            x1_end = x1_start + self.width
            if x1_end > 0:
                src_x1 = max(0, -x1_start)
                dst_x1 = max(0, x1_start)
                width1 = min(self.width - dst_x1, self.width - src_x1)
                if width1 > 0:
                    frame[0:self.height, dst_x1:dst_x1+width1] = image1[0:self.height, src_x1:src_x1+width1]
            
            # Image2 slides right (enters)
            x2_start = self.width - slide_distance
            x2_end = x2_start + self.width
            if x2_start < self.width:
                src_x2 = max(0, -x2_start)
                dst_x2 = max(0, x2_start)
                width2 = min(self.width - dst_x2, self.width - src_x2)
                if width2 > 0:
                    frame[0:self.height, dst_x2:dst_x2+width2] = image2[0:self.height, src_x2:src_x2+width2]
            
            frames.append(frame)
        
        return frames
    
    def add_text_overlay(self, frame, headline="", subtext="", cta="", position_y_offset=0):
        """
        Add text overlay to frame (matching template style).
        
        Args:
            frame: Frame to add text to
            headline: Main headline text
            subtext: Subtext
            cta: Call-to-action button text
            position_y_offset: Y position offset
        """
        frame = frame.copy()
        
        # Fonts
        headline_font = cv2.FONT_HERSHEY_SIMPLEX
        headline_scale = 3
        headline_thickness = 4
        
        subtext_font = cv2.FONT_HERSHEY_SIMPLEX
        subtext_scale = 2
        subtext_thickness = 3
        
        cta_font = cv2.FONT_HERSHEY_SIMPLEX
        cta_scale = 2.5
        cta_thickness = 4
        
        # Colors (BGR format for OpenCV)
        text_color = (255, 255, 255)  # White
        bg_color = (50, 50, 50)  # Dark gray (semi-transparent effect will be added)
        
        # Headline
        if headline:
            headline_size = cv2.getTextSize(headline, headline_font, headline_scale, headline_thickness)[0]
            headline_x = (self.width - headline_size[0]) // 2
            headline_y = int(self.height * 0.35) + position_y_offset
            
            # Background for headline
            padding = 20
            cv2.rectangle(frame, 
                         (headline_x - padding, headline_y - headline_size[1] - padding),
                         (headline_x + headline_size[0] + padding, headline_y + padding),
                         bg_color, -1)
            
            # Add text
            cv2.putText(frame, headline, (headline_x, headline_y), 
                       headline_font, headline_scale, text_color, headline_thickness)
        
        # Subtext
        if subtext:
            subtext_size = cv2.getTextSize(subtext, subtext_font, subtext_scale, subtext_thickness)[0]
            subtext_x = (self.width - subtext_size[0]) // 2
            subtext_y = int(self.height * 0.50) + position_y_offset
            
            # Background for subtext
            padding = 15
            cv2.rectangle(frame,
                         (subtext_x - padding, subtext_y - subtext_size[1] - padding),
                         (subtext_x + subtext_size[0] + padding, subtext_y + padding),
                         bg_color, -1)
            
            # Add text
            cv2.putText(frame, subtext, (subtext_x, subtext_y),
                       subtext_font, subtext_scale, text_color, subtext_thickness)
        
        # CTA Button
        if cta:
            cta_size = cv2.getTextSize(cta, cta_font, cta_scale, cta_thickness)[0]
            cta_x = (self.width - cta_size[0]) // 2
            cta_y = int(self.height * 0.85) + position_y_offset
            
            # Background for CTA (red for automotive)
            padding = 25
            cv2.rectangle(frame,
                         (cta_x - padding, cta_y - cta_size[1] - padding),
                         (cta_x + cta_size[0] + padding, cta_y + padding),
                         (43, 57, 192), -1)  # Red (BGR)
            
            # Border
            cv2.rectangle(frame,
                         (cta_x - padding, cta_y - cta_size[1] - padding),
                         (cta_x + cta_size[0] + padding, cta_y + padding),
                         (255, 255, 255), 3)  # White border
            
            # Add text
            cv2.putText(frame, cta, (cta_x, cta_y),
                       cta_font, cta_scale, text_color, cta_thickness)
        
        return frame
    
    def generate_carousel_video(self, image_paths: List[str], output_path: str,
                               headline: str = "", subtext: str = "", cta: str = "",
                               num_loops: int = 2):
        """
        Generate carousel video from multiple images.
        
        Args:
            image_paths: List of image file paths
            output_path: Output video file path
            headline: Text to display at top
            subtext: Text to display in middle
            cta: Call-to-action text
            num_loops: Number of times to loop through all images
        """
        
        print("\n" + "="*70)
        print("CAROUSEL VIDEO GENERATOR")
        print("="*70 + "\n")
        
        print(f"📝 Creating carousel video from {len(image_paths)} images")
        print(f"   Duration per image: {self.image_duration}s")
        print(f"   Resolution: {self.width}x{self.height}@{self.fps}fps")
        print(f"   Output: {output_path}\n")
        
        # Load and resize images
        print("Step 1: Loading and preparing images...")
        images = []
        for i, img_path in enumerate(image_paths):
            if not Path(img_path).exists():
                print(f"  ✗ Image not found: {img_path}")
                continue
            
            img = cv2.imread(img_path)
            if img is None:
                print(f"  ✗ Failed to load: {img_path}")
                continue
            
            # Resize to fit video dimensions
            resized = self.resize_image_to_fit(img, self.width, self.height)
            images.append(resized)
            print(f"  ✓ Loaded image {i+1}: {img_path}")
        
        if not images:
            print("  ✗ No images loaded!")
            return False
        
        print(f"  ✓ Total images: {len(images)}\n")
        
        # Create video writer
        print("Step 2: Initializing video writer...")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        if not out.isOpened():
            print("  ✗ Failed to create video writer!")
            return False
        
        print(f"  ✓ Video writer initialized\n")
        
        # Generate frames for carousel
        print("Step 3: Generating carousel frames...")
        total_frames = 0
        frame_count = 0
        
        for loop in range(num_loops):
            print(f"\n  Loop {loop + 1}/{num_loops}:")
            
            for i, image in enumerate(images):
                # Static frames (4 seconds at current image)
                for frame_idx in range(self.frames_per_image):
                    frame_with_text = self.add_text_overlay(image, headline, subtext, cta)
                    out.write(frame_with_text)
                    frame_count += 1
                
                # Sliding transition to next image
                if i < len(images) - 1:
                    next_image = images[i + 1]
                    transition_frames = self.create_sliding_transition(image, next_image, transition_frames=30)
                    
                    for trans_frame in transition_frames:
                        frame_with_text = self.add_text_overlay(trans_frame, headline, subtext, cta)
                        out.write(frame_with_text)
                        frame_count += 1
                else:
                    # After last image, transition back to first (for loop)
                    if loop < num_loops - 1:
                        next_image = images[0]
                        transition_frames = self.create_sliding_transition(image, next_image, transition_frames=30)
                        
                        for trans_frame in transition_frames:
                            frame_with_text = self.add_text_overlay(trans_frame, headline, subtext, cta)
                            out.write(frame_with_text)
                            frame_count += 1
                
                total_frames = frame_count
                print(f"    ✓ Image {i+1}/{len(images)} - {frame_count} frames")
        
        out.release()
        
        # Calculate video duration
        video_duration = frame_count / self.fps
        file_size = Path(output_path).stat().st_size / (1024 * 1024)  # MB
        
        print("\n" + "="*70)
        print("✅ CAROUSEL VIDEO GENERATED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📹 Output Video: {output_path}")
        print(f"   Resolution: {self.width}x{self.height}@{self.fps}fps")
        print(f"   Duration: {video_duration:.2f} seconds")
        print(f"   Total Frames: {frame_count}")
        print(f"   File Size: {file_size:.2f} MB")
        print(f"\n🎨 Overlay Text:")
        print(f"   Headline: '{headline}'")
        print(f"   Subtext: '{subtext}'")
        print(f"   CTA: '{cta}'")
        print("="*70 + "\n")
        
        return True


if __name__ == "__main__":
    # Example usage
    gen = CarouselVideoGenerator(width=1920, height=1080, fps=30, image_duration=4)
    
    # Generate carousel video from promo images
    image_list = [
        "edited_images/template_demo_0.jpg",
        "edited_images/template_demo_1.jpg",
        "edited_images/template_demo_2.jpg",
    ]
    
    gen.generate_carousel_video(
        image_paths=image_list,
        output_path="edited_videos/carousel_promo.mp4",
        headline="EXCLUSIVE OFFERS",
        subtext="LIMITED TIME ONLY",
        cta="SHOP NOW",
        num_loops=2
    )
