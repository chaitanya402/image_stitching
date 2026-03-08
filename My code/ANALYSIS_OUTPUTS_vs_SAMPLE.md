# Analysis: Generated Outputs vs. Sample Image

**Date**: March 8, 2026  
**Issue**: Generated images don't match the sample template at all

---

## 1. Repository Overview

This is a **GenAI-Powered Promotional Video Content Generator** that transforms:
- **Input**: Product image + Product description
- **Output**: AI-enhanced promotional images/videos for social media (Instagram, TikTok)

The core pipeline uses a **3-Agent Architecture**:
1. **Description-Based Icon Agent** - Extracts metadata from product description (discount %, keywords, product type)
2. **Image Generation Agent** - Creates/modifies images using AI models
3. **Carousel Video Generator** - Assembles images into MP4 videos with music, transitions, text

---

## 2. Two Image Generation Approaches in Your Code

### **Approach A: AI Image Generation** ❌ (Creates completely new images)
**Scripts**: `generate_promo_from_image.py`, `generate_images.py`, etc.

```
Input Image        Description              AI Model              Output Image
jackets.jpg  +  "20% off motorcycle"  →  FLUX/SDXL   →  Completely new AI image
 (reference)     gear and jackets"       (HF API)         (looks like photo, but generated)
```

**What happens**:
- Input image is used as **visual context reference only**
- Description is enhanced with AI-suggested keywords, icons, colors
- AI model generates an entirely **new photograph** matching the description
- Output has nothing to do with original image composition

**Example prompt generated**:
```
"featured product: Flat 20% off on all motorcycle accessories and jackets, 
featuring: motorcycle_jacket, leather, protective_gear, sale_badge, 
color scheme: black and silver, discount badge: 20%, professional product photography, 
studio lighting, 8k quality, high resolution"
```

**Supported Backends**:
- FLUX (local GPU) - Best quality but slow, requires GPU memory
- FLUX Spaces (free cloud) - Slower but reliable, free
- SDXL (HuggingFace remote) - Fast, decent quality, costs $$ 
- HF Free Options - Fastest, but lower quality

### **Approach B: Overlay/Template** ✓ (Preserves input image)
**Script**: `generate_professional_promo.py`

```
Input Image                             Output Image
jackets.jpg  (1215x2160)     →    Original image + promotional overlays:
                                   - Top banner (22% height): Dark overlay + "20% OFF" in gold
                                   - Bottom banner (25% height): Dark overlay + text
                                   - Center: 100% original product image preserved
```

**Layout Structure**:
```
┌─────────────────────────────────┐
│      TOP BANNER (22%)           │  ← Dark gray, gold accent line
│    "20% OFF" (Large Gold Text)  │
├─────────────────────────────────┤
│                                 │
│     ORIGINAL PRODUCT IMAGE      │  ← 100% preserved content (53%)
│        (Center Content)         │
│                                 │
├─────────────────────────────────┤
│    BOTTOM BANNER (25%)          │  ← Dark gray overlay  
│  "GET 20% OFF"                  │     "SHOP NOW" (white text)
│  Description wrapped text       │     Description text (white)
│  "SHOP NOW" CTA                 │
└─────────────────────────────────┘
```

**Design Details**:
- Background: `(10, 10, 10, 200)` - very dark gray, semi-transparent
- Accent line: `#DAA520` - goldenrod  
- Text: White for body text, `#FFD700` gold for headlines
- Fonts: Arial Bold for headlines, Arial regular for text
- Output: 398KB JPEG (professional ad-ready quality)

---

## 3. Comparison: Your Sample vs. Generated Outputs

### **Sample Image** (jacket_promo.jpg)
```
Expected Design (Assumption based on professional promo standards):
┌──────────────────────────────────────┐
│  Professional product composition    │
│  with lifestyle/luxury styling       │
│  Complete banner design integrated   │
│  into the image naturally            │
│  ✓ Balanced product + branding       │
│  ✓ Premium aesthetic                 │
└──────────────────────────────────────┘
```

### **Generated Output** (jackets_professional_20pct.jpg)
**If using Overlay Approach**:
```
Result: Original image + slapped-on banners
┌──────────────────────────────────────┐  
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← Top banner added (may not match sample style)
│ FROM CODE: "20% OFF" in gold text    │
├──────────────────────────────────────┤
│                                      │
│  Original jackets photo (preserved)  │  ← Looks identical to input
│                                      │
├──────────────────────────────────────┤
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← Bottom banner added
│ "GET 20% OFF" + "SHOP NOW"           │     (may clash with sample design)
└──────────────────────────────────────┘

❌ Mismatch: Sample uses cohesive design, overlay approach looks like stickers placed on top
```

**If using AI Generation Approach**:
```
Result: Completely new AI-generated image
┌──────────────────────────────────────┐  
│  AI-generated motorcycle jacket      │
│  photo that looks nothing like       │
│  your original input image           │
│  ✓ Generated from description        │
│  ✓ Brand new composition             │
│  ❌ Doesn't match your sample design │
└──────────────────────────────────────┘

❌ Mismatch: Sample is specific design, AI generates random new images
```

---

## 4. Root Cause Analysis

