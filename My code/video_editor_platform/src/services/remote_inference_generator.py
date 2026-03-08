"""
Remote Inference Generator - Uses Hugging Face InferenceClient (WORKING)
This is the RECOMMENDED production approach - fast, reliable, no local resources needed.

InferenceClient automatically handles the new HF Router routing.

Supports:
- SDXL (free tier)  
- FLUX models (requires payment)
and other models available on HF Inference API
"""

import json
from typing import Optional
from PIL import Image
import time
from pathlib import Path
from huggingface_hub import InferenceClient
from .image_generator_base import ImageGenerator


class RemoteInferenceGenerator(ImageGenerator):
    """Generate images using HuggingFace Inference API via InferenceClient."""
    
    # Free and fast models available
    AVAILABLE_MODELS = {
        "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",  # Free, fast
        "sd3": "stabilityai/stable-diffusion-3-medium",      # Requires credits
        "flux-dev": "black-forest-labs/FLUX.1-dev",          # Requires credits
        "flux-pro": "black-forest-labs/FLUX.1-pro",          # Requires credits
    }
    
    def __init__(self, api_key: str = None, model_name: str = "sdxl", timeout: int = 120):
        """
        Initialize Remote Inference Generator.
        
        Args:
            api_key: HF API token (loads from config if not provided)
            model_name: Model to use (see AVAILABLE_MODELS)
            timeout: Request timeout in seconds
        """
        super().__init__(model_name=model_name)
        
        # Load API key
        self.api_key = api_key or self._load_api_key_from_config()
        if not self.api_key:
            raise ValueError(
                "No HF API token found! Provide via api_key param or config/config.json"
            )
        
        # Set model
        self.model_id = self.AVAILABLE_MODELS.get(model_name, model_name)
        print(f"[RemoteInferenceGenerator] Using model: {self.model_id}")
        
        # Create InferenceClient (handles routing automatically)
        self.client = InferenceClient(api_key=self.api_key)
        self.timeout = timeout
    
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
        """
        Generate an image using HF Inference API.
        
        Args:
            prompt: Text description
            negative_prompt: Things to avoid
            height: Image height
            width: Image width
            num_inference_steps: Number of diffusion steps
            guidance_scale: Guidance scale for prompt adherence
            
        Returns:
            PIL Image or None on failure
        """
        
        print(f"\n[RemoteInference] Generating image...")
        print(f"  Model: {self.model_id}")
        print(f"  Prompt: {prompt[:60]}...")
        print(f"  Height: {height}, Width: {width}")
        
        try:
            start_time = time.time()
            
            # InferenceClient.text_to_image handles routing automatically
            image = self.client.text_to_image(
                prompt,
                model=self.model_id,
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
            
            # Check for specific errors
            if "410" in error_msg or "Gone" in error_msg:
                print(f"  ✗ Model endpoint error (410 Gone)")
                print(f"  Note: {self.model_id} may not be available via InferenceClient")
                print(f"  💡 Try using 'sdxl-remote' instead (free and reliable)")
                return None
            
            if "503" in error_msg or "loading" in error_msg.lower():
                print(f"  ⚠ Model loading (503). Retrying in 5s...")
                time.sleep(5)
                return self.generate_image(
                    prompt, negative_prompt, height, width, 
                    num_inference_steps, guidance_scale
                )
            else:
                print(f"  ✗ Error: {error_msg[:200]}")
                return None
