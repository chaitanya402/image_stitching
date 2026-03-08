"""Agent to understand product descriptions and generate promotional content with appropriate icons."""

import re
from typing import Dict, List, Tuple
from src.services.description_agent import DescriptionAgent


class DescriptionBasedIconAgent:
    """
    Analyzes product descriptions and generates:
    - Discount information (percentage, type)
    - Product category/type
    - Suggested headline text
    - Suggested icons needed
    - Color scheme recommendations
    """

    @staticmethod
    def parse_description(description: str) -> Dict:
        """
        Parse a product description and extract key marketing information.
        
        Returns:
            Dict with keys:
            - discount_percent: int (extracted discount)
            - discount_text: str ("20% OFF")
            - product_type: str (category)
            - offer_type: str (discount, buy1get1, promotion)
            - headline: str (action text)
            - subtext: str (product focus)
            - cta: str (call-to-action)
            - suggested_icons: list of icon names (offer-specific)
            - color_scheme: dict with primary, secondary colors
            - template: str (template layout to use)
        """
        
        # Extract discount percentage
        discount_match = re.search(r'(\d+)\s*%\s*(?:off|discount|sale)', description, re.IGNORECASE)
        discount_percent = int(discount_match.group(1)) if discount_match else 0
        discount_text = f"{discount_percent}% OFF" if discount_percent else "SPECIAL OFFER"
        
        # Extract keywords for product type
        keywords = DescriptionAgent.extract_keywords(description)
        keywords_lower = [k.lower() for k in keywords]
        
        # Identify product category
        product_type = DescriptionBasedIconAgent._identify_product_type(keywords_lower, description.lower())
        
        # Identify offer type (discount, buy1get1, promotion)
        offer_type = DescriptionBasedIconAgent._identify_offer_type(description.lower(), keywords_lower)
        
        # Generate contextual text
        headline = f"GET {discount_text}" if discount_percent else "SPECIAL OFFER"
        subtext = DescriptionBasedIconAgent._generate_subtext(product_type, keywords_lower)
        cta = "SHOP NOW"
        
        # Suggest offer-specific icons
        suggested_icons = DescriptionBasedIconAgent._suggest_offer_icons(offer_type)
        
        # Color scheme based on product type
        color_scheme = DescriptionBasedIconAgent._get_color_scheme(product_type)
        
        # Select template based on offer type and product type
        template = DescriptionBasedIconAgent._select_template(offer_type, product_type)
        
        return {
            "discount_percent": discount_percent,
            "discount_text": discount_text,
            "product_type": product_type,
            "offer_type": offer_type,
            "headline": headline,
            "subtext": subtext,
            "cta": cta,
            "suggested_icons": suggested_icons,
            "color_scheme": color_scheme,
            "template": template,
            "keywords": keywords_lower
        }
        color_scheme = DescriptionBasedIconAgent._get_color_scheme(product_type)
        
        return {
            "discount_percent": discount_percent,
            "discount_text": discount_text,
            "product_type": product_type,
            "headline": headline,
            "subtext": subtext,
            "cta": cta,
            "suggested_icons": suggested_icons,
            "color_scheme": color_scheme,
            "keywords": keywords_lower
        }

    @staticmethod
    def _identify_product_type(keywords: List[str], description_lower: str) -> str:
        """Identify the product category from keywords."""
        
        categories = {
            "apparel": ["shirt", "dress", "pants", "jacket", "clothes", "wear", "apparel", "fashion"],
            "electronics": ["phone", "laptop", "computer", "tablet", "electronic", "gadget", "device"],
            "sports": ["gear", "equipment", "sports", "athletic", "shoes", "sneakers", "running"],
            "home": ["furniture", "home", "decor", "bed", "kitchen", "appliance"],
            "beauty": ["cosmetics", "skincare", "beauty", "makeup", "care", "lotion"],
            "luxury": ["premium", "luxury", "exclusive", "designer", "high-end"],
            "automotive": ["car", "cars", "vehicle", "rental", "booking", "automotive", "drive", "rent"],
            "services": ["service", "booking", "hotel", "travel", "tour", "experience"],
        }
        
        for category, terms in categories.items():
            if any(term in description_lower or term in keywords for term in terms):
                return category
        
        return "general"

    @staticmethod
    def _generate_subtext(product_type: str, keywords: List[str]) -> str:
        """Generate context-aware subtext based on product type."""
        
        subtexts = {
            "apparel": "ON ALL FASHION",
            "electronics": "ON TECH & GADGETS",
            "sports": "ON ALL GEAR",
            "home": "ON HOME ESSENTIALS",
            "beauty": "ON BEAUTY PRODUCTS",
            "luxury": "ON PREMIUM COLLECTION",
            "automotive": "ON ALL CAR RENTALS",
            "services": "ON ALL BOOKINGS",
        }
        
        return subtexts.get(product_type, "ON ALL PRODUCTS")

    @staticmethod
    def _suggest_icons(product_type: str, keywords: List[str]) -> List[str]:
        """Suggest which icons to display based on product type."""
        
        # Base icon - always discount badge
        icons = ["badge"]
        
        # Add product-specific icons
        icon_map = {
            "apparel": ["hanger", "shirt"],
            "electronics": ["phone", "laptop"],
            "sports": ["trophy", "weights"],
            "home": ["house", "furniture"],
            "beauty": ["star", "flower"],
            "luxury": ["crown", "gem"],
        }
        
        if product_type in icon_map:
            icons.extend(icon_map[product_type])
        else:
            icons.append("arrow")  # default secondary icon
        
        return icons

    @staticmethod
    def _get_color_scheme(product_type: str) -> Dict[str, Tuple[int, int, int]]:
        """
        Get premium color scheme based on product type.
        Returns RGB tuples for primary and accent colors.
        """
        
        schemes = {
            "apparel": {
                "primary": (25, 55, 120),      # Navy blue
                "accent": (255, 215, 0),       # Gold
                "background": (0, 0, 0, 180),  # Dark semi-transparent
            },
            "electronics": {
                "primary": (31, 78, 121),      # Deep blue
                "accent": (255, 153, 0),       # Orange
                "background": (0, 0, 0, 180),
            },
            "sports": {
                "primary": (25, 55, 120),      # Navy
                "accent": (255, 215, 0),       # Gold
                "background": (0, 0, 0, 180),
            },
            "home": {
                "primary": (70, 130, 180),     # Steel blue
                "accent": (255, 215, 0),       # Gold
                "background": (0, 0, 0, 180),
            },
            "beauty": {
                "primary": (138, 43, 226),     # Blue violet
                "accent": (255, 215, 0),       # Gold
                "background": (0, 0, 0, 180),
            },
            "luxury": {
                "primary": (25, 25, 112),      # Midnight blue
                "accent": (255, 215, 0),       # Gold
                "background": (0, 0, 0, 200),
            },
            "automotive": {
                "primary": (192, 57, 43),      # Energetic red
                "accent": (255, 215, 0),       # Gold
                "background": (0, 0, 0, 180),
            },
            "services": {
                "primary": (46, 125, 50),      # Green
                "accent": (255, 215, 0),       # Gold
                "background": (0, 0, 0, 180),
            },
        }
        
        return schemes.get(product_type, {
            "primary": (25, 55, 120),
            "accent": (255, 215, 0),
            "background": (0, 0, 0, 180),
        })

    @staticmethod
    def _identify_offer_type(description_lower: str, keywords: List[str]) -> str:
        """Identify the type of offer (discount, buy1get1, promotion)."""
        
        # Check for buy 1 get 1
        if "buy" in keywords and "get" in keywords:
            return "buy1get1"
        
        # Check for promotion/promo
        if any(word in keywords for word in ["promotion", "promo"]):
            return "promotion"
        
        # Check for discount/sale/off
        if any(word in keywords for word in ["discount", "sale", "off"]):
            return "discount"
        
        return "promotion"  # default

    @staticmethod
    def _suggest_offer_icons(offer_type: str) -> List[str]:
        """Suggest icons based on offer type."""
        
        offer_icons = {
            "discount": ["badge", "shopping_bag", "percent"],
            "buy1get1": ["badge", "gift_box", "plus"],
            "promotion": ["badge", "megaphone", "star"],
        }
        
        return offer_icons.get(offer_type, ["badge", "arrow"])

    @staticmethod
    def _select_template(offer_type: str, product_type: str) -> str:
        """
        Select the best template layout for the offer and product combination.
        
        Available templates:
        - 'badge_top_right': Badge top-right, arrow center (default)
        - 'badge_center': Large badge center (minimal/luxury products)
        - 'badge_left_side': Badge on left side (for wide products)
        - 'stacked': Badge on top, center (for tall products)
        """
        
        # Luxury products prefer centered badge
        if product_type == "luxury":
            return "badge_center"
        
        # Buy 1 Get 1 uses left-side for comparison
        if offer_type == "buy1get1":
            return "badge_left_side"
        
        # Promotions use stacked layout for visibility
        if offer_type == "promotion":
            return "stacked"
        
        # Default for regular discounts
        return "badge_top_right"

