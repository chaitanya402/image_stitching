#!/usr/bin/env python
"""
Integrated GenAI Carousel Pipeline Orchestrator
Coordinates all three agents for full carousel generation from descriptions.

AGENT 1: DescriptionBasedIconAgent
  - Studies the description
  - Prepares icons/emojis to add
  - Generates initial prompt
  - Extracts product metadata
  
AGENT 2: EnhancedPromptAndImageAgent  
  - Takes prompt from Agent 1
  - Enhances it with visual context
  - Calls GenAI (Hugging Face) to generate image
  - Returns image (NOT template stitching)

AGENT 3: CarouselVideoGenerator
  - Collects all generated images
  - Creates carousel video with transitions
  - Adds overlays and text
  - Exports final MP4
"""

import sys
import os
from pathlib import Path
from typing import List, Optional

# Setup path for imports
platform_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, platform_root)

from src.services.description_based_icon_agent import DescriptionBasedIconAgent
from src.services.enhanced_prompt_image_agent import EnhancedPromptAndImageAgent
from generate_carousel_video import CarouselVideoGenerator


class IntegratedGenAICarouselPipeline:
    """
    Orchestrates the full pipeline:
    Description → Agent 1 → Agent 2 → Agent 3 → Carousel Video
    """
    
    def __init__(self, backend: str = "hf-spaces", **backend_kwargs):
        """
        Initialize the integrated pipeline.
        
        Args:
            backend: "hf-spaces" (free, testing) or "hf-inference" (paid, production)
            **backend_kwargs: Arguments for the GenAI backend
        """
        self.backend = backend
        self.backend_kwargs = backend_kwargs
        
        # Initialize agents
        print("\n" + "="*80)
        print("INTEGRATED GENAI CAROUSEL PIPELINE")
        print("="*80)
        print(f"\nInitializing agents...")
        print(f"[Agent 1] DescriptionBasedIconAgent ✓")
        print(f"[Agent 2] EnhancedPromptAndImageAgent (backend: {backend})")
        
        self.agent2 = EnhancedPromptAndImageAgent(backend, **backend_kwargs)
        print(f"[Agent 3] CarouselVideoGenerator ✓")
        
        print(f"\nPipeline ready for processing!\n")
    
    def process_descriptions(self,
                            descriptions: List[str],
                            output_video_path: str,
                            video_headline: str = "",
                            video_subtext: str = "",
                            video_cta: str = "",
                            image_width: int = 1080,
                            image_height: int = 1080,
                            image_duration: int = 4) -> bool:
        """
        Full end-to-end pipeline: descriptions → carousel video
        
        Args:
            descriptions: List of product descriptions
            output_video_path: Path for output MP4 video
            video_headline: Fixed headline for all video frames
            video_subtext: Fixed subtext for all video frames
            video_cta: Fixed CTA for all video frames
            image_width: Width of generated images
            image_height: Height of generated images
            image_duration: Seconds to display each image
        
        Returns:
            True if successful, False otherwise
        """
        
        print("\n" + "="*60)
        print("PIPELINE EXECUTION")
        print("="*60)
        print(f"\nInput: {len(descriptions)} product descriptions")
        print(f"Output: {output_video_path}\n")
        
        # Create temp directory
        temp_images_dir = "temp_integrated_genai"
        Path(temp_images_dir).mkdir(exist_ok=True)
        Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)
        
        # ============================================================
        # AGENT 1: Parse descriptions
        # ============================================================
        print("\n[STEP 1] AGENT 1: Analyze descriptions & prepare context\n")
        
        parsed_results = []
        for i, desc in enumerate(descriptions, 1):
            print(f"  [{i}/{len(descriptions)}] Parsing description...")
            
            parsed = DescriptionBasedIconAgent.parse_description(desc)
            parsed_results.append(parsed)
            
            print(f"      Product Type: {parsed['product_type']}")
            print(f"      Discount: {parsed['discount_text']}")
            print(f"      Icons: {', '.join(parsed.get('suggested_icons', [])[:2])}")
            print(f"      Keywords: {', '.join(parsed.get('keywords', [])[:3])}")
        
        print(f"\n[STEP 1] ✓ Completed: {len(parsed_results)} descriptions analyzed\n")
        
        # ============================================================
        # AGENT 2: Generate images using GenAI
        # ============================================================
        print("\n[STEP 2] AGENT 2: Generate images with GenAI\n")
        print(f"Note: This may take several minutes depending on backend")
        print(f"Backend: {self.agent2.image_generator.backend_name}\n")
        
        generated_images = []
        
        for i, (description, parsed_data) in enumerate(zip(descriptions, parsed_results), 1):
            output_path = f"{temp_images_dir}/image_{i:03d}.jpg"
            
            print(f"  [{i}/{len(descriptions)}] Generating image...")
            
            if self.agent2.generate_and_save_image(
                description=description,
                output_path=output_path,
                parsed_data=parsed_data
            ):
                generated_images.append(output_path)
            else:
                print(f"      ✗ Failed to generate image")
        
        if not generated_images:
            print(f"\n[STEP 2] ✗ FAILED: No images generated!")
            return False
        
        print(f"\n[STEP 2] ✓ Completed: {len(generated_images)}/{len(descriptions)} images generated\n")
        
        # ============================================================
        # AGENT 3: Create carousel video
        # ============================================================
        print("\n[STEP 3] AGENT 3: Create carousel video\n")
        
        carousel_gen = CarouselVideoGenerator(
            width=1920,
            height=1080,
            fps=30,
            image_duration=image_duration
        )
        
        print(f"  Creating carousel with {len(generated_images)} images...")
        print(f"  Duration: {image_duration}s per image")
        print(f"  Output: {output_video_path}\n")
        
        success = carousel_gen.generate_carousel_video(
            image_paths=generated_images,
            output_path=output_video_path,
            headline=video_headline,
            subtext=video_subtext,
            cta=video_cta,
            num_loops=1
        )
        
        if not success:
            print(f"\n[STEP 3] ✗ FAILED: Could not create carousel video")
            return False
        
        print(f"\n[STEP 3] ✓ Completed: Carousel video created\n")
        
        # ============================================================
        # Cleanup and summary
        # ============================================================
        print("\n" + "="*60)
        print("PIPELINE COMPLETE ✓")
        print("="*60)
        
        print(f"\n[SUCCESS] Carousel video ready!")
        print(f"  Output: {output_video_path}")
        print(f"  Images: {len(generated_images)} AI-generated")
        print(f"  Backend: {self.agent2.image_generator.backend_name}")
        
        # Cleanup temp images
        print(f"\nCleaning up temporary files...")
        for img_path in generated_images:
            try:
                Path(img_path).unlink()
            except:
                pass
        
        try:
            Path(temp_images_dir).rmdir()
        except:
            pass
        
        print(f"[OK] Cleanup complete\n")
        
        return True


