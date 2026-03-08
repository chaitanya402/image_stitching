# Carousel Video Generator - Usage Guide

## Overview

The **Carousel Video Generator** creates professional promotional carousel videos from multiple product descriptions. It intelligently generates individual promo images and combines them with smooth sliding transitions.

**Features:**
- ✅ Automatic promo image generation from product descriptions
- ✅ Sliding transition between images (4 seconds each)
- ✅ Infinite loop support
- ✅ Fixed text overlay matching template style
- ✅ 1080p @ 30fps MP4 output
- ✅ Semantic product recognition (apparel, electronics, sports, etc.)
- ✅ Template-based intelligent layout selection
- ✅ Category-specific color schemes and icons

---

## Quick Start

### 1. Simple Carousel from Descriptions

```python
from batch_carousel_generator import create_carousel_from_descriptions

descriptions = [
    "FLAT 20% off on all clothing and apparel",
    "Buy one get one free on all sports gear",
    "30% discount on electronics this week only",
]

create_carousel_from_descriptions(
    descriptions=descriptions,
    output_video_path="edited_videos/my_carousel.mp4",
    fixed_headline="MEGA SALE",
    fixed_subtext="LIMITED TIME",
    fixed_cta="SHOP NOW",
    base_image="temp_images/car rental.jpg"
)
```

**Output:** `my_carousel.mp4` (1920x1080, 30fps, 10-15MB)

---

## Advanced Usage

### 2. Generate Pre-Made Promo Images First

```python
from generate_promo_template_system import generate_promotional_image_template

# Generate individual promo images
descriptions = [
    "20% off on fashion",
    "Buy 1 Get 1 on sports",
]

for i, desc in enumerate(descriptions):
    generate_promotional_image_template(
        input_image_path="temp_images/car rental.jpg",
        description=desc,
        output_path=f"my_promos/promo_{i}.jpg"
    )
```

### 3. Create Video from Pre-Generated Promos

```python
from generate_carousel_video import CarouselVideoGenerator

gen = CarouselVideoGenerator(width=1920, height=1080, fps=30, image_duration=4)

gen.generate_carousel_video(
    image_paths=[
        "my_promos/promo_0.jpg",
        "my_promos/promo_1.jpg",
        "my_promos/promo_2.jpg",
    ],
    output_path="edited_videos/carousel.mp4",
    headline="EXCLUSIVE OFFERS",
    subtext="LIMITED TIME ONLY",
    cta="SHOP NOW",
    num_loops=1
)
```

---

## Command Line Usage

### Run Batch Generator

```bash
python batch_carousel_generator.py
```

This will generate a demo carousel with 4 product types:
- Apparel (20% off) - Blue theme
- Sports (Buy 1 Get 1) - Orange theme
- Electronics (30% off) - Purple theme
- Automotive (50% off) - Red theme

Output: `edited_videos/carousel_from_descriptions.mp4`

---

## Configuration Options

### CarouselVideoGenerator Parameters

```python
gen = CarouselVideoGenerator(
    width=1920,           # Video width (default: 1920 for 1080p)
    height=1080,          # Video height (default: 1080 for 1080p)
    fps=30,               # Frames per second (24/30/60)
    image_duration=4      # Seconds to show each image
)
```

### generate_carousel_video Parameters

```python
gen.generate_carousel_video(
    image_paths=[...],              # List of image file paths
    output_path="video.mp4",        # Output MP4 file
    headline="",                    # Text overlay (top)
    subtext="",                     # Text overlay (middle)
    cta="",                         # Call-to-action button text
    num_loops=1                     # Number of times to loop
)
```

### create_carousel_from_descriptions Parameters

```python
create_carousel_from_descriptions(
    descriptions=[...],             # Product descriptions
    output_video_path="video.mp4",  # Output file
    fixed_headline="",              # Fixed text across all frames
    fixed_subtext="",               # Fixed text across all frames
    fixed_cta="",                   # Fixed text across all frames
    base_image="temp_images/*.jpg"  # Base product image
)
```

---

## Generated Promo Image Details

### Product Categories Supported

| Category | Keywords | Color | Subtext |
|----------|----------|-------|---------|
| **Apparel** | clothing, apparel, fashion, dress, shirt | Blue | ON ALL FASHION |
| **Electronics** | electronics, tech, gadget, phone, computer | Purple | ON TECH & GADGETS |
| **Sports** | sports, gear, athletic, fitness, workout | Orange | ON ALL GEAR |
| **Home** | home, furniture, decor, kitchen | Brown | ON ALL HOME |
| **Beauty** | beauty, cosmetics, skincare, makeup | Pink | ON BEAUTY & CARE |
| **Luxury** | luxury, premium, exclusive, designer | Gold | ON LUXURY ITEMS |
| **Automotive** | car, rental, booking, vehicle, drive | Red | ON ALL CAR RENTALS |
| **Services** | service, booking, hotel, travel, tour | Green | ON ALL BOOKINGS |

### Offer Types

