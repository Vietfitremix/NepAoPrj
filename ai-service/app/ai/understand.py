"""Lần gọi ①: Hiểu ý. Câu người dùng -> Intent (Gemini, hoặc bắt từ khóa khi Gemini lỗi)."""
from pydantic import ValidationError

from app.models import Intent

from .fallback import finalize_intent, parse_by_keywords
from .gemini import AIError, GeminiClient
from .prompts import load_prompt
from .schemas import intent_schema


async def understand(text: str, catalog, gemini: GeminiClient, log=None) -> tuple[Intent, str]:
    """Trả về (intent, source) với source = "gemini" hoặc "fallback"."""
    text = text.strip()[:600]                      # câu gõ nhanh hoặc phần gõ tự do của nhiều câu quiz
    try:
        raw, ms = await gemini.call_json(
            system=load_prompt("understand"),
            contents=f"Câu cần phân tích: \"{text}\"",
            schema=intent_schema(catalog),
            temperature=0.2,
        )
        intent = finalize_intent(Intent.model_validate(raw), catalog)
        if log:
            await log("understand", gemini.model, ms, "gemini", True)
        return intent, "gemini"
    except (AIError, ValidationError) as e:
        if log:
            await log("understand", gemini.model, None, "fallback", False, str(e)[:300])
        return parse_by_keywords(text, catalog), "fallback"
