"""Agent that takes description context and generates emojis/text decorations."""

from typing import List, Dict


class CreativeAgent:
    @staticmethod
    def generate_decorations(keywords: List[str], sentiment: str) -> List[Dict]:
        """Based on keywords and sentiment produce a list of decoration objects.
        Each object may specify type: 'emoji' or 'text', value, and optional font size.
        """
        decorations = []
        # simple emoji mapping
        # treat explicit 'sale' or 'discount' or positive sentiment as sale
        # also numeric keywords or 'off' indicate discount
        discount_flag = False
        if "sale" in keywords or "discount" in keywords or sentiment == "positive":
            discount_flag = True
        for kw in keywords:
            if kw == "off" or kw.isdigit() or kw.endswith("%"):
                discount_flag = True
        if discount_flag:
            decorations.append({"type": "emoji", "value": "\U0001F389"})  # party popper
            decorations.append({"type": "text", "value": "SALE", "font_size": 32})
            # if there's a number we can add it explicitly
            for kw in keywords:
                if kw.isdigit() or kw.endswith("%"):
                    decorations.append({"type": "text", "value": kw.upper() + " OFF", "font_size": 28})
        elif sentiment == "negative":
            decorations.append({"type": "text", "value": "Oops", "font_size": 24})

        # if specific keywords appear, add emojis
        if "gift" in keywords:
            decorations.append({"type": "emoji", "value": "\U0001F381"})
        if "new" in keywords:
            decorations.append({"type": "text", "value": "NEW", "font_size": 28})

        return decorations
