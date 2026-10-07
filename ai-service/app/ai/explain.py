"""Lần gọi ②: Diễn giải. Viết lời stylist cho các bộ đồ đã được bộ luật chấm, rồi kiểm tra chống bịa.

Dùng chung cho: 3 thẻ gợi ý (/ai/stylist), nhận xét 1 bộ (/ai/explain) và so sánh phương án (/ai/review).
"""
import json
import re

from app.engine.rules import LEVEL_LABEL
from app.models import StylistOutfit

from .fallback import fallback_comment
from .gemini import AIError, GeminiClient
from .prompts import load_prompt
from .schemas import explain_schema

BANNED = re.compile(r"\bsai\b|cấm|không được|phản cảm", re.IGNORECASE)
MAX_COMMENT = 400


def context_payload(ctx, catalog) -> dict:
    """Bối cảnh dạng chữ tiếng Việt để đưa vào prompt (bỏ trường trống)."""
    if not ctx:
        return {}
    out = {
        "dịp": catalog.name("occasions", ctx.occasion),
        "phong cách": catalog.name("styles", ctx.style),
        "giới tính": {"nu": "nữ", "nam": "nam"}.get(ctx.gender, ""),
        "thời tiết": catalog.context_label("weather", ctx.weather),
        "nơi": catalog.context_label("setting", ctx.setting),
        "buổi": catalog.context_label("timeOfDay", ctx.timeOfDay),
        "vai trò": catalog.context_label("role", ctx.role),
        "màu thích": [catalog.name("colors", c) for c in ctx.preferredColors],
    }
    return {k: v for k, v in out.items() if v}


def outfit_payload(o: StylistOutfit, catalog) -> dict:
    s = o.state
    return {
        "outfitId": o.outfitId,
        "garment": f"{catalog.name('garments', s.garment)} ({'nữ' if s.gender == 'nu' else 'nam'})",
        "style": catalog.name("styles", s.style),
        "colors": [catalog.name("colors", c) for c in (s.colors.main, s.colors.bottom) if c],
        "pattern": catalog.name("patterns", s.pattern),
        "accessories": [catalog.name("accessories", a) for a in s.accessories],
        "colorScore": o.color.score,
        "colorNote": o.color.note,
        "rules": [{"ruleId": e.id, "level": LEVEL_LABEL[e.level], "reason": e.reason,
                   "suggestion": e.suggestion.text} for e in o.evaluations],
    }


def _payload(outfits: list[StylistOutfit], catalog, user_request: str | None, changes: dict | None,
             ctx=None) -> dict:
    items = []
    for o in outfits:
        items.append({**outfit_payload(o, catalog),
                      **({"changes": changes[o.outfitId]} if changes and o.outfitId in changes else {})})
    occ = outfits[0].state.occasion if outfits else None
    return {"userRequest": user_request or "", "occasion": catalog.name("occasions", occ),
            "context": context_payload(ctx, catalog), "outfits": items}


def trim_comment(text: str) -> str:
    text = text.strip()
    if len(text) <= MAX_COMMENT:
        return text
    cut = text[:MAX_COMMENT]
    return cut[: cut.rfind(".") + 1] or cut


def valid_item(item: dict, o: StylistOutfit) -> bool:
    allowed = {e.id for e in o.evaluations}
    rule_ids = set(item.get("ruleIds") or [])
    if not rule_ids <= allowed:                                  # nhắc tới luật không có trong dữ liệu
        return False
    risk_ids = {e.id for e in o.evaluations if e.level == "risk"}
    if risk_ids and not (risk_ids & rule_ids):                   # lờ đi cảnh báo nặng
        return False
    text = f"{item.get('title', '')} {item.get('comment', '')} {item.get('tip', '')}"
    if BANNED.search(text) or not item.get("comment", "").strip():
        return False
    return True


def fill_fallback(o: StylistOutfit, catalog) -> None:
    o.title, o.comment, o.tip = fallback_comment(o.state, o.evaluations, o.color.note, catalog)


async def explain(outfits: list[StylistOutfit], catalog, gemini: GeminiClient, user_request: str | None = None,
                  prompt: str = "explain", changes: dict | None = None, log=None, ctx=None) -> str:
    """Điền title/comment/tip vào từng bộ (sửa trực tiếp). Trả về source: gemini | fallback."""
    if not outfits:
        return "fallback"
    try:
        raw, ms = await gemini.call_json(
            system=load_prompt(prompt),
            contents=json.dumps(_payload(outfits, catalog, user_request, changes, ctx), ensure_ascii=False),
            schema=explain_schema(),
            temperature=0.7,
        )
    except AIError as e:
        if log:
            await log(prompt, gemini.model, None, "fallback", False, str(e)[:300])
        for o in outfits:
            fill_fallback(o, catalog)
        return "fallback"

    by_id = {it.get("outfitId"): it for it in raw.get("outfits", []) if isinstance(it, dict)}
    used_gemini = 0
    for o in outfits:
        item = by_id.get(o.outfitId)
        if item and valid_item(item, o):
            o.title, o.comment, o.tip = item["title"].strip(), trim_comment(item["comment"]), item["tip"].strip()
            used_gemini += 1
        else:
            fill_fallback(o, catalog)
    ok = used_gemini == len(outfits)
    if log:
        await log(prompt, gemini.model, ms, "gemini" if used_gemini else "fallback", ok,
                  None if ok else f"{len(outfits) - used_gemini} bộ dùng câu dự phòng")
    return "gemini" if used_gemini else "fallback"
