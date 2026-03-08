"""
HuggingFace Free Image Generation - Multiple Approaches
1. InferenceClient with free models
2. Gradio client for community FLUX Spaces
"""

import json
import time
from typing import Optional
from pathlib import Path
from PIL import Image

from .image_generator_base import ImageGenerator


class HFInferenceGenerator(ImageGenerator):
    """
    Generate images using HuggingFace Inference API with free tier support.
    Tests multiple free/reliable models available through Inference Providers.
    """
    
    # Free and reliable models on HF Inference
    FREE_MODELS = {
        "jax-diffusers-t2i": "https://api-inference.huggingface.co/models/jax-diffusers/stable-diffusion-2-1",
        "stable-diffusion-2-1": "stabilityai/stable-diffusion-2-1",
        "stable-diffusion-xl": "stabilityai/stable-diffusion-xl-base-1.0",
    }
    
    def __init__(self, api_key: str = None):
        """Initialize HF Inference Generator."""
        super().__init__(model_name="hf-inference-free")
        
        # Load API key
        self.api_key = api_key or self._load_api_key_from_config()
        if not self.api_key:
            raise ValueError(
                "No HF API token found! Provide via api_key param or config/config.json"
            )
        
        # Import here to avoid breaking if not installed
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(api_key=self.api_key)
        except ImportError:
            raise ImportError("huggingface_hub not installed. Run: pip install huggingface-hub")
    
    @staticmethod
    def _load_api_key_from_config() -> Optional[str]:
        """Load API key from config/config.json."""
        try:
            possible_paths = [
                Path(__file__).parent.parent.parent / "config" / "config.json",
                Path.cwd() / "config" / "config.json",
            ]
            
            for config_path in possible_paths:
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        token = config.get('huggingface', {}).get('api_token')
                        if token and token != "your_token_here":
                            return token
        except Exception as e:
            print(f"[Warning] Could not load token from config: {e}")
        
        return None
    
    def generate_image(self,
                      prompt: str,
                      negative_prompt: str = "",
                      height: int = 768,
                      width: int = 768,
                      num_inference_steps: int = 30,
                      guidance_scale: float = 7.5) -> Optional[Image.Image]:
        """Generate image using SDXL (free tier available)."""
        
        print(f"\n[HFInference] Generating image...")
        print(f"  Model: stabilityai/stable-diffusion-xl-base-1.0")
        print(f"  Prompt: {prompt[:60]}...")
        
        try:
            start_time = time.time()
            
            image = self.client.text_to_image(
                prompt,
                model="stabilityai/stable-diffusion-xl-base-1.0",
                height=height,
                width=width,
                negative_prompt=negative_prompt if negative_prompt else None,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
            
            elapsed = time.time() - start_time
            print(f"  ✓ Image generated in {elapsed:.1f}s: {image.width}x{image.height}")
            
            return image
                
        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ Error: {error_msg[:200]}")
            return None


class HFSpacesGradioGenerator(ImageGenerator):
    """
    Generate images using free FLUX Spaces via Gradio client.
    Uses community-hosted FLUX spaces that are free to use.
    """
    
    # Popular free FLUX Spaces
    SPACES = {
        "flux-schnell": "black-forest-labs/FLUX.1-schnell",  # Official, fastest, usually free
        "flux-schnell-alt": "andreakiro/FLUX.1-schnell",
        "flux-dev": "black-forest-labs/FLUX.1-dev",
    }
    
    def __init__(self, space_id: str = "flux-schnell"):
        """
        Initialize Gradio-based FLUX Space Generator.
        
        Args:
            space_id: Key from SPACES dict (models available on community Spaces)
        """
        super().__init__(model_name="hf-spaces-gradio")
        
        self.space_id = space_id
        self.space_path = self.SPACES.get(space_id, space_id)
        
        print(f"[HFSpacesGradio] Using Space: {self.space_path}")
        
        # Import here to avoid breaking if not installed
        try:
            from gradio_client import Client
            self.Client = Client
        except ImportError:
            raise ImportError("gradio_client not installed. Run: pip install gradio-client")
    
    def generate_image(self,
                      prompt: str,
                      negative_prompt: str = "",
                      height: int = 768,
                      width: int = 768,
                      num_inference_steps: int = 4,
                      guidance_scale: float = 3.5) -> Optional[Image.Image]:
        """Generate image using Gradio Space FLUX."""
        
        print(f"\n[HFSpacesGradio] Generating image...")
        print(f"  Space: {self.space_path}")
        print(f"  Prompt: {prompt[:60]}...")
        
        try:
            start_time = time.time()
            
            # Initialize Gradio client for the Space
            client = self.Client(self.space_path)
            
            # Call the predict endpoint (specific to FLUX Spaces)
            # Most FLUX spaces take: prompt, negative_prompt, height, width, steps, guidance
            result = client.predict(
                prompt=prompt,
                negative_prompt=negative_prompt if negative_prompt else "",
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
            
            elapsed = time.time() - start_time
            
            # Result is typically a file path
            if isinstance(result, str):
                image = Image.open(result)
            else:
                image = result
            
            print(f"  ✓ Image generated in {elapsed:.1f}s: {image.width}x{image.height}")
            
            return image
                
        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ Error: {error_msg[:200]}")
            return None
