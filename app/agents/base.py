import logging
from typing import Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for ThreadIQ specialized AI agents.
    Handles provider selection (OpenAI, Gemini, Local) and fallback mechanisms.
    """

    def __init__(
        self,
        ai_provider: str | None = None,
        openai_api_key: str | None = None,
        gemini_api_key: str | None = None,
    ):
        self.ai_provider = ai_provider or settings.ai_provider
        self.openai_api_key = openai_api_key or settings.openai_api_key
        self.gemini_api_key = gemini_api_key or settings.gemini_api_key

    def get_active_provider(self) -> str:
        if self.ai_provider == "openai" and self.openai_api_key:
            return "openai"
        if self.ai_provider == "gemini" and self.gemini_api_key:
            return "gemini"
        if self.ai_provider == "auto":
            if self.openai_api_key:
                return "openai"
            if self.gemini_api_key:
                return "gemini"
        return "local"

    def _call_openai_chat(self, prompt: str, system_prompt: str = "") -> str | None:
        """Call OpenAI Chat Completions API via HTTPX."""
        if not self.openai_api_key:
            return None
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "gpt-4o",
            "messages": messages,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"OpenAI API returned status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
        return None

    def _call_gemini_generate(self, prompt: str, system_prompt: str = "") -> str | None:
        """Call Google Gemini API via HTTPX."""
        if not self.gemini_api_key:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                logger.warning(f"Gemini API returned status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
        return None
