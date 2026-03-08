"""
Prompt Generator Agent - Converts product descriptions to detailed image generation prompts.
Takes context from DescriptionAgent and creates detailed, style-consistent prompts for Stable Diffusion.
"""

import re
from typing import Dict, Tuple
from .description_agent import DescriptionAgent


class PromptGeneratorAgent:
    """Generates detailed image prompts from product descriptions for Stable Diffusion."""
    
    # Style presets for consistent aesthetic
    STYLE_PRESETS = {
        "professional": "professional product photography, studio lighting, white background, high quality, sharp focus",
        "lifestyle": "lifestyle photography, natural lighting, modern aesthetic, realistic",
        "minimalist": "minimalist design, clean composition, white space, modern, elegant",
        "vibrant": "vibrant colors, dynamic composition, eye-catching, energetic, modern design",
        "luxury": "luxury product shot, premium styling, gold accents, elegant composition, sophisticated",
        "casual": "casual lifestyle, friendly vibes, natural setting, approachable, warm tones",
    }
    
    # Quality modifiers for image generation
    QUALITY_MODIFIERS = "8k, high resolution, intricate details, professional quality, trending on artstation"
    
    @staticmethod
    def analyze_description(description: str) -> Dict[str, any]:
        """Extract key elements from description."""
        if not description:
            return {"style": "professional", "keywords": [], "sentiment": "neutral", "discount": False}
        
        desc_lower = description.lower()
        
        # Check for discount/sale indicators
        has_discount = bool(re.search(r'(\d+%|off|sale|discount|limited)', desc_lower))
        
        # Detect style hints
        style = "professional"
        if any(word in desc_lower for word in ["lifestyle", "casual", "everyday", "relax"]):
            style = "lifestyle"
        elif any(word in desc_lower for word in ["luxury", "premium", "exclusive", "high-end"]):
            style = "luxury"
        elif any(word in desc_lower for word in ["vibrant", "bright", "colorful", "fun"]):
            style = "vibrant"
        elif any(word in desc_lower for word in ["minimal", "simple", "clean", "minimal"]):
            style = "minimalist"
        
        # Extract keywords
        keywords = DescriptionAgent.extract_keywords(description)
        
        # Get sentiment
        sentiment = DescriptionAgent.sentiment(description)
        
        return {
            "style": style,
            "keywords": keywords,
            "sentiment": sentiment,
            "discount": has_discount,
            "raw_description": description
        }
    
    @staticmethod
    def generate_prompt(description: str, style: str = None, include_discount_badge: bool = True) -> str:
        """
        Generate a detailed image prompt from product description.
        
        Args:
            description: Product description
            style: Optional style override (professional, lifestyle, minimalist, vibrant, luxury, casual)
            include_discount_badge: Add discount badge elements if detected
            
        Returns:
            Detailed prompt for Stable Diffusion
        """
        analysis = PromptGeneratorAgent.analyze_description(description)
        
        # Use provided style or detected style
        if style:
            analysis["style"] = style
        
        style_preset = PromptGeneratorAgent.STYLE_PRESETS.get(analysis["style"], 
                                                               PromptGeneratorAgent.STYLE_PRESETS["professional"])
        
        # Build prompt components
        components = []
        
        # Main product description - first 100 chars as main focus
        main_desc = description.split('.')[0][:150]
        components.append(f"featured product: {main_desc}")
        
        # Add keywords as visual elements
        if analysis["keywords"]:
            keywords_str = ", ".join(analysis["keywords"][:5])  # Limit to 5 keywords
            components.append(f"featuring: {keywords_str}")
        
        # Add discount visual if applicable
        if analysis["discount"] and include_discount_badge:
            discount_match = re.search(r'(\d+)%', description)
            if discount_match:
                discount = discount_match.group(1)
                components.append(f"prominent {discount}% discount badge in corner")
            else:
                components.append("sale or discount badge visible")
        
        # Add style preset
        components.append(style_preset)
        
        # Add quality modifiers
        components.append(PromptGeneratorAgent.QUALITY_MODIFIERS)
        
        # Combine all components
        final_prompt = ", ".join(components)
        
        # Ensure reasonable length (Stable Diffusion typically handles up to 77 tokens)
        # Prioritize early components which are more important
        if len(final_prompt) > 500:
            final_prompt = final_prompt[:500]
        
        return final_prompt
    
    @staticmethod
    def generate_negative_prompt(description: str = None) -> str:
        """
        Generate negative prompt (things to avoid) for better image quality.
        
        Args:
            description: Optional description for context-specific negatives
            
        Returns:
            Negative prompt string
        """
        base_negatives = [
            "watermark",
            "text overlay",
            "low quality",
            "blurry",
            "distorted",
            "amateur",
            "poorly composed",
            "duplicate",
            "nsfw"
        ]
        
        # Add context-specific negatives
        if description:
            desc_lower = description.lower()
            if "outdoor" not in desc_lower:
                base_negatives.append("outdoor background")
            if "person" not in desc_lower:
                base_negatives.append("people")
        
        return ", ".join(base_negatives)
    
    @staticmethod
    def batch_generate_prompts(descriptions: list, style: str = None) -> list:
        """
        Generate prompts for multiple descriptions.
        
        Args:
            descriptions: List of product descriptions
            style: Optional consistent style for all prompts
            
        Returns:
            List of generated prompts
        """
        return [PromptGeneratorAgent.generate_prompt(desc, style=style) for desc in descriptions]


# Example usage:
if __name__ == "__main__":
    # Test examples
    test_descriptions = [
        "Premium leather wallet with RFID protection, perfect for travelers. Get 20% OFF today!",
        "Elegant minimalist coffee table made from sustainable wood. Limited edition collection.",
        "Vibrant summer dress in tropical print. Perfect for beach vacation. Sale on all summer items!",
    ]
    
    print("=" * 80)
    print("PROMPT GENERATOR TEST")
    print("=" * 80)
    
    for desc in test_descriptions:
        print(f"\nOriginal Description:\n{desc}\n")
        
        prompt = PromptGeneratorAgent.generate_prompt(desc)
        neg_prompt = PromptGeneratorAgent.generate_negative_prompt(desc)
        
        print(f"Generated Prompt:\n{prompt}\n")
        print(f"Negative Prompt:\n{neg_prompt}\n")
        print("-" * 80)
