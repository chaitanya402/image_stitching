"""
Image Generator Factory - Easily switch between different image generation backends.
Supports: HuggingFace Spaces (free testing), HuggingFace Inference API (production).
"""

from typing import Optional
from .image_generator_base import ImageGenerator
from .huggingface_spaces_generator import HuggingFaceSpacesGenerator
from .huggingface_inference_generator import HuggingFaceInferenceGenerator


class ImageGeneratorFactory:
    """Factory for creating image generators with different backends."""
    
    BACKENDS = {
        "hf-spaces": HuggingFaceSpacesGenerator,
        "hf-inference": HuggingFaceInferenceGenerator,
    }
    
    @staticmethod
    def create(backend: str = "hf-spaces", **kwargs) -> ImageGenerator:
        """
        Create an image generator instance.
        
        Args:
            backend: Backend to use:
                - "hf-spaces": Hugging Face Spaces (free, CPU-based, slow) [DEFAULT for testing]
                - "hf-inference": Hugging Face Inference API (paid, GPU-based, fast) [PRODUCTION]
            **kwargs: Arguments to pass to the generator constructor
            
        Returns:
            ImageGenerator instance
            
        Raises:
            ValueError: If backend not found
        """
        if backend not in ImageGeneratorFactory.BACKENDS:
            raise ValueError(
                f"Unknown backend: {backend}\n"
                f"Available backends: {', '.join(ImageGeneratorFactory.BACKENDS.keys())}"
            )
        
        generator_class = ImageGeneratorFactory.BACKENDS[backend]
        return generator_class(**kwargs)
    
    @staticmethod
    def get_recommended_backend(use_case: str = "testing") -> str:
        """
        Get recommended backend for a use case.
        
        Args:
            use_case: "testing" or "production"
            
        Returns:
            Backend name
        """
        if use_case == "testing":
            return "hf-spaces"  # Free, good for quick testing
        elif use_case == "production":
            return "hf-inference"  # Fast, reliable, needs API key and credits
        else:
            return "hf-spaces"  # Default to testing backend
    
    @staticmethod
    def print_backend_info():
        """Print information about available backends."""
        print("\n" + "=" * 80)
        print("AVAILABLE IMAGE GENERATION BACKENDS")
        print("=" * 80)
        
        backends_info = {
            "hf-spaces": {
                "name": "Hugging Face Spaces (Option B - TEST)",
                "speed": "Slow (60-120s per image)",
                "cost": "Free",
                "quality": "Good (CPU inference)",
                "requirements": ["Internet connection"],
                "best_for": "Testing, prototyping, small batches",
                "setup": "No API key needed (but slower)"
            },
            "hf-inference": {
                "name": "Hugging Face Inference API (Option D - PRODUCTION)",
                "speed": "Fast (5-30s per image)",
                "cost": "Paid (~$0.01 per image)",
                "quality": "Excellent (GPU inference)",
                "requirements": ["HF API key", "Paid credits"],
                "best_for": "Production, high-volume generation, speed-critical",
                "setup": "Get API key from https://huggingface.co/settings/tokens"
            }
        }
        
        for backend_key, info in backends_info.items():
            print(f"\n{info['name']}")
            print(f"  Speed:       {info['speed']}")
            print(f"  Cost:        {info['cost']}")
            print(f"  Quality:     {info['quality']}")
            print(f"  Best for:    {info['best_for']}")
            print(f"  Requirements: {', '.join(info['requirements'])}")
            print(f"  Setup:       {info['setup']}")
        
        print("\n" + "=" * 80)


# Example usage and testing
if __name__ == "__main__":
    # Print available backends
    ImageGeneratorFactory.print_backend_info()
    
    # Example: Create generator for testing
    print("\n\nCreating generator for TESTING (HF Spaces)...")
    try:
        generator = ImageGeneratorFactory.create("hf-spaces")
        print(f"✓ Created: {generator.backend_name}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example: Create generator for production (requires API key)
    print("\n\nCreating generator for PRODUCTION (HF Inference API)...")
    try:
        generator = ImageGeneratorFactory.create("hf-inference")
        print(f"✓ Created: {generator.backend_name}")
    except Exception as e:
        print(f"Note: {e}")
