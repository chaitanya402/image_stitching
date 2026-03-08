# Parametrized Promotional Image Generator - Architecture

## Overview

The new architecture removes hardcoding by introducing an **agent-based system** that understands product descriptions and dynamically generates promotional content.

## Architecture Flow

```
User Input (Product Description)
         ↓
[DescriptionBasedIconAgent]
         ↓
    ├─ Extract discount %
    ├─ Identify product type
    ├─ Generate contextual text
    ├─ Suggest icons needed
    └─ Recommend color scheme
         ↓
[ParametrizedPromoGenerator]
         ↓
    ├─ Create icons (with colors)
    ├─ Compose layout
    ├─ Add text overlays
    └─ Save output image
         ↓
Output Image (fully personalized)
```

## Key Components

### 1. DescriptionBasedIconAgent (`src/services/description_based_icon_agent.py`)

**Purpose:** Analyze product descriptions and extract marketing intelligence

**Main Methods:**

- `parse_description(description: str) -> Dict`
  - Extracts discount percentage using regex
  - Identifies product category (apparel, electronics, sports, home, beauty, luxury)
  - Generates contextual headlines and subtexts
  - Suggests relevant icons
  - Recommends color scheme based on product type

- `_identify_product_type()` - Category detection
  - Scans keywords for product classification
  - Maps 6+ product categories
  - Falls back to "general" if no match

- `_generate_subtext()` - Context-aware subtitles
  - Returns product-specific subtext
  - Examples: "ON ALL GEAR", "ON TECH & GADGETS", "ON BEAUTY PRODUCTS"

- `_suggest_icons()` - Icon recommendations
  - Always includes discount badge
  - Adds product-specific icons per category
  - Provides fallback icons

- `_get_color_scheme()` - Premium color palettes
  - 6 predefined color schemes (navy/gold, deep blue/orange, etc.)
  - Returns RGB tuples for:
    - Primary color (badge)
    - Accent color (text)
    - Background color (overlays)

### 2. Parametrized Generator (`generate_promo_parametrized.py`)

**Purpose:** Create promotional images using agent-derived content

**Key Functions:**

- `generate_promotional_image(input_image_path, description, output_path)`
  - Takes any product image + any description
  - Uses agent to analyze description
  - Dynamically creates promotional overlay
  - Returns success boolean

- `create_discount_badge(size, discount_text, color_scheme)`
  - Accepts color scheme parameter
  - Renders badge in specified colors
  - No hardcoded colors

- `create_arrow_icon(size, color)`
  - Generic directional icon
  - Accepts color parameter

## Input Examples & Outputs

### Example 1: Sports Product
**Input:** `"flat 20% off on gear"`
- Product Type: `sports`
- Headline: `GET 20% OFF`
- Subtext: `ON ALL GEAR`
- Color Scheme: Navy/Gold
- Icons: Badge, Trophy, Weights

### Example 2: Fashion Product
**Input:** `"elegant leather shoes - 35% off on all footwear"`
- Product Type: `apparel`
- Headline: `GET 35% OFF`
- Subtext: `ON ALL FASHION`
- Color Scheme: Navy/Gold
- Icons: Badge, Hanger, Shirt

### Example 3: Electronics
**Input:** `"premium electronics - 40% discount on gadgets"`
- Product Type: `electronics`
- Headline: `GET 40% OFF`
- Subtext: `ON TECH & GADGETS`
- Color Scheme: Deep Blue/Orange
- Icons: Badge, Phone, Laptop

### Example 4: Special Offers
**Input:** `"luxury home decor - buy 1 get 1 on furniture"`
- Product Type: `home`
- Headline: `SPECIAL OFFER`
- Subtext: `ON HOME ESSENTIALS`
- Color Scheme: Steel Blue/Gold
- Icons: Badge, House, Furniture

## Supported Product Categories

| Category | Keywords | Subtext | Color Scheme |
|----------|----------|---------|--------------|
| **apparel** | shirt, dress, pants, jacket, clothes, wear | ON ALL FASHION | Navy/Gold |
| **electronics** | phone, laptop, computer, tablet, gadget | ON TECH & GADGETS | Deep Blue/Orange |
| **sports** | gear, equipment, athletic, shoes, running | ON ALL GEAR | Navy/Gold |
| **home** | furniture, home, decor, kitchen, appliance | ON HOME ESSENTIALS | Steel Blue/Gold |
| **beauty** | cosmetics, skincare, makeup, lotion | ON BEAUTY PRODUCTS | Blue Violet/Gold |
| **luxury** | premium, luxury, exclusive, designer | ON PREMIUM COLLECTION | Midnight Blue/Gold |

## Usage

### Basic Usage
```python
from generate_promo_parametrized import generate_promotional_image

# Any product, any discount
generate_promotional_image(
    input_image_path="path/to/product/image.jpg",
    description="your product description with discount info",
    output_path="output/promo.jpg"
)
```

### Command Line
```bash
python generate_promo_parametrized.py
# Uses default test with "flat 20% off on gear"
```

### Programmatic (with multiple products)
```python
descriptions = [
    "flat 20% off on gear",
    "50% discount on all electronics",
    "luxury collection - 30% off"
]

for desc in descriptions:
    generate_promotional_image(
        "temp_images/product.jpg",
        desc,
        f"output/promo_{i}.jpg"
    )
```

## Key Advantages

1. **No Hardcoding** - Text, colors, icons all derived from description
2. **Scalable** - Add new product categories by extending agent
3. **Intelligent** - Understands discount %, product type, offers
4. **Reusable** - Single script for all product types
5. **Maintainable** - Logic centralized in agent class
6. **Extensible** - Easy to add new icon types, color schemes, categories

## Future Enhancements

1. **Dynamic Icon Generation** - Create product-specific icons (beyond badge)
2. **Multi-badge Support** - Display multiple offer types simultaneously
3. **A/B Testing** - Generate multiple color/layout variations
4. **NLP Enhancement** - Use transformers for better product understanding
5. **Image-based Analysis** - Extract colors from product image for matching
6. **Batch Processing** - Handle multiple products in one run
7. **API Endpoint** - Expose as FastAPI route for web service

## Testing the Agent

```bash
# Test individual agent methods
python -c "
from src.services.description_based_icon_agent import DescriptionBasedIconAgent

desc = 'flat 20% off on gear'
result = DescriptionBasedIconAgent.parse_description(desc)
print(result)
"
```

## File Structure

```
video_editor_platform/
├── src/services/
│   ├── description_based_icon_agent.py    # Agent logic
│   └── ... (other agents)
├── generate_promo_parametrized.py         # Main generator
├── generate_icon_promo_image.py            # Legacy (hardcoded)
└── edited_images/
    ├── generated_promo.jpg
    ├── promo_0.jpg
    ├── promo_1.jpg
    └── promo_2.jpg
```

## Integration with Video Editor Platform

This can be integrated into the FastAPI application:

```python
# In src/api/routes.py
@app.post("/generate-promo")
def create_promotional_image(
    product_image: UploadFile,
    description: str
):
    """Generate promotional image from description"""
    from generate_promo_parametrized import generate_promotional_image
    
    # Save uploaded image
    # Call generator
    # Return generated image
```

---

**Next Phase:** Convert suggested icons list to actual drawable icons (trophy, weights, phone, laptop, etc.)