| Type | Trigger | Icon Set | Template |
|------|---------|----------|----------|
| **Discount** | "20% off", "discount", "sale" | Badge, Shopping Bag, Percent | badge_top_right |
| **Buy 1 Get 1** | "buy one get one", "BOGO" | Badge, Gift Box, Plus | badge_left_side |
| **Promotion** | "promotion", "special offer", "limited" | Badge, Megaphone, Star | stacked |

---

## Output Specs

### Video Format
- **Codec:** H.264 (MP4v)
- **Resolution:** 1920x1080 (1080p)
- **Frame Rate:** 30 fps
- **Duration per Image:** 4 seconds
- **Transition Duration:** ~1 second (30 frames)
- **File Size:** ~2.5MB per 10-second loop

### Text Overlay Style
All text overlays use the promotional template system style:
- **Headline:** Large bold text (top 1/3 of screen)
- **Subtext:** Medium text (middle of screen)
- **CTA Button:** Red background, white border, white text (bottom area)
- **Backgrounds:** Dark semi-transparent (0, 0, 0, 200)
- **Shadow Effect:** 3px text outline for visibility

---

## Example Workflows

### Workflow 1: Single Description to Video

```python
from batch_carousel_generator import create_carousel_from_descriptions

create_carousel_from_descriptions(
    descriptions=["50% off on electronics"],
    output_video_path="demo.mp4"
)
```

### Workflow 2: Multiple Products from CSV

```python
import csv
from batch_carousel_generator import create_carousel_from_descriptions

# Read descriptions from file
descriptions = []
with open("products.csv") as f:
    for row in csv.DictReader(f):
        descriptions.append(row['description'])

create_carousel_from_descriptions(
    descriptions=descriptions,
    output_video_path="carousel.mp4",
    fixed_headline="SALE NOW",
    fixed_cta="BUY TODAY"
)
```

### Workflow 3: Batch Videos for Multiple Brands

```python
from batch_carousel_generator import create_carousel_from_descriptions

brands = {
    "nike": ["20% off running shoes", "Buy 2 Get 1 on sports gear"],
    "apple": ["15% off on iphones", "Free accessories with iPad"],
}

for brand, descriptions in brands.items():
    create_carousel_from_descriptions(
        descriptions=descriptions,
        output_video_path=f"videos/{brand}_carousel.mp4",
        fixed_headline=f"{brand.upper()} OFFERS"
    )
```

---

## Troubleshooting

### Issue: Images look "dirty" or low quality
**Solution:** The enhanced template system applies:
- +15% contrast boost
- +10% color saturation
- +30% sharpness enhancement
- Text outline rendering for clarity

If you need more enhancement, edit `generate_promo_template_system.py` lines 230-234.

### Issue: Video codec error
**Solution:** Ensure OpenCV is installed with codec support:
```bash
pip install opencv-python
```

### Issue: Text overlay not visible
**Solution:** Check that your promo images have sufficient contrast. The text uses:
- White text (255, 255, 255)
- Dark background (0, 0, 0, 200)
- 3px outline for visibility

### Issue: Video file size too large
**Solution:** Adjust video duration or reduce fps:
```python
gen = CarouselVideoGenerator(
    width=1920, height=1080, 
    fps=24,               # Reduced from 30
    image_duration=3      # Reduced from 4
)
```

---

## File Locations

| Purpose | Path |
|---------|------|
| Generated Carousel Videos | `edited_videos/` |
| Generated Promo Images | `edited_images/` |
| Temp Carousel Promos | `temp_promo_carousel/` (auto-cleaned) |
| Base Product Images | `temp_images/` |

---

## Performance Metrics

- **Image Generation:** ~2-3 seconds per promo
- **Video Generation:** ~5-10 seconds per video
- **Total Time for 4 Promos → Video:** ~30-40 seconds
- **Output Size:** ~2.5-3MB per 10 seconds

---

## API Reference

### CarouselVideoGenerator

```python
class CarouselVideoGenerator:
    def __init__(width, height, fps, image_duration)
    def resize_image_to_fit(image, target_width, target_height)
    def create_sliding_transition(image1, image2, transition_frames)
    def add_text_overlay(frame, headline, subtext, cta, position_y_offset)
    def generate_carousel_video(image_paths, output_path, headline, subtext, cta, num_loops)
```

### Batch Generator

```python
def create_carousel_from_descriptions(
    descriptions: List[str],
    output_video_path: str,
    fixed_headline: str = "",
    fixed_subtext: str = "",
    fixed_cta: str = "",
    base_image: str = "temp_images/car rental.jpg"
) -> bool
```

---

## Next Steps

1. **Test with your own descriptions:** `python batch_carousel_generator.py`
2. **Customize base image:** Replace `temp_images/car rental.jpg`
3. **Modify text overlays:** Update headline, subtext, CTA
4. **Add to web platform:** Integrate into FastAPI endpoints
5. **Batch process:** Loop over CSV/database for production

---

## Support

For issues or feature requests, check:
- `ARCHITECTURE.md` - System design
- `TEMPLATE_SYSTEM.md` - Template documentation
- `PROMO_ARCHITECTURE.md` - Agent architecture