def example_usage():
    """Example of using the integrated pipeline."""
    
    print("\n" + "="*80)
    print("INTEGRATED GENAI CAROUSEL PIPELINE - EXAMPLE")
    print("="*80)
    
    # Example product descriptions
    test_descriptions = [
        "Premium leather wallet with RFID protection and multiple card slots. Limited time 20% OFF!",
        "Elegant minimalist coffee table made from sustainable reclaimed wood.",
        "Vibrant summer beach dress with tropical print. Perfect for vacation!",
    ]
    
    print("\nExample: Generating carousel from 3 product descriptions")
    print("Backend: HuggingFace Spaces (free, CPU-based, slower)")
    print("Expected time: 5-15 minutes\n")
    
    # Create pipeline
    pipeline = IntegratedGenAICarouselPipeline(backend="hf-spaces")
    
    # Process descriptions
    success = pipeline.process_descriptions(
        descriptions=test_descriptions,
        output_video_path="integrated_carousel_output.mp4",
        video_headline="New Collection",
        video_subtext="AI-Generated Designs",
        video_cta="Shop Now",
        image_duration=4  # 4 seconds per image
    )
    
    if success:
        print("\n✓ Successfully generated carousel!")
        print("✓ Ready to upload to social media!")
    else:
        print("\n✗ Pipeline failed")
        return False
    
    # Show next steps
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. UPGRADE TO PRODUCTION (Optional):")
    print("   - Get API key: https://huggingface.co/settings/tokens")
    print("   - Set environment: set HUGGINGFACE_TOKEN=your_key")
    print("   - Change backend: backend='hf-inference' (10x faster!)")
    print("\n2. INTEGRATE INTO YOUR PLATFORM:")
    print("   - Import IntegratedGenAICarouselPipeline")
    print("   - Call process_descriptions() in your API routes")
    print("   - Pass user-provided descriptions")
    print("\n3. CUSTOMIZE:")
    print("   - Adjust image_duration for different pacing")
    print("   - Modify colors via DescriptionBasedIconAgent")
    print("   - Fine-tune prompts in EnhancedPromptAndImageAgent")


if __name__ == "__main__":
    example_usage()
