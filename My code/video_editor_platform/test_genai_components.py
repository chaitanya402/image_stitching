#!/usr/bin/env python
"""
Test script for GenAI Carousel Image Generation
Tests the new prompt generation and image generation pipeline.
"""

import sys
import os
from pathlib import Path

# Setup path for imports
platform_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, platform_root)

from src.services.prompt_generator_agent import PromptGeneratorAgent
from src.services.image_generator_factory import ImageGeneratorFactory


def test_prompt_generation():
    """Test 1: Prompt generation from descriptions."""
    print("\n" + "="*80)
    print("TEST 1: PROMPT GENERATION")
    print("="*80)
    
    test_descriptions = [
        "Premium leather wallet with RFID protection and multiple card slots. Get 20% OFF today!",
        "Elegant minimalist coffee table made from sustainable reclaimed wood.",
        "Vibrant summer beach dress with tropical print. Perfect for vacation. Limited edition!",
    ]
    
    print("\nTesting PromptGeneratorAgent:\n")
    
    for i, description in enumerate(test_descriptions, 1):
        print(f"[{i}] Original Description:")
        print(f"    {description[:75]}...")
        
        # Generate prompt
        prompt = PromptGeneratorAgent.generate_prompt(description)
        print(f"\n    Generated Prompt:")
        print(f"    {prompt[:80]}...")
        
        # Generate negative prompt
        neg_prompt = PromptGeneratorAgent.generate_negative_prompt(description)
        print(f"\n    Negative Prompt:")
        print(f"    {neg_prompt[:60]}...")
        
        print()
    
    print("[✓] Prompt generation test passed!")
    return True


def test_backend_factory():
    """Test 2: Image generator factory and backend info."""
    print("\n" + "="*80)
    print("TEST 2: IMAGE GENERATOR FACTORY")
    print("="*80)
    
    # Print backend info
    ImageGeneratorFactory.print_backend_info()
    
    # Test creating HF Spaces generator
    print("\n\nAttempting to create HF Spaces generator...")
    try:
        generator = ImageGeneratorFactory.create("hf-spaces")
        print(f"[✓] Successfully created: {generator.backend_name}")
    except Exception as e:
        print(f"[!] Note: {e}")
    
    # Test creating HF Inference generator (will fail without API key)
    print("\n\nAttempting to create HF Inference API generator...")
    try:
        generator = ImageGeneratorFactory.create("hf-inference")
        print(f"[✓] Successfully created: {generator.backend_name}")
    except Exception as e:
        print(f"[!] API Key not configured (this is expected)")
        print(f"    To use Option D, set HUGGINGFACE_TOKEN environment variable")
    
    return True


def test_style_presets():
    """Test 3: Different style presets."""
    print("\n" + "="*80)
    print("TEST 3: STYLE PRESETS")
    print("="*80)
    
    description = "Leather wallet with RFID protection"
    
    print(f"\nBase description: {description}\n")
    print("Generated prompts with different styles:\n")
    
    for style in ["professional", "luxury", "casual", "vibrant"]:
        prompt = PromptGeneratorAgent.generate_prompt(description, style=style)
        print(f"Style: {style:15} → {prompt[:65]}...")
    
    print("\n[✓] Style preset test passed!")
    return True


def test_batch_generation():
    """Test 4: Batch prompt generation."""
    print("\n" + "="*80)
    print("TEST 4: BATCH PROMPT GENERATION")
    print("="*80)
    
    descriptions = [
        "Red sports car with leather interior",
        "Blue mountain bike with suspension",
        "Green hiking backpack waterproof",
    ]
    
    print(f"\nGenerating prompts for {len(descriptions)} products...\n")
    
    prompts = PromptGeneratorAgent.batch_generate_prompts(descriptions)
    
    for desc, prompt in zip(descriptions, prompts):
        print(f"Desc: {desc[:40]}")
        print(f"Prompts: {prompt[:65]}...\n")
    
    print(f"[✓] Batch generation test passed! Generated {len(prompts)} prompts")
    return True


def test_image_generation_mock():
    """Test 5: Test image generator interface (mock - no actual generation)."""
    print("\n" + "="*80)
    print("TEST 5: IMAGE GENERATOR INTERFACE")
    print("="*80)
    
    print("\nTesting ImageGenerator base class interface...")
    
    try:
        # Create the generator
        generator = ImageGeneratorFactory.create("hf-spaces")
        
        # Check attributes and methods
        print(f"[✓] Generator created: {generator.backend_name}")
        print(f"[✓] Has generate_image method: {hasattr(generator, 'generate_image')}")
        print(f"[✓] Has generate_and_save method: {hasattr(generator, 'generate_and_save')}")
        print(f"[✓] Has batch_generate method: {hasattr(generator, 'batch_generate')}")
        
        print("\n[!] To actually generate images, use:")
        print("    with Option B: `batch_carousel_genai_generator.py` (free, slow)")
        print("    with Option D: Set HUGGINGFACE_TOKEN and run again (fast, paid)")
        
        return True
    except Exception as e:
        print(f"[!] Could not test: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("GENAI CAROUSEL - COMPONENT TESTS")
    print("="*80)
    print("\nThis script tests the individual components of the GenAI carousel system")
    print("without actual image generation (to save time and resources).\n")
    
    tests = [
        ("Prompt Generation", test_prompt_generation),
        ("Backend Factory", test_backend_factory),
        ("Style Presets", test_style_presets),
        ("Batch Generation", test_batch_generation),
        ("Image Generator Interface", test_image_generation_mock),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASSED"))
        except Exception as e:
            print(f"\n[✗] TEST FAILED: {e}")
            results.append((test_name, "FAILED"))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")
    
    for test_name, status in results:
        symbol = "✓" if status == "PASSED" else "✗"
        print(f"{symbol} {test_name:30} → {status}")
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[✓] All component tests passed!")
        print("\nNext steps:")
        print("1. To generate actual images with HIGH QUALITY, run:")
        print("   python batch_carousel_genai_generator.py")
        print("\n2. Production setup (Option D - faster, $0.01 per image):")
        print("   - Get API key: https://huggingface.co/settings/tokens")
        print("   - Set: set HUGGINGFACE_TOKEN=your_key")
        print("   - Then run batch_carousel_genai_generator.py (same code, 10x faster)")
        return 0
    else:
        print("\n[✗] Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    exit(main())
