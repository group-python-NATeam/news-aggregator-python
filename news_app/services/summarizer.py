# news_app/services/summarizer.py
import os
import logging
from typing import Optional

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

logger = logging.getLogger("crawler")  # reuse crawler logger if present

def _init_client() -> Optional["OpenAI"]:
    if OpenAI is None:
        logger.warning("OpenAI SDK not installed; summarizer disabled.")
        return None
    try:
        # OPENAI_API_KEY is read automatically from env by the SDK.
        client = OpenAI()
        logger.info("✅ OpenAI client initialized for summarizer.")
        return client
    except Exception as e:
        logger.warning(f"⚠️ Failed to init OpenAI client: {e}")
        return None

_client = _init_client()
_MODEL = os.environ.get("OPENAI_SUMMARY_MODEL", "gpt-4o-mini")
_TEMPERATURE = float(os.environ.get("OPENAI_SUMMARY_TEMPERATURE", "0.4"))
_MAX_TOKENS = int(os.environ.get("OPENAI_SUMMARY_MAX_TOKENS", "200"))

_SYSTEM_PROMPT = (
    "Bạn là một biên tập viên báo chí chuyên nghiệp. "
    "Hãy tóm tắt văn bản sau thành 2–3 câu tiếng Việt, súc tích, nêu rõ ý chính và sự kiện quan trọng. "
    "Chỉ trả về phần tóm tắt, không thêm lời dẫn."
)

def get_summary(text: str) -> str:
    """
    Return a short Vietnamese summary (2–3 sentences) for the given article body.
    Never raises: returns '' on failure.
    """
    if not text or not isinstance(text, str):
        return ""
    if _client is None:
        return ""
    try:
        # Chat Completions (stable and simple). You may migrate to Responses API later.
        resp = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=_TEMPERATURE,
            max_tokens=_MAX_TOKENS,
        )
        summary = (resp.choices[0].message.content or "").strip()
        return summary
    except Exception as e:
        logger.warning(f"❌ OpenAI summarization failed: {e}")
        return ""

__all__ = ["get_summary"]
