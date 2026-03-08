"""Unit tests for EmoGImageAgent."""

import unittest
import os
import sys

# Add the video_editor_platform directory to path
test_file_dir = os.path.dirname(os.path.abspath(__file__))
platform_root = os.path.abspath(os.path.join(test_file_dir, '../../'))
sys.path.insert(0, platform_root)

from PIL import Image
from src.services.emo_g_image_agent import EmoGImageAgent

class TestEmoGImageAgent(unittest.TestCase):
    def setUp(self):
        """Create a temporary image for testing."""
        self.test_image_path = "test_image.png"
        self.output_image_path = "output_image.png"
        img = Image.new("RGB", (200, 200), color="blue")
        img.save(self.test_image_path)

    def tearDown(self):
        """Remove temporary images after tests."""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.output_image_path):
            os.remove(self.output_image_path)

    def test_add_emo_g_to_image(self):
        """Test adding emo-g to an image."""
        emo_g_list = [
            {"emo_g": "🎉", "position": (50, 50), "font_size": 32},
            {"emo_g": "🎁", "position": (100, 100), "font_size": 48}
        ]

        EmoGImageAgent.add_emo_g_to_image(self.test_image_path, emo_g_list, self.output_image_path)

        # Check if the output image is created
        self.assertTrue(os.path.exists(self.output_image_path))

if __name__ == "__main__":
    unittest.main()