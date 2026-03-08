# Template-Based Promotional Image System with Offer-Specific Icons

## Architecture Overview

The new system uses **intelligent template selection** and **offer-specific icons** to generate diverse promotional images from product descriptions.

```
User Description
         ↓
DescriptionBasedIconAgent
         ├─ Extract offer type (discount/buy1get1/promotion)
         ├─ Identify product type
         ├─ Select appropriate template
         ├─ Suggest offer-specific icons
         └─ Choose color scheme
         ↓
TemplateSystem
         ├─ Template: badge_top_right
         ├─ Template: badge_center
         ├─ Template: badge_left_side
         └─ Template: stacked
         ↓
IconFactory
         ├─ Shopping Bag (discount)
         ├─ Gift Box (buy1get1)
         ├─ Megaphone (promotion)
         ├─ Star (highlight)
         ├─ Percent (math/discount)
         ├─ Plus (addition/bundle)
         └─ Crown (luxury)
         ↓
Promotional Image
```

## Offer Types & Associated Icons

### 1. Discount Offer
**Identifiers:** "discount", "sale", "off", "%" sign
**Icons:** Badge + Shopping Bag + Percent Sign
**Template:** `badge_top_right` (standard layout)
**Color Scheme:** Navy/Gold (professional)
**Example:** "flat 20% off on gear"

### 2. Buy 1 Get 1 Bundle
**Identifiers:** "buy 1 get 1", "buy", "get"
**Icons:** Badge + Gift Box + Plus Sign
**Template:** `badge_left_side` (comparison layout)
**Color Scheme:** Depends on product type
**Example:** "buy 1 get 1 on luxury home decor"

### 3. Promotion
**Identifiers:** "promotion", "promo", "limited"
**Icons:** Badge + Megaphone + Star
**Template:** `stacked` (prominent visibility)
**Color Scheme:** Bold/vibrant
**Example:** "promotion - 50% off on all electronics"

## Template Types

### Template 1: badge_top_right (Default)
- Badge positioned top-right corner
- Secondary icon(s) in center
- Best for: Standard discount offers
- Visual: Traditional e-commerce style

### Template 2: badge_center
- Large badge centered on image
- Minimal/luxury aesthetic
- Best for: Premium/luxury products
- Visual: Clean, minimal design

### Template 3: badge_left_side
- Badge on left side
- Secondary icon on right
- Best for: Comparison/bundle offers (Buy1Get1)
- Visual: Side-by-side comparison

### Template 4: stacked
- Badge at top center
- Secondary icons in row below
- Best for: Promotions (maximum visibility)
- Visual: Stacked/layered design

## Icon Factory Functions

### Available Icons

| Icon Name | Function | Use Case | Visual |
|-----------|----------|----------|--------|
| **shopping_bag** | `create_shopping_bag_icon()` | Discount/shopping | Bag with handle |
| **gift_box** | `create_gift_box_icon()` | Bundle/promotion | Box with ribbon |
| **megaphone** | `create_megaphone_icon()` | Promotion/announcement | Megaphone/horn |
| **star** | `create_star_icon()` | Highlight/premium | 5-pointed star |
| **percent** | `create_percent_icon()` | Discount math | % symbol |
| **plus** | `create_plus_icon()` | Addition/bundle | Plus/add sign |
| **crown** | `create_crown_icon()` | Luxury/premium | Crown with gems |

### Icon Factory Usage
```python
from src.utils.icon_factory import create_shopping_bag_icon, create_gift_box_icon

# Create icons with custom colors
color = (25, 55, 120, 255)  # Navy blue
shopping_icon = create_shopping_bag_icon(size=280, color=color)
gift_icon = create_gift_box_icon(size=280, color=color)
```

## Agent-Driven Template Selection

The `DescriptionBasedIconAgent` intelligently selects templates:

```python
from src.services.description_based_icon_agent import DescriptionBasedIconAgent

content = DescriptionBasedIconAgent.parse_description("buy 1 get 1 on luxury furniture")

# Returns:
# {
#     "offer_type": "buy1get1",
#     "product_type": "home",
#     "template": "badge_left_side",
#     "suggested_icons": ["badge", "gift_box", "plus"]
# }
```

### Template Selection Logic

