"""Agent to pick and add emo-g to an image."""

from typing import List, Dict
import cv2
import numpy as np
import requests
import os
import torch
from diffusers import DiffusionPipeline
from diffusers.utils import load_image

class EmoGImageAgent:
    @staticmethod
    def add_emo_g_to_image(image_path: str, emo_g_list: List[Dict[str, str]], output_path: str) -> None:
        """Add emo-g to the image and save the result.

        Args:
            image_path (str): Path to the input image.
            emo_g_list (List[Dict[str, str]]): List of emo-g to add, with their positions.
            output_path (str): Path to save the output image.
        """
        # Load the image
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Add text to the image
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "20% SALE"
        font_scale = 3
        font_thickness = 5
        text_color = (0, 0, 255)  # Red color in BGR
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x = (image.shape[1] - text_size[0]) // 2
        text_y = image.shape[0] // 3
        cv2.putText(image, text, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        # Add emojis to the image
        for emo_g in emo_g_list:
            emoji = emo_g.get('emo_g', '?')
            position = emo_g.get('position', (0, 0))
            font_size = emo_g.get('font_size', 96)

            # Create a blank image for the emoji
            emoji_image = np.zeros((font_size, font_size, 4), dtype=np.uint8)
            emoji_font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(emoji_image, emoji, (10, font_size - 10), emoji_font, 1, (255, 255, 255, 255), 2, cv2.LINE_AA)

            # Overlay emoji on the main image
            x, y = position
            y1, y2 = y, y + emoji_image.shape[0]
            x1, x2 = x, x + emoji_image.shape[1]

            alpha_s = emoji_image[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                image[y1:y2, x1:x2, c] = (alpha_s * emoji_image[:, :, c] + alpha_l * image[y1:y2, x1:x2, c])

        # Save the output image
        cv2.imwrite(output_path, image)

    @staticmethod
    def generate_image_with_genai(prompt, input_image_path, output_path):
        """
        Generate an image using Hugging Face's Stable Diffusion 2 model.

        Args:
            prompt (str): The text prompt to generate the image.
            input_image_path (str): Path to the input image.
            output_path (str): The path to save the generated image.
        """
        # Log the prompt
        print(f"Prompt: {prompt}")

        # Ensure the output directory exists
        edited_images_dir = os.path.dirname(output_path)
        if not os.path.exists(edited_images_dir):
            os.makedirs(edited_images_dir)

        # Load the input image
        input_image = load_image(input_image_path)

        # Initialize the pipeline with the updated model ID
        pipe = DiffusionPipeline.from_pretrained(
            "sd2-community/stable-diffusion-2",
            torch_dtype=torch.float32,
            device="cpu"  # Use CPU for compatibility
        )

        try:
            # Generate the image
            generated_image = pipe(image=input_image, prompt=prompt).images[0]

            # Save the generated image
            generated_image.save(output_path)

            print(f"Image successfully generated and saved to {output_path}")
        except Exception as e:
            print(f"Failed to generate image: {e}")