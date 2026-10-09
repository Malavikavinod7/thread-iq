import datetime
import json
import logging
from typing import Any

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class ValidationAgent(BaseAgent):
    """
    Specialized agent for auditing AI-generated metadata, fashion copy, and quality scoring.
    Enforces business constraints, schema validity, safety checks, and color/attribute consistency.
    """

    PROFANITY_LIST = {"explicit", "fake", "counterfeit", "scam", "trash"}

    def validate(
        self,
        description_data: dict[str, Any],
        visual_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Main entry point for validating metadata quality and safety.
        """
        visual_data = visual_data or {}
        provider = self.get_active_provider()
        logger.info(f"ValidationAgent executing quality audit using provider: {provider}")

        errors: list[str] = []
        warnings: list[str] = []
        passed_safety = True

        title = str(description_data.get("title", "")).strip()
        description = str(description_data.get("description", "")).strip()
        tags = description_data.get("tags", [])

        # 1. Title validation
        if not title:
            errors.append("Title is missing or empty.")
        elif len(title) < 2:
            errors.append("Title failed quality validation minimum length requirement (< 2 chars).")
        elif len(title) > 250:
            warnings.append("Title is exceptionally long (> 250 chars).")

        # 2. Description validation
        if not description:
            errors.append("Product description is missing.")
        elif len(description) < 15:
            warnings.append("Product description is shorter than recommended (< 15 chars).")

        # 3. Tags validation
        if not tags or not isinstance(tags, list):
            warnings.append("No metadata tags provided.")

        # 4. Safety & profanity check
        combined_text = f"{title} {description} {' '.join(str(t) for t in tags)}".lower()
        for word in self.PROFANITY_LIST:
            if word in combined_text:
                errors.append(f"Safety check failed: forbidden term '{word}' detected.")
                passed_safety = False

        # 5. Visual consistency check
        if visual_data:
            color = str(visual_data.get("primary_color", "")).lower()
            if color and color not in ("classic", "none"):
                # check if color keywords match roughly
                color_part = color.split()[0]
                if color_part not in combined_text and color not in combined_text:
                    warnings.append(f"Visual color '{color}' is not mentioned in generated title or description.")

        is_valid = len(errors) == 0

        # Quality score calculation (base 1.0 minus penalties)
        score = 1.0
        score -= len(errors) * 0.35
        score -= len(warnings) * 0.05
        if not passed_safety:
            score -= 0.5
        quality_score = max(0.0, min(1.0, round(score, 2)))

        return {
            "is_valid": is_valid,
            "quality_score": quality_score,
            "passed_safety_checks": passed_safety,
            "errors": errors,
            "warnings": warnings,
            "audited_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "provider_used": provider,
        }