```
Offer Type Detection:
├─ If "buy" + "get" → buy1get1
├─ If "promotion"/"promo" → promotion
├─ If "discount"/"off"/"sale" → discount
└─ Else → promotion (default)

Template Selection:
├─ If product_type == "luxury" → badge_center
├─ If offer_type == "buy1get1" → badge_left_side
├─ If offer_type == "promotion" → stacked
└─ Else → badge_top_right
```

## Tested Examples

### Example 1: Discount (Sports Product)
```
Input: "flat 20% off on gear"
├─ Offer Type: discount
├─ Product Type: sports
├─ Template: badge_top_right
├─ Icons: [badge, shopping_bag, percent]
├─ Headline: GET 20% OFF
├─ Subtext: ON ALL GEAR
└─ Color: Navy/Gold
```

### Example 2: Bundle (Home/Furniture)
```
Input: "buy 1 get 1 on luxury home decor"
├─ Offer Type: buy1get1
├─ Product Type: home
├─ Template: badge_left_side
├─ Icons: [badge, gift_box, plus]
├─ Headline: SPECIAL OFFER
├─ Subtext: ON HOME ESSENTIALS
└─ Color: Steel Blue/Gold
```

### Example 3: Promotion (Electronics)
```
Input: "promotion - 50% off on all electronics"
├─ Offer Type: promotion
├─ Product Type: electronics
├─ Template: stacked
├─ Icons: [badge, megaphone, star]
├─ Headline: GET 50% OFF
├─ Subtext: ON TECH & GADGETS
└─ Color: Deep Blue/Orange
```

## Usage

### Generate Single Image with Template System
```python
from generate_promo_template_system import generate_promotional_image_template

generate_promotional_image_template(
    input_image_path="path/to/product.jpg",
    description="flat 20% off on gear",
    output_path="output/promo.jpg"
)
```

### Batch Generate Multiple Templates
```python
descriptions = [
    "flat 20% off on gear",
    "buy 1 get 1 on furniture",
    "promotion - 50% off electronics"
]

for desc in descriptions:
    generate_promotional_image_template(
        "temp_images/product.jpg",
        desc,
        f"output/{desc[:20]}.jpg"
    )
```

## Key Features

✅ **Offer-Specific Icons** - Different icons for different offer types
✅ **Intelligent Templates** - Agent selects best layout
✅ **Dynamic Icon Creation** - 7+ drawable icon types
✅ **Color Coordination** - Icons match brand colors
✅ **Semantic Accuracy** - Icons semantically match offer type
✅ **No Hardcoding** - Fully parametrized system
✅ **Scalable** - Easy to add new templates/icons

## File Structure

```
video_editor_platform/
├── src/
│   ├── services/
│   │   └── description_based_icon_agent.py    # Enhanced with offer detection
│   └── utils/
│       └── icon_factory.py                     # Icon creation functions
├── generate_promo_parametrized.py              # Original (simple)
├── generate_promo_template_system.py            # New (template-based)
└── edited_images/
    ├── template_demo_0.jpg                      # Discount example
    ├── template_demo_1.jpg                      # Bundle example
    └── template_demo_2.jpg                      # Promotion example
```

## Extension Possibilities

### Add New Offer Types
```python
# In DescriptionBasedIconAgent._identify_offer_type()
if "flash" in keywords and "sale" in keywords:
    return "flash_sale"

# In _suggest_offer_icons()
"flash_sale": ["badge", "lightning", "star"]
```

### Add New Icons
```python
# In src/utils/icon_factory.py
def create_lightning_icon(size=150, color=(25, 55, 120, 255)):
    """Create lightning bolt icon"""
    # Implementation...
```

### Add New Templates
```python
# In generate_promo_template_system.py
def apply_template_custom(base_img, badge, icons_list, color_scheme):
    """Custom template layout"""
    # Implementation...

template_map["custom"] = apply_template_custom
```

## Comparison: Old vs New

| Feature | Old (Parametrized) | New (Template System) |
|---------|-------------------|----------------------|
| Icon Variety | 1 arrow icon | 7+ offer-specific icons |
| Templates | 1 fixed layout | 4 intelligent templates |
| Offer Recognition | Basic | Full (discount/bundle/promo) |
| Icon Selection | Static | Dynamic per offer |
| Scalability | Good | Excellent |
| Semantic Accuracy | Low | High |
| Visual Variety | Limited | High |

---

**Status:** ✅ Template system fully operational with 3 template types tested and verified
