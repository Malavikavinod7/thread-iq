import json
import logging
import re
from typing import Any

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class VisionAgent(BaseAgent):
    """
    Specialized agent for visual feature extraction from product imagery and catalog signals.
    Extracts primary color, pattern, material look, category, fit style, and key visual attributes.
    """

    COLOR_KEYWORDS = {
        "navy": "Navy Blue",
        "blue": "Blue",
        "black": "Black",
        "white": "White",
        "red": "Crimson Red",
        "green": "Emerald Green",
        "beige": "Beige",
        "brown": "Chocolate Brown",
        "grey": "Charcoal Grey",
        "gray": "Charcoal Grey",
        "pink": "Pastel Pink",
        "yellow": "Mustard Yellow",
    }

    MATERIAL_KEYWORDS = {
        "denim": "Cotton / Denim",
        "jeans": "Cotton / Denim",
        "leather": "Genuine / Synthetic Leather",
        "silk": "Silk / Satin",
        "cotton": "100% Breathable Cotton",
        "wool": "Pure Wool",
        "linen": "Linen Weave",
        "knit": "Knitwear / Cashmere",
        "polyester": "Synthetic Polyester",
    }

    PATTERN_KEYWORDS = {
        "striped": "Striped",
        "stripe": "Striped",
        "plaid": "Plaid / Checkered",
        "check": "Plaid / Checkered",
        "floral": "Floral Print",
        "solid": "Solid",
        "graphic": "Graphic Printed",
    }

    CATEGORY_KEYWORDS = {
        "jeans": "Bottoms / Denim",
        "short": "Bottoms / Denim",
        "shorts": "Bottoms / Denim",
        "pant": "Bottoms / Trousers",
        "pants": "Bottoms / Trousers",
        "trouser": "Bottoms / Trousers",
        "trousers": "Bottoms / Trousers",
        "sweatpants": "Bottoms / Trousers",
        "shirt": "Apparel / Tops",
        "t-shirt": "Apparel / Tops",
        "tee": "Apparel / Tops",
        "sweater": "Apparel / Tops",
        "cardigan": "Apparel / Tops",
        "hoodie": "Apparel / Tops",
        "dress": "Apparel / Dresses",
        "skirt": "Apparel / Dresses",
        "jacket": "Outerwear / Jackets",
        "coat": "Outerwear / Coats",
        "shoe": "Footwear",
        "shoes": "Footwear",
        "boot": "Footwear",
        "boots": "Footwear",
        "sneaker": "Footwear / Sneakers",
        "bag": "Accessories / Bags",
        "scarf": "Apparel",
        "hat": "Apparel",
        "beret": "Apparel",
    }


    def analyze(self, product_name: str = "", image_url: str | None = None) -> dict[str, Any]:
        """
        Main entry point for analyzing product visual attributes.
        """
        provider = self.get_active_provider()
        logger.info(f"VisionAgent executing analysis using provider: {provider}")

        if provider in ("openai", "gemini"):
            llm_result = self._analyze_with_llm(provider, product_name, image_url)
            if llm_result:
                llm_result["provider_used"] = provider
                return llm_result

        return self._analyze_local(product_name, image_url)

    def _analyze_with_llm(
        self, provider: str, product_name: str, image_url: str | None
    ) -> dict[str, Any] | None:
        system_prompt = (
            "You are a fashion computer vision and visual intelligence agent. "
            "Extract visual attributes from product data into a strict JSON object with fields: "
            "primary_color (str), secondary_color (str), pattern (str), material_look (str), "
            "category (str), fit_style (str), visual_features (list of str), confidence_score (float 0-1)."
        )
        user_prompt = f"Product Title: {product_name}\nImage URL: {image_url or 'N/A'}"

        if provider == "openai":
            raw_res = self._call_openai_chat(user_prompt, system_prompt)
        else:
            raw_res = self._call_gemini_generate(user_prompt, system_prompt)

        if raw_res:
            try:
                data = json.loads(raw_res)
                return {
                    "primary_color": str(data.get("primary_color", "Classic Navy")),
                    "secondary_color": str(data.get("secondary_color", "None")),
                    "pattern": str(data.get("pattern", "Solid")),
                    "material_look": str(data.get("material_look", "Cotton")),
                    "category": str(data.get("category", "Apparel")),
                    "fit_style": str(data.get("fit_style", "Regular Fit")),
                    "visual_features": list(data.get("visual_features", ["High Quality Finish"])),
                    "confidence_score": float(data.get("confidence_score", 0.95)),
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM vision JSON output: {e}")
        return None

    def _analyze_local(self, product_name: str, image_url: str | None) -> dict[str, Any]:
        """Deterministic NLP/heuristic feature extractor for fashion items."""
        name_lower = product_name.lower()

        # Extract primary color
        primary_color = "Navy Blue"
        for kw, color in self.COLOR_KEYWORDS.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", name_lower):
                primary_color = color
                break

        # Extract material
        material_look = "Cotton / Denim"
        for kw, mat in self.MATERIAL_KEYWORDS.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", name_lower):
                material_look = mat
                break

        # Extract pattern
        pattern = "Solid"
        for kw, pat in self.PATTERN_KEYWORDS.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", name_lower):
                pattern = pat
                break

        # Extract category
        category = "Apparel"
        for kw, cat in self.CATEGORY_KEYWORDS.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", name_lower):
                category = cat
                break

        fit_style = "Regular Fit"
        if "slim" in name_lower:
            fit_style = "Slim Fit"
        elif "oversized" in name_lower or "loose" in name_lower:
            fit_style = "Oversized Fit"
        elif "tailored" in name_lower:
            fit_style = "Tailored Fit"

        features = ["High-quality stitching", f"{pattern} weave finish"]
        if "denim" in name_lower or "jeans" in name_lower:
            features.extend(["Reinforced seams", "5-pocket construction", "Durable wash finish"])
        elif "shirt" in name_lower:
            features.extend(["Button-down collar", "Adjustable cuffs"])

        return {
            "primary_color": primary_color,
            "secondary_color": "Accent Neutral",
            "pattern": pattern,
            "material_look": material_look,
            "category": category,
            "fit_style": fit_style,
            "visual_features": features,
            "confidence_score": 0.92,
            "provider_used": "local",
        }
