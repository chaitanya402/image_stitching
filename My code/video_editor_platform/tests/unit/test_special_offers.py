"""Unit tests for identifying special offers in EmoGAgent."""

import unittest
import sys
import os

# Add the video_editor_platform directory to path
test_file_dir = os.path.dirname(os.path.abspath(__file__))
platform_root = os.path.abspath(os.path.join(test_file_dir, '../../'))
sys.path.insert(0, platform_root)

from src.services.emo_g_agent import EmoGAgent

class TestSpecialOffers(unittest.TestCase):
    def test_identify_discount(self):
        description = "Huge discount on all items!"
        expected_offers = ["Discount"]
        result = EmoGAgent.identify_special_offers(description)
        self.assertEqual(result, expected_offers)

    def test_identify_promotion(self):
        description = "Limited time promotion available now."
        expected_offers = ["Promotion"]
        result = EmoGAgent.identify_special_offers(description)
        self.assertEqual(result, expected_offers)

    def test_identify_buy_1_get_1(self):
        description = "Buy 1 get 1 free on all products!"
        expected_offers = ["Buy 1 Get 1"]
        result = EmoGAgent.identify_special_offers(description)
        self.assertEqual(result, expected_offers)

    def test_identify_multiple_offers(self):
        description = "Buy 1 get 1 free and enjoy a discount!"
        expected_offers = ["Discount", "Buy 1 Get 1"]
        result = EmoGAgent.identify_special_offers(description)
        self.assertEqual(result, expected_offers)

    def test_no_special_offers(self):
        description = "This is a regular product description."
        expected_offers = []
        result = EmoGAgent.identify_special_offers(description)
        self.assertEqual(result, expected_offers)

if __name__ == "__main__":
    unittest.main()