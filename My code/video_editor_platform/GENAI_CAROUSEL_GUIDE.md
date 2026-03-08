# GenAI Carousel Video Generator - Quick Start Guide

## Overview

The new GenAI-based carousel generator replaces the template-based image stitching system with AI-powered image generation using Stable Diffusion.

**Key Changes:**
- ❌ **Old**: Product description → Template selection → Stitch image
- ✅ **New**: Product description → Generate prompt → AI generates image

## Two Options for Testing & Production

### Option B: HuggingFace Spaces (Testing - FREE) ✅ START HERE
```
Use this for: Testing, prototyping, understanding the workflow
Speed: 60-120 seconds per image
Cost: Free
Quality: Good (CPU-based)
Setup: No API key needed
```

### Option D: HuggingFace Inference API (Production - PAID) ⭐ LATER
```
Use this for: Production, high volume, speed critical
Speed: 5-30 seconds per image
Cost: ~$0.01 per image
Quality: Excellent (GPU-based)
Setup: Need HF API key + paid credits
```

---

## Quick Start: Test with Option B (Free)

### Step 1: Run the Test Script

```bash
cd "My code/video_editor_platform"
python batch_carousel_genai_generator.py
```

This will:
1. Generate 3 test product images using Stable Diffusion
2. Create a carousel video from the images
3. Save output as `test_carousel_genai.mp4`

**Expected time: 5-10 minutes** (due to CPU inference)

### Step 2: Use in Your Code

```python
from batch_carousel_genai_generator import GenAICarouselGenerator

# Create generator (Option B - free testing)
generator = GenAICarouselGenerator(backend="hf-spaces")

# Generate carousel from product descriptions
descriptions = [
    "Premium leather wallet with RFID protection. 20% OFF!",
    "Minimalist coffee table from sustainable wood.",
    "Vibrant summer dress in tropical print.",
]

success = generator.generate_carousel_from_descriptions(
    descriptions=descriptions,
    output_video_path="my_carousel.mp4",
    fixed_headline="New Collection",
    fixed_cta="Shop Now"
)
```

### Step 3: Generate from Custom Prompts (Advanced)

```python
# You can also provide direct prompts, bypassing description analysis
prompts = [
    "luxury leather wallet, professional product photography, studio lighting, 8k quality",
    "minimalist wooden coffee table, modern design, white background, high quality",
]

success = generator.generate_carousel_from_prompts(
    prompts=prompts,
    output_video_path="my_carousel.mp4"
)
```

---

## Production Setup: Upgrade to Option D

### Step 1: Get HuggingFace API Key

1. Go to: https://huggingface.co/settings/tokens
2. Create a new token (read access is sufficient)
3. Copy the token

### Step 2: Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:HUGGINGFACE_TOKEN = "your_token_here"
```

**Windows (Command Prompt):**
```cmd
set HUGGINGFACE_TOKEN=your_token_here
```

**Linux/Mac:**
```bash
export HUGGINGFACE_TOKEN="your_token_here"
```

### Step 3: Switch to Production Backend

```python
from batch_carousel_genai_generator import GenAICarouselGenerator

# CHANGE THIS:
# generator = GenAICarouselGenerator(backend="hf-spaces")

# TO THIS:
generator = GenAICarouselGenerator(backend="hf-inference")

# Rest of code stays the same!
success = generator.generate_carousel_from_descriptions(
    descriptions=descriptions,
    output_video_path="my_carousel.mp4"
)
```

**That's it!** Same code, 10x faster, production-ready.

---

## Architecture: How It Works

### Flow Diagram

```
Product Description
       ↓
PromptGeneratorAgent (analyzes + converts to prompt)
       ↓
Image Generator (HF Spaces or HF Inference API)
       ↓
Generated Image
       ↓
CarouselVideoGenerator (assembles images into video)
       ↓
Carousel Video Output
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **PromptGeneratorAgent** | `src/services/prompt_generator_agent.py` | Converts descriptions to detailed image prompts |
| **ImageGenerator (Base)** | `src/services/image_generator_base.py` | Abstract interface for all backends |
| **HF Spaces Generator** | `src/services/huggingface_spaces_generator.py` | Option B - Free testing backend |
| **HF Inference Generator** | `src/services/huggingface_inference_generator.py` | Option D - Production backend |
| **Factory** | `src/services/image_generator_factory.py` | Manage backend switching |
| **GenAI Carousel** | `batch_carousel_genai_generator.py` | Main orchestration class |

---

## Configuration & Customization

### Style Presets

The prompt generator includes built-in style presets:

```python
PromptGeneratorAgent.STYLE_PRESETS = {
    "professional": "professional product photography, studio lighting, white background...",
    "lifestyle": "lifestyle photography, natural lighting, modern aesthetic...",
    "luxury": "luxury product shot, premium styling, gold accents...",
    "vibrant": "vibrant colors, dynamic composition, eye-catching...",
    "minimalist": "minimalist design, clean composition, white space...",
    "casual": "casual lifestyle, friendly vibes, natural setting...",
}
```

