"""Agent to add custom text to an image."""

from PIL import Image, ImageDraw, ImageFont

class TextImageAgent:
    @staticmethod
    def add_text_to_image(image_path: str, text: str, output_path: str, position=(10, 10), font_size=32) -> None:
        """Add custom text to an image and save the result.

        Args:
            image_path (str): Path to the input image.
            text (str): Text to add to the image.
            output_path (str): Path to save the output image.
            position (tuple): Position to place the text (default: top-left corner).
            font_size (int): Font size of the text (default: 32).
        """
        # Open the image
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # Load font
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=font_size)
        except Exception:
            font = ImageFont.load_default()

        # Add text to the image
        draw.text(position, text, font=font, fill=(255, 255, 255))

        # Save the modified image
        img.save(output_path)