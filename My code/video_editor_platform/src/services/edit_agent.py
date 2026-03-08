"""Agent responsible for applying decorations onto images/videos."""

from typing import List, Dict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os


class EditAgent:
    @staticmethod
    def apply_decorations(img: Image.Image, decorations: List[Dict]) -> Image.Image:
        """Return a new image with all decorations drawn onto it."""
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        draw = ImageDraw.Draw(img)
        w, h = img.size

        # before drawing decorations, optionally composite the source
        # image onto a promotional template if one exists.
        try:
            from config.base import Settings
            tpl_dir = Path(Settings().TEMPLATES_DIR)
            if tpl_dir.exists() and tpl_dir.is_dir():
                files = list(tpl_dir.glob("*"))
                if files:
                    tpl = Image.open(files[0]).convert("RGBA")
                    # scale the original image down to fit within template
                    max_w, max_h = tpl.width - 40, tpl.height - 40
                    ratio = min(max_w / img.width, max_h / img.height, 1.0)
                    resized = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
                    # position centered
                    x = (tpl.width - resized.width) // 2
                    y = (tpl.height - resized.height) // 2
                    tpl.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)
                    img = tpl
                    w, h = img.size
        except Exception:
            # silently ignore template problems
            pass

        # first, look for sale/discount related text to draw as a banner
        banner_texts = []
        normal_decs = []
        for deco in decorations:
            if deco.get("type") == "text":
                val = deco.get("value", "").upper()
                if any(k in val for k in ["SALE", "OFF", "%"]):
                    banner_texts.append(val)
                    continue
            normal_decs.append(deco)

        # draw banner if any
        if banner_texts:
            combined = " ".join(banner_texts)
            # banner height based on font size guess
            try:
                banner_font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=48)
            except Exception:
                banner_font = ImageFont.load_default()
            # compute text dimensions in a version-safe way
            try:
                text_w, text_h = banner_font.getsize(combined)
            except Exception:
                try:
                    bbox = draw.textbbox((0, 0), combined, font=banner_font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                except Exception:
                    text_w, text_h = (0, 0)
            pad = 20
            rect_h = text_h + pad * 2
            # draw semi-transparent rectangle at bottom
            rect_y0 = h - rect_h
            draw.rectangle([(0, rect_y0), (w, h)], fill=(255, 0, 0, 180))
            # text centered
            x = (w - text_w) // 2
            y = rect_y0 + pad
            draw.text((x, y), combined, font=banner_font, fill=(255, 255, 255, 255))
        # now draw other decorations normally
        for deco in normal_decs:
            typ = deco.get("type")
            if typ == "emoji":
                # draw emoji roughly top-right
                size = deco.get("font_size", 32)
                try:
                    font = ImageFont.truetype("AppleColorEmoji.ttf", size=size)
                except Exception:
                    font = ImageFont.load_default()
                text = deco.get("value", "")
                draw.text((w - size - 10, 10), text, font=font)
            elif typ == "text":
                size = deco.get("font_size", 24)
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
                except Exception:
                    font = ImageFont.load_default()
                text = deco.get("value", "")
                # place bottom-left
                draw.text((10, h - size - 10), text, font=font, fill=(255, 255, 255, 255))

        # after drawing, bump up color saturation to make output more vibrant
        try:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.3)  # 30% more color
        except Exception:
            pass

        return img