Use with:
```python
generator.generate_carousel_from_descriptions(
    descriptions=descriptions,
    style="luxury",  # Force a specific style
    output_video_path="carousel.mp4"
)
```

### Image Quality / Speed Tradeoff

Adjust inference steps (higher = better quality but slower):

```python
# Fast but lower quality (good for testing)
success = generator.generate_carousel_from_descriptions(
    descriptions=descriptions,
    output_video_path="carousel.mp4",
    num_inference_steps=20  # default 30, best quality
)
```

### Cost Estimation (Option D)

```python
from src.services.huggingface_inference_generator import HuggingFaceInferenceGenerator

generator = HuggingFaceInferenceGenerator()
cost = generator.get_cost_estimate(num_images=10)
print(cost)
# Output: {'estimated_total_cost': '$0.10', 'cost_per_image': '$0.0100', ...}
```

---

## Troubleshooting

### "API key not found" Error
```
Error: HuggingFace API key required!
Solution: Set HUGGINGFACE_TOKEN environment variable
```

### "Model loading" (503 error) on Option D
```
The model is being loaded, retry in 30 seconds
Solution: Wait 30 seconds and try again
```

### Very slow generation on Option B
```
This is normal! HF Spaces uses CPU inference.
Expected time: 60-120 seconds per image
Solution: Either wait, or upgrade to Option D
```

### Out of memory error
```
Your GPU (Option D) ran out of memory
Solution: Reduce image resolution or use fewer steps
```

---

## Migration from Old Template System

### Old Code (Template-Based)
```python
from generate_promo_template_system import generate_promotional_image_template

generate_promotional_image_template(
    input_image_path="template.jpg",
    description="20% OFF leather wallets",
    output_path="promo.jpg"
)
```

### New Code (GenAI-Based)
```python
from batch_carousel_genai_generator import GenAICarouselGenerator

generator = GenAICarouselGenerator(backend="hf-spaces")
generator.generate_carousel_from_descriptions(
    descriptions=["20% OFF leather wallets"],
    output_video_path="carousel.mp4"
)
```

---

## Cost Analysis

### Option B (HF Spaces - Testing)
- **Cost**: $0
- **Time per image**: 60-120 seconds
- **Carousel of 5 images**: 5-10 minutes
- **Quality**: Good

### Option D (HF Inference API - Production)
- **Cost**: ~$0.01 per image
- **Time per image**: 5-30 seconds
- **Carousel of 5 images**: 30-150 seconds
- **Quality**: Excellent

**Example Monthly Costs (Option D):**
- 100 carousels × 5 images × $0.01 = $5/month
- 1,000 carousels × 5 images × $0.01 = $50/month

---

## Next Steps

1. ✅ **Test with Option B** (this guide)
2. ⏳ **Get HF API credentials** (for Option D)
3. ⏳ **Set up production monitoring** (once you scale)
4. ⏳ **Fine-tune prompts** for your products

---

## API Reference

### GenAICarouselGenerator

#### Constructor
```python
GenAICarouselGenerator(backend="hf-spaces", **backend_kwargs)
```

#### Methods

**generate_carousel_from_descriptions()**
```python
success = generator.generate_carousel_from_descriptions(
    descriptions: List[str],           # Product descriptions
    output_video_path: str,            # Output MP4 path
    style: Optional[str] = None,       # Style preset (professional, luxury, etc.)
    fixed_headline: str = "",          # Fixed headline for video
    fixed_subtext: str = "",           # Fixed subtext
    fixed_cta: str = "",               # Call-to-action text
    image_width: int = 1080,           # Image width
    image_height: int = 1080           # Image height
) -> bool
```

**generate_carousel_from_prompts()**
```python
success = generator.generate_carousel_from_prompts(
    prompts: List[str],                # Direct image prompts
    output_video_path: str,            # Output MP4 path
    fixed_headline: str = "",
    fixed_subtext: str = "",
    fixed_cta: str = "",
    image_width: int = 1080,
    image_height: int = 1080
) -> bool
```

### PromptGeneratorAgent

```python
# Generate a single prompt
prompt = PromptGeneratorAgent.generate_prompt(
    description: str,
    style: Optional[str] = None,
    include_discount_badge: bool = True
) -> str

# Generate multiple prompts
prompts = PromptGeneratorAgent.batch_generate_prompts(
    descriptions: List[str],
    style: Optional[str] = None
) -> List[str]

# Generate negative prompt (things to avoid)
negative = PromptGeneratorAgent.generate_negative_prompt(
    description: Optional[str] = None
) -> str
```

### ImageGeneratorFactory

```python
# Create generator
generator = ImageGeneratorFactory.create(
    backend: str = "hf-spaces",  # or "hf-inference"
    **kwargs
) -> ImageGenerator

# Print backend info
ImageGeneratorFactory.print_backend_info()
```

---

## Support & Documentation

- **Backend Info**: `ImageGeneratorFactory.print_backend_info()`
- **Test Prompts**: Check `batch_carousel_genai_generator.py` examples
- **HF Docs**: https://huggingface.co/docs/inference-api
- **Prompt Tips**: See `PromptGeneratorAgent` docstrings

