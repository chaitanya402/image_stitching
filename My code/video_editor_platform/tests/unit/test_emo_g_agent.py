"""Unit tests for EmoGAgent."""

import sys
import os
import unittest

# Add the video_editor_platform directory to path
test_file_dir = os.path.dirname(os.path.abspath(__file__))
platform_root = os.path.abspath(os.path.join(test_file_dir, '../../'))
sys.path.insert(0, platform_root)

from src.services.emo_g_agent import EmoGAgent

class TestEmoGAgent(unittest.TestCase):
    def test_identify_emo_g(self):
        """Test emo-g generation for a positive sentiment description."""
        description = "Amazing sale with 50% off!"
        expected_emo_g = ["🎉"]  # Example based on CreativeAgent logic
        result = EmoGAgent.identify_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertEqual(result, expected_emo_g)

    def test_identify_emo_g_with_negative_sentiment(self):
        """Test emo-g generation for a negative sentiment description."""
        description = "This is a bad deal."
        expected_emo_g = []  # No emojis for negative sentiment
        result = EmoGAgent.identify_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertEqual(result, expected_emo_g)

    def test_identify_emo_g_with_multiple_keywords(self):
        """Test emo-g generation for a description with multiple keywords."""
        description = "New gift available with 20% off!"
        expected_emo_g = ["🎁"]  # Example based on CreativeAgent logic
        result = EmoGAgent.identify_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertIn("🎁", result)

    def test_identify_emo_g_with_empty_description(self):
        """Test emo-g generation for an empty description."""
        description = ""
        expected_emo_g = []  # No emojis for empty description
        result = EmoGAgent.identify_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertEqual(result, expected_emo_g)

    def test_display_emo_g(self):
        emo_g_list = ["🎉", "🎁"]
        # This test ensures no exceptions are raised during display
        try:
            EmoGAgent.display_emo_g(emo_g_list)
        except Exception as e:
            self.fail(f"display_emo_g raised an exception: {e}")

    def test_identify_discount_with_emo_g(self):
        description = "Huge discount on all items!"
        expected_offers = [{"offer": "Discount", "emo_g": "💸"}]
        result = EmoGAgent.identify_special_offers_with_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertEqual(result, expected_offers)

    def test_identify_promotion_with_emo_g(self):
        description = "Limited time promotion available now."
        expected_offers = [{"offer": "Promotion", "emo_g": "📣"}]
        result = EmoGAgent.identify_special_offers_with_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertEqual(result, expected_offers)

    def test_identify_buy_1_get_1_with_emo_g(self):
        description = "Buy 1 get 1 free on all products!"
        expected_offers = [{"offer": "Buy 1 Get 1", "emo_g": "🛍️"}]
        result = EmoGAgent.identify_special_offers_with_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertEqual(result, expected_offers)

    def test_identify_multiple_offers_with_emo_g(self):
        description = "Buy 1 get 1 free and enjoy a discount!"
        expected_offers = [
            {"offer": "Discount", "emo_g": "💸"},
            {"offer": "Buy 1 Get 1", "emo_g": "🛍️"}
        ]
        result = EmoGAgent.identify_special_offers_with_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertEqual(result, expected_offers)

    def test_no_special_offers_with_emo_g(self):
        description = "This is a regular product description."
        expected_offers = []
        result = EmoGAgent.identify_special_offers_with_emo_g(description)
        print(f"Description: {description}")
        print(f"Detected Emo-G: {result}")
        self.assertEqual(result, expected_offers)

if __name__ == "__main__":
    unittest.main()