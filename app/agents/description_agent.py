import json
import logging
from typing import Any

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class DescriptionAgent(BaseAgent):
    """
    Specialized agent for generating enriched fashion catalog copy, title, description,
    key feature bullet points, and SEO metadata.
    """

    def generate(
        self,
        product_name: str = "",
        visual_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Main entry point for generating enriched fashion product copy.
        """
        visual_data = visual_data or {}
        provider = self.get_active_provider()
        logger.info(f"DescriptionAgent executing copy generation using provider: {provider}")

        if provider in ("openai", "gemini"):
            llm_result = self._generate_with_llm(provider, product_name, visual_data)
            if llm_result:
                llm_result["provider_used"] = provider
                return llm_result

        return self._generate_local(product_name, visual_data)

    def _generate_with_llm(
        self,
        provider: str,
        product_name: str,
        visual_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        system_prompt = (
            "You are an expert e-commerce fashion copywriter and catalog optimization specialist. "
            "Generate structured product copy in JSON format with fields: "
            "title (str), short_description (str), description (str), key_features (list of str), "
            "tags (list of str), seo_keywords (str), target_audience (str)."
        )
        user_prompt = (
            f"Product Name: {product_name}\n"
            f"Visual Attributes: {json.dumps(visual_data)}"
        )

        if provider == "openai":
            raw_res = self._call_openai_chat(user_prompt, system_prompt)
        else:
            raw_res = self._call_gemini_generate(user_prompt, system_prompt)

        if raw_res:
            try:
                data = json.loads(raw_res)
                return {
                    "title": str(data.get("title", product_name or "Fashion Item")),
                    "short_description": str(data.get("short_description", "")),
                    "description": str(data.get("description", "")),
                    "key_features": list(data.get("key_features", [])),
                    "tags": list(data.get("tags", [])),
                    "seo_keywords": str(data.get("seo_keywords", "")),
                    "target_audience": str(data.get("target_audience", "General")),
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM description JSON output: {e}")
        return None

    def _generate_local(
        self,
        product_name: str,
        visual_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Deterministic fashion copy synthesis engine."""
        color = visual_data.get("primary_color", "Classic")
        pattern = visual_data.get("pattern", "Solid")
        material = visual_data.get("material_look", "Cotton")
        category = visual_data.get("category", "Apparel")
        fit = visual_data.get("fit_style", "Regular Fit")

        base_title = product_name.strip() if product_name else "Fashion Item"
        if color.lower() not in base_title.lower():
            enriched_title = f"{color} {base_title}"
        else:
            enriched_title = base_title

        short_desc = (
            f"Elevate your daily style with this premium {color.lower()} {category.lower()} "
            f"crafted with a high-quality {material.lower()} finish."
        )

        full_desc = (
            f"Crafted for versatile everyday wear, this {enriched_title} combines contemporary aesthetics "
            f"with exceptional durability. Featuring a {pattern.lower()} pattern and a flattering {fit.lower()}, "
            f"it offers unmatched comfort whether dressed up for formal occasions or worn casually."
        )

        features = [
            f"Premium {material} construction",
            f"{color} shade with a {pattern.lower()} texture",
            f"Designed with a {fit} for all-day comfort",
            "Easy care and color-fast durability",
        ]

        tags = list({
            color.lower(),
            pattern.lower(),
            category.lower().split("/")[0].strip(),
            "fashion",
            "apparel",
            "catalog",
        })

        seo_keywords = f"{color} {base_title}, premium {material} {category}, fashion catalog"

        return {
            "title": enriched_title,
            "short_description": short_desc,
            "description": full_desc,
            "key_features": features,
            "tags": tags,
            "seo_keywords": seo_keywords,
            "target_audience": "Unisex / Contemporary",
            "provider_used": "local",
        }
