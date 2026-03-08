"""
Image Generator Base Class - Abstract interface for different image generation backends.
Allows easy switching between Hugging Face Spaces (free/test), Hugging Face Inference API, 
Replicate, Stability AI, or local Stable Diffusion.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path
from PIL import Image
import io


class ImageGenerator(ABC):
    """Abstract base class for image generation backends."""
    
    def __init__(self, model_name: str = "stabilityai/stable-diffusion-3"):
        self.model_name = model_name
        self.last_prompt = None
        self.last_error = None
    
    @abstractmethod
    def generate_image(self, 
                      prompt: str,
                      negative_prompt: str = "",
                      height: int = 768,
                      width: int = 768,
                      num_inference_steps: int = 30,
                      guidance_scale: float = 7.5) -> Optional[Image.Image]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of image to generate
            negative_prompt: Things to avoid in the image
            height: Image height in pixels
            width: Image width in pixels
            num_inference_steps: Number of diffusion steps (more = higher quality but slower)
            guidance_scale: How closely to follow the prompt (7-8 is typical)
            
        Returns:
            PIL Image object or None if generation fails
        """
        pass
    
    def generate_and_save(self,
                         prompt: str,
                         output_path: str,
                         negative_prompt: str = "",
                         **kwargs) -> bool:
        """
        Generate image and save to file.
        
        Args:
            prompt: Text prompt
            output_path: Path to save image
            negative_prompt: Things to avoid
            **kwargs: Additional arguments passed to generate_image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            image = self.generate_image(prompt, negative_prompt, **kwargs)
            if image is None:
                return False
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def batch_generate(self,
                      prompts: list,
                      output_dir: str,
                      negative_prompt: str = "",
                      **kwargs) -> dict:
        """
        Generate multiple images from a list of prompts.
        
        Args:
            prompts: List of text prompts
            output_dir: Directory to save images
            negative_prompt: Things to avoid
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with statistics: {success: int, failed: int, paths: list}
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        results = {"success": 0, "failed": 0, "paths": []}
        
        for i, prompt in enumerate(prompts):
            output_path = f"{output_dir}/generated_{i:03d}.jpg"
            
            if self.generate_and_save(prompt, output_path, negative_prompt, **kwargs):
                results["success"] += 1
                results["paths"].append(output_path)
            else:
                results["failed"] += 1
        
        return results
    
    @property
    def backend_name(self) -> str:
        """Return the name of the backend (for logging/debugging)."""
        return self.__class__.__name__
