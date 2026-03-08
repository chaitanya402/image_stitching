"""Agent to identify and display potential emo-g based on text input."""

from typing import List, Dict
from src.services.description_agent import DescriptionAgent
from src.services.creative_agent import CreativeAgent

class EmoGAgent:
    @staticmethod
    def identify_emo_g(description: str) -> List[str]:
        """Identify potential emo-g based on the description."""
        keywords = DescriptionAgent.extract_keywords(description)
        sentiment = DescriptionAgent.sentiment(description)
        decorations = CreativeAgent.generate_decorations(keywords, sentiment)
        print(f"Identified decorations: {decorations}")
        return [deco['value'] for deco in decorations if deco['type'] == 'emoji']

    @staticmethod
    def display_emo_g(emo_g_list: List[str]) -> None:
        """Display the list of potential emo-g."""
        print("Potential Emo-G:")
        for emo_g in emo_g_list:
            print(emo_g)

    @staticmethod
    def identify_special_offers(description: str) -> List[str]:
        """Identify special offers like discount, promotion, and buy 1 get 1 from the description."""
        keywords = DescriptionAgent.extract_keywords(description)
        special_offers = []

        if any(word in keywords for word in ["discount", "sale", "off"]):
            special_offers.append("Discount")

        if any(word in keywords for word in ["promotion", "promo"]):
            special_offers.append("Promotion")

        if "buy" in keywords and "1" in keywords and "get" in keywords:
            special_offers.append("Buy 1 Get 1")

        return special_offers

    @staticmethod
    def identify_special_offers_with_emo_g(description: str) -> List[Dict[str, str]]:
        """Identify special offers and their corresponding emo-g."""
        keywords = DescriptionAgent.extract_keywords(description)
        offers_with_emo_g = []

        if any(word in keywords for word in ["discount", "sale", "off"]):
            offers_with_emo_g.append({"offer": "Discount", "emo_g": "💸"})

        if any(word in keywords for word in ["promotion", "promo"]):
            offers_with_emo_g.append({"offer": "Promotion", "emo_g": "📣"})

        if "buy" in keywords and "1" in keywords and "get" in keywords:
            offers_with_emo_g.append({"offer": "Buy 1 Get 1", "emo_g": "🛍️"})

        return offers_with_emo_g