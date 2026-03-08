#!/usr/bin/env python
"""
Batch Carousel Video Generator (GenAI Version)
Creates carousel videos from AI-generated promotional images.

Workflow:
1. Product descriptions → Prompts (PromptGeneratorAgent)
2. Prompts → AI images (Stable Diffusion via HF Spaces/API)
3. Images → Carousel video (CarouselVideoGenerator)

Supports two backends:
- Option B: HF Spaces (free, CPU-based, slow - for testing)
- Option D: HF Inference API (paid, GPU-based, fast - for production)
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Setup path for imports
platform_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, platform_root)

from src.services.prompt_generator_agent import PromptGeneratorAgent
from src.services.image_generator_factory import ImageGeneratorFactory
from generate_carousel_video import CarouselVideoGenerator


class GenAICarouselGenerator:
    """Generate carousel videos using GenAI image generation."""
    
    def __init__(self, backend: str = "hf-spaces", **backend_kwargs):
        """
        Initialize GenAI carousel generator.
        
        Args:
            backend: "hf-spaces" (test, free) or "hf-inference" (production, paid)
            **backend_kwargs: Arguments for the image generator backend
        """
        self.backend_name = backend
        self.image_generator = ImageGeneratorFactory.create(backend, **backend_kwargs)
        print(f"\n[CAROUSEL] Using image generator: {self.image_generator.backend_name}")
    
    def generate_carousel_from_descriptions(self,
                                           descriptions: List[str],
                                           output_video_path: str,
                                           style: Optional[str] = None,
                                           fixed_headline: str = "",
                                           fixed_subtext: str = "",
                                           fixed_cta: str = "",
                                           image_width: int = 1080,
                                           image_height: int = 1080) -> bool:
        """
        Generate carousel video from product descriptions using GenAI.
        
        Args:
            descriptions: List of product descriptions
            output_video_path: Path for output MP4 video
            style: Optional style preset (professional, lifestyle, luxury, etc.)
            fixed_headline: Fixed headline for all frames
            fixed_subtext: Fixed subtext for all frames
            fixed_cta: Fixed CTA for all frames
            image_width: Width of generated images
            image_height: Height of generated images
            
        Returns:
            True if successful, False otherwise
        """
        
        print("\n" + "="*80)
        print("GENAI CAROUSEL VIDEO GENERATOR")
        print("="*80)
        
        print(f"\nBackend: {self.image_generator.backend_name}")
        print(f"Input Descriptions: {len(descriptions)}")
        for i, desc in enumerate(descriptions, 1):
            print(f"   {i}. {desc[:70]}...")
        print()
        
        # Ensure directories exist
        Path("temp_carousel_images").mkdir(exist_ok=True)
        Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Generate prompts from descriptions
        print("Step 1: Converting descriptions to image generation prompts...\n")
        prompts = PromptGeneratorAgent.batch_generate_prompts(descriptions, style=style)
        negative_prompt = PromptGeneratorAgent.generate_negative_prompt()
        
        for i, (desc, prompt) in enumerate(zip(descriptions, prompts), 1):
            print(f"  [{i}] Description:")
            print(f"      {desc[:70]}")
            print(f"      Prompt: {prompt[:80]}...")
        
        # Step 2: Generate images from prompts
        print(f"\nStep 2: Generating images using {self.image_generator.backend_name}...\n")
        print(f"WARNING: Depending on backend, this may take several minutes!")
        if "spaces" in self.image_generator.backend_name.lower():
            print(f"NOTICE: HF Spaces uses CPU, expect 60-120 seconds per image")
        print()
        
        generated_images = []
        for i, prompt in enumerate(prompts):
            output_path = f"temp_carousel_images/carousel_{i:03d}.jpg"
            
            print(f"  [{i+1}/{len(prompts)}] Generating image...")
            try:
                success = self.image_generator.generate_and_save(
                    prompt=prompt,
                    output_path=output_path,
                    negative_prompt=negative_prompt,
                    height=image_height,
                    width=image_width
                )
                
                if success:
                    generated_images.append(output_path)
                    print(f"      ✓ Saved: {output_path}\n")
                else:
                    print(f"      ✗ Failed: {self.image_generator.last_error}\n")
            except Exception as e:
                print(f"      ✗ Exception: {str(e)}\n")
        
        if not generated_images:
            print("[ERROR] No images generated!")
            return False
        
        print(f"\n[SUCCESS] Generated {len(generated_images)}/{len(prompts)} images")
        
        # Step 3: Create carousel video
        print(f"\nStep 3: Creating carousel video with {len(generated_images)} images...\n")
        
        carousel_gen = CarouselVideoGenerator(
            width=1920,
            height=1080,
            fps=30,
            image_duration=4  # 4 seconds per image
        )
        
        success = carousel_gen.generate_carousel_video(
            image_paths=generated_images,
            output_path=output_video_path,
            headline=fixed_headline,
            subtext=fixed_subtext,
            cta=fixed_cta,
            num_loops=1
        )
        
        if success:
            print(f"✓ Carousel video created successfully!")
            print(f"✓ Video saved to: {output_video_path}")
            
            # Cleanup
            print("\nCleaning up temporary files...")
            for img in generated_images:
                try:
                    Path(img).unlink()
                except:
                    pass
            try:
                Path("temp_carousel_images").rmdir()
            except:
                pass
            print("[OK] Cleanup complete")
            
            return True
        else:
            print(f"✗ Failed to create carousel video")
            return False
    
    def generate_carousel_from_prompts(self,
                                      prompts: List[str],
                                      output_video_path: str,
                                      fixed_headline: str = "",
                                      fixed_subtext: str = "",
                                      fixed_cta: str = "",
                                      image_width: int = 1080,
                                      image_height: int = 1080) -> bool:
        """
        Generate carousel video directly from image generation prompts.
        
        Args:
            prompts: List of direct image generation prompts
            output_video_path: Path for output MP4 video
            fixed_headline: Fixed headline
            fixed_subtext: Fixed subtext
            fixed_cta: Fixed CTA
            image_width: Image width
            image_height: Image height
            
        Returns:
            True if successful
        """
        
        print("\n" + "="*80)
        print("GENAI CAROUSEL VIDEO GENERATOR (Direct Prompts)")
        print("="*80)
        
        print(f"\nBackend: {self.image_generator.backend_name}")
        print(f"Input Prompts: {len(prompts)}")
        for i, prompt in enumerate(prompts[:5], 1):
            print(f"   {i}. {prompt[:70]}...")
        if len(prompts) > 5:
            print(f"   ... and {len(prompts)-5} more")
        
        # Generate images directly
        Path("temp_carousel_images").mkdir(exist_ok=True)
        Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\nGenerating {len(prompts)} images using {self.image_generator.backend_name}...\n")
        
        generated_images = []
        for i, prompt in enumerate(prompts):
            output_path = f"temp_carousel_images/carousel_{i:03d}.jpg"
            
            print(f"  [{i+1}/{len(prompts)}] Generating image from prompt...")
            try:
                success = self.image_generator.generate_and_save(
                    prompt=prompt,
                    output_path=output_path,
                    height=image_height,
                    width=image_width
                )
                
                if success:
                    generated_images.append(output_path)
                    print(f"      ✓ Saved: {output_path}\n")
                else:
                    print(f"      ✗ Failed: {self.image_generator.last_error}\n")
            except Exception as e:
                print(f"      ✗ Exception: {str(e)}\n")
        
        if not generated_images:
            print("[ERROR] No images generated!")
            return False
        
        print(f"\n[SUCCESS] Generated {len(generated_images)}/{len(prompts)} images")
        
        # Create video
        print(f"\nCreating carousel video...\n")
        carousel_gen = CarouselVideoGenerator(width=1920, height=1080, fps=30, image_duration=4)
        
        success = carousel_gen.generate_carousel_video(
            image_paths=generated_images,
            output_path=output_video_path,
            headline=fixed_headline,
            subtext=fixed_subtext,
            cta=fixed_cta,
            num_loops=1
        )
        
        if success:
            print(f"✓ Video saved to: {output_video_path}")
            
            # Cleanup
            print("\nCleaning up...")
            for img in generated_images:
                try:
                    Path(img).unlink()
                except:
                    pass
            try:
                Path("temp_carousel_images").rmdir()
            except:
                pass
            
            return True
        else:
            print(f"✗ Failed to create carousel video")
            return False


if __name__ == "__main__":
    # Example usage
    print("\n" + "="*80)
    print("GENAI CAROUSEL GENERATOR - EXAMPLE")
    print("="*80)
    
    # Show available backends
    ImageGeneratorFactory.print_backend_info()
    
    # Example descriptions
    test_descriptions = [
        "Premium leather wallet with RFID protection. Limited time 20% OFF!",
        "Elegant minimalist coffee table made from sustainable wood.",
        "Vibrant summer dress in tropical print with beach vibes.",
    ]
    
    print("\n\nTesting with HF Spaces Backend (Option B - Free/Slow)...")
    print("Note: This will take several minutes due to CPU inference")
    print("To skip this test, comment out the code below.\n")
    
    try:
        # Option B: Free tier (slow)
        generator = GenAICarouselGenerator(backend="hf-spaces")
        
        success = generator.generate_carousel_from_descriptions(
            descriptions=test_descriptions,
            output_video_path="test_carousel_genai.mp4",
            fixed_headline="Featured Products",
            fixed_cta="Shop Now"
        )
        
        if success:
            print("\n[SUCCESS] Test carousel generated!")
        else:
            print("\n[FAILED] Test carousel generation failed")
    
    except Exception as e:
        print(f"\n[ERROR] Exception during generation: {e}")
        print("\nNote: To use production backend (Option D), you need:")
        print("1. HF API key: https://huggingface.co/settings/tokens")
        print("2. Set HUGGINGFACE_TOKEN environment variable")
        print("3. Paid credits on Hugging Face")
