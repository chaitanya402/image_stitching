"""
BannerContentAgent
==================
Uses a HuggingFace LLM (via InferenceClient) to generate all promotional
banner copy from a plain-text product description.

Replaces every hardcoded rule in the old DescriptionBasedIconAgent:
  - "GET X% OFF"          → LLM-generated catchy headline
  - product_type.title()  → LLM-generated product tagline
  - raw description text  → LLM-generated bullet offer points

Falls back to lightweight phrase extraction if the LLM call fails.
"""

import json
import os
import re
import requests
from pathlib import Path


def _load_api_key() -> str:
    config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        token = cfg.get("huggingface", {}).get("api_token", "")
        if token and token != "your_token_here":
            return token
    except Exception:
        pass
    return os.environ.get("HF_TOKEN", "")


class BannerContentAgent:
    """
    Calls a HuggingFace LLM to extract structured promotional copy from a
    product description. Tries multiple models / API styles gracefully.

    Returns a dict with:
      banner_headline  — 3-6 word punchy headline for the top banner strip
      banner_tagline   — 1 short descriptive line for below the headline
      offer_points     — list of 2-3 concise bullet points (no discount %)
      badge_label      — text for the circular badge, e.g. "20% OFF"
    """

    # Models tried in order; uses chat completions via direct HTTP
    MODELS = [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "Qwen/Qwen2.5-1.5B-Instruct",
        "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    ]

    def __init__(self):
        self._api_key = _load_api_key()

    def generate(self, description: str, discount: int) -> dict:
        """Main entry point. Calls LLM; falls back to phrase extraction on failure."""
        for model in self.MODELS:
            try:
                result = self._call_chat(model, description, discount)
                if result:
                    print(f"  [BannerContentAgent] Content from LLM ({model.split('/')[-1]})")
                    return result
            except Exception as e:
                print(f"  [BannerContentAgent] {model.split('/')[-1]} failed: {e}")

        print("  [BannerContentAgent] Using intelligent phrase extraction")
        return self._fallback(description, discount)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _call_chat(self, model: str, description: str, discount: int) -> dict | None:
        """POST to HF /v1/chat/completions endpoint (works for instruct models)."""
        discount_note = (
            f"There is a {discount}% discount. Do NOT mention the discount percentage in "
            "headline, tagline, or offer_points — it will appear separately in a badge. "
            if discount else ""
        )
        system_msg = "You are a professional retail copywriter. Reply ONLY with valid JSON, no markdown."
        user_msg = (
            f"Extract concise promotional banner copy from this product description. "
            f"{discount_note}"
            f'Description: "{description}" '
            f"Return exactly: "
            f'{{"banner_headline":"<3-6 word catchy headline about the product>",'
            f'"banner_tagline":"<1 short descriptive line about product/service>",'
            f'"offer_points":["<feature 1>","<feature 2>","<feature 3>"],'
            f'"badge_label":"{f"{discount}% OFF" if discount else ""}"}}'
        )
        url = f"https://router.huggingface.co/hf-inference/models/{model}/v1/chat/completions"
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg},
            ], "max_tokens": 300, "temperature": 0.4},
            timeout=40,
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        return self._parse_json(raw, description, discount)

    def _parse_json(self, raw: str, description: str, discount: int) -> dict | None:
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return None

        headline = str(data.get("banner_headline", "")).strip()[:60]
        tagline  = str(data.get("banner_tagline", "")).strip()[:100]
        points   = [str(p).strip() for p in data.get("offer_points", []) if str(p).strip()][:3]
        badge    = str(data.get("badge_label", "")).strip()

        if not headline:
            return None

        return {
            "banner_headline": headline,
            "banner_tagline":  tagline,
            "offer_points":    points,
            "badge_label":     badge or (f"{discount}% OFF" if discount else ""),
        }

    def _fallback(self, description: str, discount: int) -> dict:
        """
        Smart phrase extraction fallback:
        1. Pull the product focus out of the discount clause ("off on <product>")
        2. Strip connectives from remaining fragment TEXT (not skip fragments)
        3. Filter CTAs ("visit our shop", "shop now") — never use as headline/tagline
        """
        # ---- Step 1: Extract product focus from "flat X% off on <product>" ----
        product_match = re.search(
            r'(?i)\d+%\s*off\s+on\s+(.+?)(?:\s*,|$)', description
        )
        product_focus = product_match.group(1).strip() if product_match else ""

        # ---- Step 2: Strip discount clause, get remaining text ----
        clean = re.sub(r'(?i)flat\s+\d+%\s*off\s+on\b[^,]*', '', description)
        clean = re.sub(r'(?i)\b\d+%\s*off\b[^,]*', '', clean).strip(" ,.")

        # ---- Step 3: Split into fragments ----
        raw_frags = [p.strip().rstrip('.,') for p in re.split(r'[,;]+', clean) if p.strip()]

        # ---- Step 4: Strip leading connectives from fragment TEXT ----
        _conn = re.compile(r'^(?:and|or|but|also|plus|with|for|to)\s+', re.IGNORECASE)
        frags = [_conn.sub('', f).strip() for f in raw_frags if f.strip()]
        frags = [f for f in frags if len(f) > 3]

        # ---- Step 5: Separate CTAs from feature phrases ----
        _cta = re.compile(
            r'^(?:visit|shop|buy|order|click|call|find|explore|discover|get yours)\b',
            re.IGNORECASE
        )
        features = [f for f in frags if not _cta.match(f)]

        # ---- Step 6: Build headline from product focus (most relevant noun phrase) ----
        _stop = {'and', 'or', 'the', 'a', 'an', 'of', 'in', 'for', 'with', 'on', 'at', 'to', 'by'}

        def _short_headline(text: str) -> str:
            """Strip connectives, keep max 3 meaningful words, return UPPER."""
            words = [w for w in re.split(r'\s+', text) if w.lower() not in _stop]
            return ' '.join(w.upper() for w in words[:3]) or 'EXCLUSIVE OFFER'

        if product_focus:
            headline = _short_headline(product_focus)
            # tagline uses the cleaned words (max 5) in title-case
            clean_words = [w for w in re.split(r'\s+', product_focus) if w.lower() not in _stop]
            tagline = ' '.join(clean_words[:5]).title()
        elif features:
            headline = _short_headline(features[0])
            tagline = features[0].capitalize()
        else:
            headline = 'EXCLUSIVE OFFER'
            tagline = ''

        # ---- Step 7: Offer points — features only, up to 3 ----
        points = [f.capitalize() for f in features[:3]]
        if not points and product_focus:
            points = [product_focus.capitalize()]

        return {
            'banner_headline': headline,
            'banner_tagline':  tagline,
            'offer_points':    points,
            'badge_label':     f'{discount}% OFF' if discount else '',
        }

