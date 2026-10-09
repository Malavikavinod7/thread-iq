import hashlib
import json
import logging
import math
from typing import Any

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class EmbeddingAgent(BaseAgent):
    """
    Specialized agent for generating vector embeddings for fashion products.
    Enables semantic search, visual similarity, and recommendation workflows.
    """

    def embed(self, text: str, dimension: int = 128) -> dict[str, Any]:
        """
        Main entry point for generating dense vector embeddings from product text/metadata.
        """
        provider = self.get_active_provider()
        logger.info(f"EmbeddingAgent generating {dimension}-d vector using provider: {provider}")

        if provider in ("openai", "gemini"):
            llm_result = self._embed_with_api(provider, text, dimension)
            if llm_result:
                llm_result["provider_used"] = provider
                return llm_result

        # Try optional sentence-transformers provider
        try:
            from sentence_transformers import SentenceTransformer
            if not hasattr(self, "_st_model"):
                self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
            vec = self._st_model.encode(text).tolist()
            return {
                "vector": vec,
                "dimension": len(vec),
                "model_name": "all-MiniLM-L6-v2",
                "provider_used": "sentence-transformers",
            }
        except Exception:
            pass

        return self._embed_local(text, dimension)


    def _embed_with_api(self, provider: str, text: str, dimension: int) -> dict[str, Any] | None:
        """API client call for OpenAI or Gemini embeddings."""
        if provider == "openai" and self.openai_api_key:
            url = "https://api.openai.com/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "text-embedding-3-small",
                "input": text,
            }
            try:
                import httpx
                with httpx.Client(timeout=10.0) as client:
                    res = client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        vec = res.json()["data"][0]["embedding"]
                        return {
                            "vector": vec,
                            "dimension": len(vec),
                            "model_name": "text-embedding-3-small",
                        }
            except Exception as e:
                logger.warning(f"OpenAI embedding call failed: {e}")
        return None

    def _embed_local(self, text: str, dimension: int = 128) -> dict[str, Any]:
        """
        Deterministic, unit-normalized hashing vectorizer for semantic search representation.
        """
        clean_text = text.strip().lower()
        if not clean_text:
            clean_text = "empty fashion item"

        vec = [0.0] * dimension
        words = clean_text.split()
        for word in words:
            # Hash each word into vector buckets
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % dimension
            sign = 1.0 if ((h >> 8) & 1) == 1 else -1.0
            vec[idx] += sign

        # Compute L2 norm for normalization
        norm = math.sqrt(sum(val * val for val in vec))
        if norm > 0:
            vec = [round(val / norm, 6) for val in vec]
        else:
            vec[0] = 1.0

        return {
            "vector": vec,
            "dimension": dimension,
            "model_name": "local-threadiq-hashing-v1",
            "provider_used": "local",
        }
