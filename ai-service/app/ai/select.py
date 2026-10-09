"""Gemini chọn 3 bộ: từ danh sách ứng viên hợp lệ (bộ ghép đồ sinh ra, đã chấm luật), Gemini chọn 3 bộ hợp
bối cảnh nhất và viết lý do + lời nhận xét. Code kiểm tra lại: mã phải có trong danh sách, không trùng,
lời nhận xét không bịa luật. Gemini lỗi -> lấy 3 bộ điểm cao nhất (khác kiểu áo) + câu viết sẵn.
"""
import json

from app.engine import pick_diverse
from app.models import StylistOutfit

from .explain import context_payload, fill_fallback, outfit_payload, trim_comment, valid_item
from .gemini import AIError, GeminiClient
from .prompts import load_prompt
from .schemas import select_schema


def why_fallback(o: StylistOutfit, ctx, catalog) -> str:
    """Lý do viết sẵn: nối dịp và các yếu tố bối cảnh đã biết."""
    parts = [catalog.name("occasions", o.state.occasion).lower()]
    for f in ("weather", "setting", "role"):
        label = catalog.context_label(f, getattr(ctx, f, None)) if ctx else ""
        if label:
            parts.append(label.lower())
    garment = catalog.name("garments", o.state.garment)
    return f"{garment} hợp với bối cảnh: {', '.join(p for p in parts if p)}."


def _fallback(candidates: list[StylistOutfit], ctx, catalog) -> list[StylistOutfit]:
    by_state = {c.state.model_dump_json(): c for c in candidates}
    picked = [by_state[s.model_dump_json()] for s in pick_diverse([c.state for c in candidates], 3)]
    for o in picked:
        fill_fallback(o, catalog)
        o.whyChosen = why_fallback(o, ctx, catalog)
    return picked


async def select_outfits(candidates: list[StylistOutfit], ctx, catalog, gemini: GeminiClient,
                         user_request: str | None = None, log=None) -> tuple[list[StylistOutfit], str]:
    """Trả về (3 bộ đã chọn, source). Mã outfitId được đánh lại thành o1, o2, o3 theo thứ tự chọn."""
    if len(candidates) <= 3:
        picked, source = _fallback(candidates, ctx, catalog), "fallback"
    else:
        payload = {"userRequest": user_request or "", "context": context_payload(ctx, catalog),
                   "candidates": [outfit_payload(c, catalog) for c in candidates]}
        try:
            raw, ms = await gemini.call_json(
                system=load_prompt("select"), contents=json.dumps(payload, ensure_ascii=False),
                schema=select_schema(), temperature=0.4)
            picked, source = _apply_picks(raw, candidates, ctx, catalog), "gemini"
            if log:
                await log("select", gemini.model, ms, "gemini", True)
        except AIError as e:
            if log:
                await log("select", gemini.model, None, "fallback", False, str(e)[:300])
            picked, source = _fallback(candidates, ctx, catalog), "fallback"

    for i, o in enumerate(picked):
        o.outfitId = f"o{i + 1}"
    return picked, source


def _apply_picks(raw: dict, candidates: list[StylistOutfit], ctx, catalog) -> list[StylistOutfit]:
    by_id = {c.outfitId: c for c in candidates}
    distinct = len({c.state.garment for c in candidates}) >= 3
    picked: list[StylistOutfit] = []
    for item in raw.get("picks", []):
        if not isinstance(item, dict):
            continue
        o = by_id.get(item.get("outfitId"))
        if not o or o in picked:                      # mã lạ hoặc chọn trùng: bỏ qua
            continue
        if distinct and o.state.garment in {p.state.garment for p in picked}:
            continue                                  # đã có kiểu áo này: để chỗ cho kiểu áo khác (đủ lựa chọn thì mới ép)
        if valid_item(item, o):
            o.title, o.comment, o.tip = item["title"].strip(), trim_comment(item["comment"]), item["tip"].strip()
        else:
            fill_fallback(o, catalog)
        o.whyChosen = (item.get("whyChosen") or "").strip()[:200] or why_fallback(o, ctx, catalog)
        picked.append(o)
        if len(picked) == 3:
            break
    if len(picked) < 3:                               # Gemini chọn thiếu: bù bằng bộ điểm cao nhất còn lại
        rest = [c for c in candidates if c not in picked]
        used = {p.state.garment for p in picked}
        fresh = [c for c in rest if c.state.garment not in used] if distinct else rest
        for o in _fallback(fresh, ctx, catalog) + _fallback(rest, ctx, catalog):
            if len(picked) == 3:
                break
            if o not in picked:
                picked.append(o)
    return picked
