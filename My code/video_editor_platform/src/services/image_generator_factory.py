"""
Image Generator Factory — remote-first AI image generation backends.

Available backends:
  REMOTE (RECOMMENDED):
    - "sdxl-remote": SDXL via HF Router (free, fast) ⭐
    - "flux-remote": FLUX via HF Router (requires credits)

  ALTERNATIVE:
    - "hf-inference": HF Inference API free tier
"""

from typing import Optional
from .image_generator_base import ImageGenerator
from .remote_inference_generator import RemoteInferenceGenerator

FREE_GENERATORS_AVAILABLE = False
try:
    from .hf_free_generators import HFInferenceGenerator
    FREE_GENERATORS_AVAILABLE = True
except ImportError:
    pass


class ImageGeneratorFactory:
    """Factory for creating image generators with different backends."""
    
    BACKENDS = {
        "sdxl-remote": lambda **kwargs: RemoteInferenceGenerator(model_name="sdxl", **kwargs),
        "flux-remote": lambda **kwargs: RemoteInferenceGenerator(model_name="flux-dev", **kwargs),
    }

    if FREE_GENERATORS_AVAILABLE:
        BACKENDS["hf-inference"] = lambda **kwargs: HFInferenceGenerator(**kwargs)
    
    @staticmethod
    def create(backend: str = "sdxl-remote", **kwargs) -> ImageGenerator:
        """
        Create an image generator instance.
        
        Args:
            backend: Backend to use (default: "sdxl-remote" - fast, free):
                
                RECOMMENDED (Remote - via HF Router):
                  - "sdxl-remote": SDXL model (FREE, fast) ⭐
                  - "flux-remote": FLUX model (requires credits, faster)
                
                ALTERNATIVE (Local inference - requires diffusers):
                  - "flux-local": Local FLUX (offline, GPU required)
                    Install: pip install diffusers transformers torch accelerate
                
                LEGACY (may not work):
                  - "hf-spaces", "hf-inference", "flux", "flux-inference"
            
            **kwargs: Arguments to pass to generator constructor
            
        Returns:
            ImageGenerator instance
            
        Raises:
            ValueError: If backend not found or dependencies missing
        """
        if backend not in ImageGeneratorFactory.BACKENDS:
            # Check if user is trying to use flux-local without diffusers
            if backend == "flux-local":
                raise ValueError(
                    f"Backend '{backend}' requires diffusers library.\n"
                    f"Install with: pip install diffusers transformers torch accelerate\n"
                    f"\nOr use 'sdxl-remote' (no installation needed):\n"
                    f"  backend='sdxl-remote'"
                )
            
            raise ValueError(
                f"Unknown backend: '{backend}'\n"
                f"Available backends:\n"
                f"  Remote (RECOMMENDED):\n"
                f"    - sdxl-remote [FREE, FAST] ⭐\n"
                f"    - flux-remote [requires credits]\n"
                f"  Alternative:\n"
                f"    - hf-inference [HF Inference API free tier]"
            )
        
        generator_class = ImageGeneratorFactory.BACKENDS[backend]
        
        # Handle lambda functions vs class constructors
        if callable(generator_class) and hasattr(generator_class, '__self__'):
            # It's a lambda, call it directly
            return generator_class(**kwargs)
        else:
            # It's a class, instantiate it
            return generator_class(**kwargs)
    
    @staticmethod
    def get_recommended_backend(use_case: str = "testing") -> str:
        return "sdxl-remote"
    
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
            },
            "flux": {
                "name": "FLUX.2-klein Spaces (FREE - Default for quality)",
                "speed": "Fast (15-60s per image, depends on queue)",
                "cost": "FREE - No credits required!",
                "quality": "Excellent (state-of-the-art FLUX model)",
                "requirements": ["Internet connection only"],
                "best_for": "Best quality images, free tier, artistic control",
                "setup": "No setup needed! Ready to use immediately."
            },
            "flux-inference": {
                "name": "FLUX.2-klein Inference API (PAID - Faster)",
                "speed": "Fast (10-30s per image)",
                "cost": "Paid (~$0.01 per image)",
                "quality": "Excellent (state-of-the-art FLUX model)",
                "requirements": ["HF API key", "Paid credits"],
                "best_for": "Production use, guaranteed speed, no queue",
                "setup": "Get API token: https://huggingface.co/settings/tokens"
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
