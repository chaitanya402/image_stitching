"""
Hugging Face Spaces Image Generator - Option B (FREE/TESTING)
Uses Hugging Face Spaces API for Stable Diffusion inference.
Good for: Testing, free tier, no API key needed initially.
Limitation: CPU-based, slower (60-120s per image), rate-limited.
"""

import requests
import time
from typing import Optional
from PIL import Image
import io
import os
from .image_generator_base import ImageGenerator


class HuggingFaceSpacesGenerator(ImageGenerator):
    """Generate images using Hugging Face Spaces (free, CPU-based inference)."""
    
    # Popular Stable Diffusion Spaces on HF (free tier)
    AVAILABLE_SPACES = {
        "stabilityai/stable-diffusion": "https://huggingface.co/spaces/stabilityai/stable-diffusion-3",
        "runwayml/stable-diffusion-v1-5": "https://huggingface.co/spaces/stabilityai/stable-diffusion-v1-5",
    }
    
    def __init__(self, space_name: str = "stabilityai/stable-diffusion", 
                 api_key: str = None, 
                 timeout: int = 300):
        """
        Initialize Hugging Face Spaces generator.
        
        Args:
            space_name: Space ID to use
            api_key: Optional HF API token (for faster inference)
            timeout: Timeout for requests (default 300s for slow CPU inference)
        """
        super().__init__(model_name=space_name)
        self.space_name = space_name
        self.api_key = api_key or os.environ.get("HUGGINGFACE_TOKEN")
        self.timeout = timeout
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Map space names to model IDs
        self.model_id = self._get_model_id(space_name)
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    @staticmethod
    def _get_model_id(space_name: str) -> str:
        """Map space name to actual model ID for inference API."""
        mapping = {
            "stabilityai/stable-diffusion": "stabilityai/stable-diffusion-2-1",
            "runwayml/stable-diffusion-v1-5": "runwayml/stable-diffusion-v1-5",
            "default": "stabilityai/stable-diffusion-2"
        }
        return mapping.get(space_name, mapping["default"])
    
    def generate_image(self,
                      prompt: str,
                      negative_prompt: str = "",
                      height: int = 768,
                      width: int = 768,
                      num_inference_steps: int = 30,
                      guidance_scale: float = 7.5) -> Optional[Image.Image]:
        """
        Generate an image using Hugging Face Inference API.
        
        Args:
            prompt: Text description
            negative_prompt: Things to avoid
            height: Image height (will be quantized to 64)
            width: Image width (will be quantized to 64)
            num_inference_steps: Number of steps (limited: free tier ~50 max)
            guidance_scale: Guidance scale (7-8 recommended)
            
        Returns:
            PIL Image or None if failed
        """
        self.last_prompt = prompt
        
        # Limit parameters for free tier
        num_inference_steps = min(num_inference_steps, 50)
        height = (height // 64) * 64  # Must be multiple of 64
        width = (width // 64) * 64
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt or "blurry, low quality, distorted",
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "height": height,
                "width": width
            }
        }
        
        url = f"{self.base_url}/{self.model_id}"
        
        try:
            print(f"[HF Spaces] Generating image from prompt: {prompt[:60]}...")
            print(f"[HF Spaces] Using model: {self.model_id}")
            print(f"[HF Spaces] Note: Free tier uses CPU, may take 60-120 seconds...")
            
            # Make request with retries
            for attempt in range(3):
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    # Response is binary image
                    image = Image.open(io.BytesIO(response.content))
                    print(f"[HF Spaces] ✓ Image generated successfully!")
                    return image
                
                elif response.status_code == 429:  # Rate limited
                    wait_time = int(response.headers.get("Retry-After", 60))
                    print(f"[HF Spaces] Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                
                elif response.status_code == 503:  # Model loading
                    print(f"[HF Spaces] Model loading, waiting 30 seconds (attempt {attempt+1}/3)...")
                    time.sleep(30)
                
                else:
                    error_msg = response.text[:200]
                    print(f"[HF Spaces] Error {response.status_code}: {error_msg}")
                    self.last_error = error_msg
                    break
            
            print("[HF Spaces] ✗ Failed to generate image")
            return None
            
        except requests.exceptions.Timeout:
            self.last_error = "Request timeout after 5 minutes"
            print(f"[HF Spaces] ✗ {self.last_error}")
            return None
        except Exception as e:
            self.last_error = str(e)
            print(f"[HF Spaces] ✗ Error: {self.last_error}")
            return None
    
    @property
    def backend_name(self) -> str:
        return f"HuggingFaceSpaces({self.model_id})"
