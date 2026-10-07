"""Endpoint chỉ dùng khi phát triển (ENABLE_DEV_ROUTES=true): thử bước Hiểu ý, chạy bộ 20 câu test."""
import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.ai import parse_by_keywords
from app.api.deps import get_service, require_admin
from app.core.config import SERVICE_DIR
from app.services.stylist import StylistService

router = APIRouter(prefix="/dev", tags=["dev"])


class TextIn(BaseModel):
    text: str = Field(min_length=1, max_length=300)


@router.post("/understand", summary="Chỉ chạy bước Hiểu ý, so sánh Gemini với bắt từ khóa")
async def understand_only(body: TextIn, svc: StylistService = Depends(get_service)):
    intent, source = await svc.understand_only(body.text)
    return {"gemini_or_fallback": {"source": source, "intent": intent},
            "keywords": parse_by_keywords(body.text, svc.catalog)}


@router.post("/eval", dependencies=[Depends(require_admin)],
             summary="Chạy 20 câu trong tests/understand_cases.json (tốn khoảng 20 lượt gọi Gemini)")
async def run_eval(svc: StylistService = Depends(get_service)):
    from scripts.eval_understand import evaluate_cases
    cases = json.loads((SERVICE_DIR / "tests" / "understand_cases.json").read_text(encoding="utf-8"))
    return await evaluate_cases(cases, svc)
