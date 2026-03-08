"""
Agent 2: Enhanced Prompt & GenAI Image Generator
Takes prepared prompt from DescriptionBasedIconAgent, enhances it, and generates image via GenAI.

Flow:
1. DescriptionBasedIconAgent analyzes description → outputs prompt_data
2. This agent (Agent 2) enhances prompt + calls GenAI → outputs image
3. CarouselVideoGenerator collects images → outputs carousel video
"""

from typing import Optional, Dict
from PIL import Image
from .image_generator_factory import ImageGeneratorFactory
from .prompt_generator_agent import PromptGeneratorAgent


class EnhancedPromptAndImageAgent:
    """
    Takes analysis from DescriptionBasedIconAgent and generates images using GenAI.
    
    Workflow:
    Input: parsed_description (from DescriptionBasedIconAgent)
    - contains: product_type, color_scheme, suggested_icons, keywords, etc.
    
    Process:
    1. Extract prompt data from parsed description
    2. Enhance prompt with additional context and style
    3. Add visual elements (icons, style hints) to prompt
    4. Call GenAI (via Hugging Face)
    5. Return generated image
    """
    
    def __init__(self, backend: str = "hf-spaces", **backend_kwargs):
        """
        Initialize with GenAI backend.
        
        Args:
            backend: "hf-spaces" (test, free) or "hf-inference" (prod, paid)
            **backend_kwargs: Arguments for backend (e.g., api_key for hf-inference)
        """
        self.image_generator = ImageGeneratorFactory.create(backend, **backend_kwargs)
        print(f"[Agent 2] Using image generator: {self.image_generator.backend_name}")
    
    def enhance_prompt_with_visual_context(self,
                                          base_description: str,
                                          parsed_data: Dict) -> tuple:
        """
        Enhance the prompt with visual context from DescriptionBasedIconAgent.
        
        Args:
            base_description: Original product description
            parsed_data: From DescriptionBasedIconAgent.parse_description()
                Contains: product_type, color_scheme, suggested_icons, keywords, etc.
        
        Returns:
            (enhanced_prompt, negative_prompt): Tuple of prompts for GenAI
        """
        
        # Start with PromptGeneratorAgent
        base_prompt = PromptGeneratorAgent.generate_prompt(base_description)
        
        # Extract visual context from parsed_data
        product_type = parsed_data.get("product_type", "product")
        color_scheme = parsed_data.get("color_scheme", {})
        suggested_icons = parsed_data.get("suggested_icons", [])
        discount_percent = parsed_data.get("discount_percent", 0)
        keywords = parsed_data.get("keywords", [])
        
        # Build enhanced prompt components
        enhancements = []
        
        # Add color scheme hints
        if color_scheme:
            primary_color = color_scheme.get("primary", "").replace("(", "").replace(")", "")
            if primary_color:
                enhancements.append(f"color scheme: {primary_color} and white")
        
        # Add icon/visual elements hints
        if suggested_icons:
            icons_str = ", ".join(suggested_icons[:3])  # Limit to 3
            enhancements.append(f"includes {icons_str} icons")
        
        # Add discount hint
        if discount_percent > 0:
            enhancements.append(f"prominent {discount_percent}% discount badge")
        
        # Add product category emphasis
        if product_type and product_type != "general":
            enhancements.append(f"emphasize {product_type} product category")
        
        # Combine all parts
        if enhancements:
            enhanced_prompt = f"{base_prompt}, {', '.join(enhancements)}"
        else:
            enhanced_prompt = base_prompt
        
        # Generate negative prompt
        negative_prompt = PromptGeneratorAgent.generate_negative_prompt(base_description)
        
        return enhanced_prompt, negative_prompt
    
    def generate_image_from_description(self,
                                       description: str,
                                       parsed_data: Optional[Dict] = None,
                                       image_width: int = 1080,
                                       image_height: int = 1080) -> Optional[Image.Image]:
        """
        Generate image for a product description using GenAI.
        
        Args:
            description: Product description
            parsed_data: Optional parsed data from DescriptionBasedIconAgent
                        If not provided, will use DescriptionAgent to analyze
            image_width: Output image width
            image_height: Output image height
        
        Returns:
            PIL Image object or None if generation fails
        """
        
        # If no parsed_data provided, use DescriptionAgent as fallback
        if parsed_data is None:
            from .description_based_icon_agent import DescriptionBasedIconAgent
            parsed_data = DescriptionBasedIconAgent.parse_description(description)
        
        # Enhance prompt with visual context
        enhanced_prompt, negative_prompt = self.enhance_prompt_with_visual_context(
            description, parsed_data
        )
        
        print(f"\n[Agent 2] Generating image from enhanced prompt...")
        print(f"[Agent 2] Product: {parsed_data.get('product_type', 'unknown')}")
        print(f"[Agent 2] Discount: {parsed_data.get('discount_text', 'N/A')}")
        print(f"[Agent 2] Enhanced Prompt: {enhanced_prompt[:70]}...")
        
        # Call GenAI
        image = self.image_generator.generate_image(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            height=image_height,
            width=image_width,
            num_inference_steps=30,
            guidance_scale=7.5
        )
        
        if image:
            print(f"[Agent 2] ✓ Image generated successfully!")
        else:
            print(f"[Agent 2] ✗ Failed: {self.image_generator.last_error}")
        
        return image
    
    def generate_and_save_image(self,
                               description: str,
                               output_path: str,
                               parsed_data: Optional[Dict] = None) -> bool:
        """
        Generate image and save to file.
        
        Args:
            description: Product description
            output_path: Path to save image
            parsed_data: Optional parsed data from DescriptionBasedIconAgent
        
        Returns:
            True if successful, False otherwise
        """
        
        image = self.generate_image_from_description(description, parsed_data)
        
        if image is None:
            return False
        
        try:
            image.save(output_path)
            print(f"[Agent 2] Saved to: {output_path}")
            return True
        except Exception as e:
            print(f"[Agent 2] Save error: {e}")
            return False
    
    def batch_generate_images_from_descriptions(self,
                                               descriptions: list,
                                               output_dir: str,
                                               parsed_data_list: Optional[list] = None) -> dict:
        """
        Generate images for multiple descriptions.
        
        Args:
            descriptions: List of product descriptions
            output_dir: Directory to save all images
            parsed_data_list: Optional list of pre-parsed data (from DescriptionBasedIconAgent)
        
        Returns:
            Dict with results: {success: int, failed: int, paths: list}
        """
        
        from pathlib import Path
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        results = {"success": 0, "failed": 0, "paths": []}
        
        for i, description in enumerate(descriptions):
            output_path = f"{output_dir}/genai_image_{i:03d}.jpg"
            
            # Use pre-parsed data if available
            parsed_data = None
            if parsed_data_list and i < len(parsed_data_list):
                parsed_data = parsed_data_list[i]
            
            print(f"\n[Agent 2] Processing {i+1}/{len(descriptions)}...")
            
            if self.generate_and_save_image(description, output_path, parsed_data):
                results["success"] += 1
                results["paths"].append(output_path)
            else:
                results["failed"] += 1
        
        print(f"\n[Agent 2] Batch complete: {results['success']}/{len(descriptions)} successful")
        
        return results


