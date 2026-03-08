"""
Hugging Face Inference API Image Generator - Option D (PRODUCTION)
Uses Hugging Face Inference API for fast GPU-based Stable Diffusion inference.
Good for: Production, fast generation (5-30s per image), reliable.
Requires: HF API key and paid credits.
"""

import requests
import time
from typing import Optional
from PIL import Image
import io
import os
from .image_generator_base import ImageGenerator


class HuggingFaceInferenceGenerator(ImageGenerator):
    """Generate images using Hugging Face Inference API (fast, GPU-backed)."""
    
    # Available models on HF Inference API (these are production-grade, fast)
    AVAILABLE_MODELS = {
        "stable-diffusion-3": "stabilityai/stable-diffusion-3",
        "stable-diffusion-2-1": "stabilityai/stable-diffusion-2-1",
        "stable-diffusion-v1-5": "runwayml/stable-diffusion-v1-5",
        "sdxl": "stabilityai/stable-diffusion-xl",
    }
    
    def __init__(self, model_name: str = "stable-diffusion-3", api_key: str = None):
        """
        Initialize Hugging Face Inference API generator.
        
        Args:
            model_name: Model to use (see AVAILABLE_MODELS)
            api_key: HF API token (required! Get from https://huggingface.co/settings/tokens)
        """
        super().__init__(model_name=model_name)
        
        self.api_key = api_key or os.environ.get("HUGGINGFACE_TOKEN")
        if not self.api_key:
            raise ValueError(
                "HuggingFace API key required! Set HUGGINGFACE_TOKEN environment variable "
                "or pass api_key parameter. Get one at https://huggingface.co/settings/tokens"
            )
        
        # Resolve model ID
        self.model_id = self.AVAILABLE_MODELS.get(model_name, model_name)
        
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.request_count = 0
        self.total_cost = 0.0  # For tracking approximate costs
    
    def generate_image(self,
                      prompt: str,
                      negative_prompt: str = "",
                      height: int = 768,
                      width: int = 768,
                      num_inference_steps: int = 30,
                      guidance_scale: float = 7.5) -> Optional[Image.Image]:
        """
        Generate an image using HF Inference API (fast GPU-backed).
        
        Args:
            prompt: Text description
            negative_prompt: Things to avoid
            height: Image height (768x768 or 1024x1024 recommended)
            width: Image width
            num_inference_steps: Quality vs speed tradeoff (20-50, 30 = default)
            guidance_scale: How strongly to follow prompt (7-8 recommended)
            
        Returns:
            PIL Image or None if failed
        """
        self.last_prompt = prompt
        
        # Validate parameters for API
        num_inference_steps = max(1, min(num_inference_steps, 100))
        guidance_scale = max(1.0, min(guidance_scale, 20.0))
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt or "blurry, low quality, distorted, watermark",
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "height": height,
                "width": width
            }
        }
        
        url = f"{self.base_url}/{self.model_id}"
        
        try:
            print(f"[HF Inference] Generating image from prompt: {prompt[:60]}...")
            print(f"[HF Inference] Using model: {self.model_id}")
            print(f"[HF Inference] Expected time: 5-30 seconds")
            
            start_time = time.time()
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=300  # 5 minute timeout for slow models
            )
            
            elapsed = time.time() - start_time
            self.request_count += 1
            
            # Estimate cost (approximately $0.01 per image for fast models)
            self.total_cost += 0.01
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                print(f"[HF Inference] ✓ Image generated in {elapsed:.1f}s")
                print(f"[HF Inference] Total requests: {self.request_count}, Approx cost: ${self.total_cost:.2f}")
                return image
            
            elif response.status_code == 503:
                # Model loading
                print("[HF Inference] Model is loading, please retry in 30 seconds")
                self.last_error = "Model loading"
                return None
            
            else:
                error_msg = response.text[:200]
                print(f"[HF Inference] Error {response.status_code}: {error_msg}")
                self.last_error = error_msg
                return None
                
        except requests.exceptions.Timeout:
            self.last_error = "Request timeout"
            print(f"[HF Inference] ✗ {self.last_error}")
            return None
        except Exception as e:
            self.last_error = str(e)
            print(f"[HF Inference] ✗ Error: {self.last_error}")
            return None
    
    def get_cost_estimate(self, num_images: int) -> dict:
        """
        Estimate cost for generating multiple images.
        
        Args:
            num_images: Number of images to generate
            
        Returns:
            Dict with cost estimates
        """
        # Approximate costs (varies by model)
        cost_per_image = 0.01  # $0.01 per image average
        
        return {
            "estimated_total_cost": f"${num_images * cost_per_image:.2f}",
            "cost_per_image": f"${cost_per_image:.4f}",
            "num_images": num_images,
            "note": "Actual costs may vary based on image resolution and model complexity"
        }
    
    @property
    def backend_name(self) -> str:
        return f"HFInferenceAPI({self.model_id})"
