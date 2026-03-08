"""Simple agent to extract context from a product description."""

import re
from typing import List


class DescriptionAgent:
    @staticmethod
    def extract_keywords(description: str) -> List[str]:
        """Return lowercased keywords found in description."""
        if not description:
            return []
        # split on non-word chars and filter
        words = re.findall(r"\w+", description.lower())
        # remove common stopwords for simplicity
        stop = {"the", "and", "a", "an", "for", "with", "of"}
        return [w for w in words if w not in stop]

    @staticmethod
    def sentiment(description: str) -> str:
        """Very naive sentiment: positive if contains good words, negative if bad."""
        if not description:
            return "neutral"
        pos = ["good", "great", "amazing", "sale", "discount", "off"]
        neg = ["bad", "poor", "cheap", "expensive"]
        low = description.lower()
        # also treat numeric percentage as positive signal
        if any(p in low for p in pos) or re.search(r"\d+%", low):
            return "positive"
        if any(n in low for n in neg):
            return "negative"
        return "neutral"