| Aspect | Sample Image | Generated Output | Mismatch |
|--------|--------------|------------------|----------|
| **Source** | Manually designed template | AI-generated OR overlay | ✗ Different design philosophy |
| **Composition** | Intentional, balanced layout | Random (AI) or preserved (overlay) | ✗ No template matching |
| **Style** | Professional, cohesive | Fragmented (overlay) or generic (AI) | ✗ Different aesthetic |
| **Text Placement** | Integrated into design | Banners added on top/bottom | ✗ Positioning doesn't match |
| **Color Scheme** | Matched to product | Hardcoded (overlay) or random (AI) | ✗ May not match |
| **Product Visibility** | Showcased elegantly | 100% preserved (overlay) or replaced (AI) | ✗ Different treatment |

---

## 5. Why the Mismatch Exists

### **Current Code Limitations**
1. **No Sample Template Matching**
   - Code doesn't analyze the sample image design
   - No extraction of sample's color scheme, layout, or styling
   - Code has no knowledge of what the sample looks like

2. **Hardcoded Design**
   - Overlay approach uses fixed dark gray + gold
   - Banner heights are fixed percentages (22%, 25%)
   - Text positioning follows rigid template
   - **No flexibility to match sample design**

3. **AI Generation is Non-Deterministic**
   - Each AI generation creates random new images
   - Every prompt generates different composition
   - No control over final composition

4. **No Style Transfer**
   - No mechanism to apply sample's visual style to new images
   - No color palette matching to sample
   - No layout pattern matching

### **Why Both Approaches Fail to Match Sample**
- **Overlay**: Looks like banner stickers on top of product image (not integrated like sample)
- **AI Generation**: Creates random new images (doesn't reproduce sample design at all)

---

## 6. What Each Script Actually Does

| Script | Approach | Input | Output | Matches Sample? |
|--------|----------|-------|--------|---|
| `generate_professional_promo.py` | Overlay | jackets.jpg + description | Input image + dark banners | ❌ No |
| `generate_promo_from_image.py` | AI Gen | jackets.jpg + description | New AI image | ❌ No |
| `generate_hybrid_promo.py` | Hybrid | jackets.jpg + description | Composite image | ❌ No |
| `generate_ai_poster.py` | AI Gen | jackets.jpg + description | AI poster | ❌ No |
| `generate_professional_clean_promo.py` | Template | description only | Clean design | ❌ No |
| `generate_professional_banner.py` | Template | description | Banner ad | ❌ No |

---

## 7. How to Fix: Make Outputs Match Sample

### **Option 1: Analyze Sample Image & Extract Design** (RECOMMENDED)
```python
# New approach:
1. Load sample_promo.jpg as reference
2. Extract:
   - Dominant colors/palette
   - Layout patterns (where is text, product, accents?)
   - Banner sizes and proportions
   - Font styles and sizes
   - Design symmetry/balance
3. Apply extracted style to new images
4. Result: Outputs that match sample aesthetic
```

### **Option 2: Reverse Engineer Sample Layout**
```python
# Manual approach:
1. Document sample design specifications:
   - Color palette: [list colors from sample]
   - Banner layout: [exact percentages]
   - Text positioning: [exact coordinates]
   - Font settings: [exact typeface, size]
2. Modify generate_professional_promo.py to use sample specs
3. Result: Outputs that match sample exactly
```

### **Option 3: Style Transfer (Advanced)**
```python
# AI-powered approach:
1. Train/use a style transfer model
2. Generate AI image from description
3. Apply sample image's style to generated image
4. Result: New content + sample aesthetic
```

---

## 8. Current Generation Status

**Files Generated Successfully**:
- `ai_promo_poster_apparel_20pct.jpg` (AI generation)
- `professional_promo_apparel.jpg` (Overlay)
- `hybrid_promo_apparel.jpg` (Hybrid)
- `promo_flat_20.jpg` (Flat design)
- `sdxl_hires_output.jpg` (High-res AI)
- `hf_free_inference.jpg` (Free tier)

**All matched?** ❌ None match the sample design perfectly

---

## 9. Recommended Next Steps

1. **Compare images visually**
   - Open sample_promo.jpg
   - Check if sample has banners or is pure product image
   - Note exact colors, text positions, layout

2. **Identify core issue**
   - Is sample a manually designed template?
   - Does sample have design integration needs?
   - Is your input image different from sample?

3. **Choose matching approach**
   - If sample is overlay-based: modify banner colors/positions to match
   - If sample is AI-generated: impossible to match (AI generates random images)
   - If sample is hybrid: combine both approaches with proper style

4. **Modify generation script**
   - Update colors to match sample palette
   - Adjust banner sizes/positions to match
   - Extract and apply sample's visual qualities

---

## Summary Table: Generation Methods

```
Method              Preserve Input?   AI Generated?   Matches Sample?   Speed
────────────────────────────────────────────────────────────────────────────
Overlay             YES              NO              ❌ Only if hardcoded   FAST
AI Generation       NO               YES             ❌ Random each time     SLOW
Hybrid              PARTIAL          YES             ❌ Usually not         MEDIUM
Template-Based      NO               NO              ❌ Generic design       FAST
Style Transfer      YES              MIXED           ✓ Possible            SLOW

Recommendation: Use Overlay approach but extract sample design specs first
```

---

**Next**: Please share what the sample image looks like, and I can help identify specific code changes needed.
