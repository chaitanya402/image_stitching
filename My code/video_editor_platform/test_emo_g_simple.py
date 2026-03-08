#!/usr/bin/env python
"""Simple test for EmoG agent without heavy dependencies"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.services.emo_g_agent import EmoGAgent

def test_emo_g_basic():
    """Test basic EmoG identification"""
    print("\n" + "="*60)
    print("Testing EmoG Agent Module")
    print("="*60 + "\n")
    
    # Test 1: Positive sentiment with sale
    print("Test 1: Sale with discount")
    description1 = "Amazing sale with 50% off!"
    emo_g1 = EmoGAgent.identify_emo_g(description1)
    print(f"  Description: {description1}")
    print(f"  Detected Emo-G: {emo_g1}")
    print(f"  ✓ PASS\n" if emo_g1 else "  ✗ FAIL\n")
    
    # Test 2: Special offers with emoji
    print("Test 2: Discount with emoji mapping")
    description2 = "Huge discount on all items!"
    offers2 = EmoGAgent.identify_special_offers_with_emo_g(description2)
    print(f"  Description: {description2}")
    print(f"  Detected Offers: {offers2}")
    expected2 = [{"offer": "Discount", "emo_g": "💸"}]
    print(f"  ✓ PASS\n" if offers2 == expected2 else "  ✗ FAIL\n")
    
    # Test 3: Multiple keywords
    print("Test 3: Multiple keywords (gift + sale)")
    description3 = "New gift available with 20% off!"
    emo_g3 = EmoGAgent.identify_emo_g(description3)
    print(f"  Description: {description3}")
    print(f"  Detected Emo-G: {emo_g3}")
    print(f"  ✓ PASS\n" if len(emo_g3) > 0 else "  ✗ FAIL\n")
    
    # Test 4: Buy 1 Get 1
    print("Test 4: Buy 1 Get 1 offer")
    description4 = "Buy 1 get 1 free on all products!"
    offers4 = EmoGAgent.identify_special_offers_with_emo_g(description4)
    print(f"  Description: {description4}")
    print(f"  Detected Offers: {offers4}")
    expected4 = [{"offer": "Buy 1 Get 1", "emo_g": "🛍️"}]
    print(f"  ✓ PASS\n" if offers4 == expected4 else "  ✗ FAIL\n")
    
    # Test 5: Promotion
    print("Test 5: Promotion offer")
    description5 = "Limited time promotion available now."
    offers5 = EmoGAgent.identify_special_offers_with_emo_g(description5)
    print(f"  Description: {description5}")
    print(f"  Detected Offers: {offers5}")
    expected5 = [{"offer": "Promotion", "emo_g": "📣"}]
    print(f"  ✓ PASS\n" if offers5 == expected5 else "  ✗ FAIL\n")
    
    print("="*60)
    print("EmoG Agent Tests Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_emo_g_basic()