# Example of integrated usage
if __name__ == "__main__":
    from .description_based_icon_agent import DescriptionBasedIconAgent
    
    print("="*80)
    print("AGENT 2 - ENHANCED PROMPT & GENAI IMAGE GENERATION")
    print("="*80)
    
    # Example workflow
    test_descriptions = [
        "Premium leather wallet with RFID protection. 20% OFF!",
        "Minimalist coffee table from sustainable wood.",
    ]
    
    print("\n[WORKFLOW] AGENT 1: Parse descriptions\n")
    
    # Step 1: Agent 1 - Parse descriptions
    parsed_results = []
    for desc in test_descriptions:
        parsed = DescriptionBasedIconAgent.parse_description(desc)
        parsed_results.append(parsed)
        print(f"Description: {desc[:50]}...")
        print(f"  → Product Type: {parsed['product_type']}")
        print(f"  → Discount: {parsed['discount_text']}")
        print(f"  → Icons: {parsed.get('suggested_icons', [])}\n")
    
    # Step 2: Agent 2 - Generate images
    print("\n[WORKFLOW] AGENT 2: Generate images (this will take 1-5 minutes)\n")
    
    generator = EnhancedPromptAndImageAgent(backend="hf-spaces")
    
    results = generator.batch_generate_images_from_descriptions(
        descriptions=test_descriptions,
        output_dir="temp_genai_images",
        parsed_data_list=parsed_results
    )
    
    print(f"\n[WORKFLOW] Results: {results['success']} images generated")
    print(f"[WORKFLOW] Ready for Agent 3 (Carousel creation)")
