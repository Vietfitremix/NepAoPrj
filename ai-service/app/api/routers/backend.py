"""Bridge the Spring catalog/JSON contract to the existing AI pipeline.

Catalogs are request-scoped: Spring remains the source of truth for codes and
supported accessories. No dependency on the unrelated catalog PostgreSQL schema.
"""
import json
import re
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.ai import AIError
from app.ai.fallback import norm, parse_by_keywords
from app.ai.select import select_outfits
from app.api.deps import client_ip, get_service
from app.catalog import Catalog
from app.catalog.sources import load_ui_data
from app.catalog.backend_bridge import enrich_catalog, native_catalog
from app.core.config import get_settings
from app.engine import score_outfit
from app.engine.variety import accessory_sets, bottom_and_shoes, diverse_shortlist
from app.models import Colors, Intent, OutfitState, StylistOutfit
from app.services.stylist import StylistService

router = APIRouter(tags=["backend integration"])


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outfitCode: str
    colorCode: str
    styleCode: str
    eventCode: str
    accessories: list[str] = Field(default_factory=list, max_length=10)
    wardrobe: dict | None = None
    context: Intent | None = None


class BackendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1, max_length=2000)
    referenceData: dict
    culturalContext: dict[str, list[dict]] = Field(default_factory=dict)
    city: str | None = None
    eventCode: str | None = None
    styleCode: str | None = None
    character: Literal['male', 'female'] | None = None
    weather: dict | None = None
    currentLook: Selection | None = None


def request_catalog(ref: dict, scoring: dict | None = None) -> Catalog:
    if scoring is None:
        scoring = load_ui_data(get_settings().data_dir)[2]  # standalone test/local mode
    try:
        colors = {r["code"]: {"id": r["code"], "name": r["name"], "hex": r["hexCode"]}
                  for r in ref["colors"]}
        styles = {r["code"]: {"id": r["code"], "name": r["name"]} for r in ref["styles"]}
        occasions = {r["code"]: {"id": r["code"], "name": r["name"]} for r in ref["events"]}
        accessories = {r["code"]: {"id": r["code"], "name": r["name"], "slot": r["type"], "type": r["type"]}
                       for r in ref["accessories"]}
        garments = {d["outfit"]["code"]: {"id": d["outfit"]["code"], "name": d["outfit"]["name"],
                    "allowedAccessories": [a["code"] for a in d["accessories"]]}
                    for d in ref["outfits"]}
        if not all((colors, styles, occasions, garments)):
            raise ValueError("empty catalog")
        return Catalog(occasions, styles, garments, accessories, colors, [], {},
                       patterns={"tron": {"id": "tron", "name": "Trơn"}}, scoring=scoring)
    except (KeyError, TypeError, ValueError):
        raise HTTPException(422, "Invalid backend reference data") from None


def validate_selection(look: Selection, cat: Catalog):
    if (look.outfitCode not in cat.garments or look.colorCode not in cat.colors
            or look.styleCode not in cat.styles or look.eventCode not in cat.occasions
            or len(set(look.accessories)) != len(look.accessories)
            or not set(look.accessories) <= set(cat.garments[look.outfitCode]["allowedAccessories"])):
        raise HTTPException(422, "Unsupported backend selection")


def state_for(look: Selection, cat: Catalog, with_bottom_and_shoes: bool = False) -> OutfitState:
    """with_bottom_and_shoes: gợi ý mới luôn kèm quần/váy và giày nên bộ luật quần/giày được áp dụng; các luồng khác
    (remix, kiểm tra bộ đang mặc) giữ nguyên vì người dùng có thể chưa chọn hai món này."""
    bottom = next((c for c in ("WHITE", "CREAM", "BLACK", *cat.colors) if c != look.colorCode and c in cat.colors), look.colorCode)
    extra = dict(zip(("bottom", "shoes"), bottom_and_shoes(look.accessories))) if with_bottom_and_shoes else {}
    return OutfitState(garment=look.outfitCode, gender="nu", occasion=look.eventCode,
                       style=look.styleCode, colors=Colors(main=look.colorCode, bottom=bottom),
                       accessories=look.accessories, **extra)


# Cách người dùng gọi màu (đã bỏ dấu). Tên trong danh mục luôn được dùng; bảng này thêm các cách gọi quen thuộc.
COLOR_ALIASES = {
    "RED": ["do", "do tuoi", "do son"], "DARK_RED": ["do sam", "do dam", "do ruou", "do tham", "do man"],
    "WHITE": ["trang", "trang tinh"], "CREAM": ["kem", "be", "be kem", "trang nga"],
    "BLUE": ["xanh duong", "xanh lam", "xanh da troi", "xanh bien", "xanh navy", "navy", "xanh coban", "xanh"],
    "GREEN": ["xanh la", "xanh luc", "xanh ngoc", "xanh reu", "xanh la cay", "luc"],
    "YELLOW": ["vang", "vang hoang", "vang dong", "vang nghe"], "BLACK": ["den", "den tuyen"],
    "PINK": ["hong", "hong dao", "hong phan"], "PURPLE": ["tim", "tim hue", "tim than"], "BROWN": ["nau", "nau dat"],
}
# Từ phủ định: viết đủ dấu để "bộ" (một bộ áo dài) không bị hiểu nhầm là "bỏ".
_AVOID = re.compile(r"\b(?:không|khong|ko|tránh|tranh|ghét|ghet|đừng|chẳng|chả|loại|bỏ|miễn)\b", re.IGNORECASE)
_SPLIT = re.compile(r"[,.;!?\n]|\b(?:nhưng|nhung|còn|con|và|va|mà|chứ|hay)\b", re.IGNORECASE)


def requested_items(prompt: str, table: dict, aliases: dict[str, list[str]] | None = None) -> tuple[list[str], list[str]]:
    """Tách món/màu người dùng muốn và muốn tránh. Câu có từ phủ định ("không thích đỏ") đưa vào danh sách tránh;
    các mục kể tiếp không kèm lời ("không thích đỏ, tím") giữ nguyên ý phủ định."""
    names = []
    for code, row in table.items():
        for name in [row["name"], *(aliases or {}).get(code, [])]:
            names.append((norm(name), code))
    names.sort(key=lambda item: -len(item[0]))          # tên dài khớp trước: "xanh lá" trước "xanh", "đỏ sẫm" trước "đỏ"
    wanted, avoided, avoid_mode = [], [], False
    for raw_clause in _SPLIT.split(re.sub(r"bỏ qua", " ", prompt, flags=re.IGNORECASE)):
        clause = f" {norm(raw_clause)} "
        found = []
        for name, code in names:
            if name and f" {name} " in clause:
                clause = clause.replace(f" {name} ", "  ")
                if code not in found:
                    found.append(code)
        if not found:
            avoid_mode = bool(_AVOID.search(raw_clause))
            continue
        leftover = clause.strip()
        if _AVOID.search(raw_clause):
            avoid_mode = True
        elif leftover:
            avoid_mode = False                           # có lời mới không phủ định: quay về "muốn"
        target = avoided if avoid_mode else wanted
        for code in found:
            if code not in target:
                target.append(code)
    return [c for c in wanted if c not in avoided], avoided


@router.post("/recommendations")
async def recommendations(body: BackendRequest, request: Request, svc: StylistService = Depends(get_service)):
    native = native_catalog(svc.catalog)
    cat = enrich_catalog(request_catalog(body.referenceData, native.scoring), native)
    if not body.city or not body.weather or body.eventCode not in cat.occasions or body.styleCode not in cat.styles:
        raise HTTPException(422, "Recommendation context is required")
    wanted, avoided = requested_items(body.prompt, cat.colors, COLOR_ALIASES)
    accs, avoid_accs = requested_items(body.prompt, cat.accessories)
    parsed = parse_by_keywords(body.prompt, native)
    ctx = parsed.model_copy(update=dict(occasion=body.eventCode, style=body.styleCode, preferredColors=wanted,
                 avoidColors=avoided, mustHave=accs, avoidAccessories=avoid_accs))
    gender = ('nam' if body.character == 'male' else 'nu') if body.character else (ctx.gender if ctx.gender in ('nu', 'nam') else 'nu')
    ctx.gender = gender
    candidates = []
    event_palette = cat.occasions[body.eventCode]['palette']
    style_palette = [c for c in cat.styles[body.styleCode]['preferColors'] if c in event_palette]
    palette = [c for c in dict.fromkeys([*wanted, *style_palette, *event_palette, *cat.colors]) if c not in avoided]
    garments = [(g, r) for g, r in cat.garments.items() if gender in r['genders']]
    suitable = [(g, r) for g, r in garments if body.eventCode in r['occasions']] or garments
    if len(suitable) < 3:                       # dịp chỉ có vài kiểu áo "chuẩn": thêm kiểu khác để vẫn có 3 lựa chọn khác nhau,
        suitable += [(g, r) for g, r in garments if (g, r) not in suitable]   # bộ luật sẽ chấm thấp hơn nếu kiểu áo ít hợp dịp
    ranks: dict[str, float] = {}
    for garment, row in suitable:
        defaults = cat.occasions[body.eventCode]['defaultAccessories'].get(garment, [])
        # Mỗi kiểu áo có nhiều bộ quần/giày/phụ kiện khác nhau để 3 gợi ý không trùng nhau ở những món này.
        for selected in accessory_sets(cat, row, defaults, accs, avoid_accs, gender):
            for color in palette[:max(2, min(len(wanted), 4))]:
                look = Selection(outfitCode=garment, colorCode=color, styleCode=body.styleCode,
                                 eventCode=body.eventCode, accessories=selected)
                state = state_for(look, cat, with_bottom_and_shoes=True).model_copy(update={'gender': gender})
                rank, evaluations, harmony, card = score_outfit(state, cat, ctx)
                outfit_id = f"c{len(candidates)+1}"
                ranks[outfit_id] = rank
                candidates.append(StylistOutfit(outfitId=outfit_id, state=state,
                                               evaluations=evaluations, color=harmony, scoreCard=card))
    if len(candidates) < 3:
        raise HTTPException(422, "Catalog cannot provide three concepts")
    candidates.sort(key=lambda o: -ranks[o.outfitId])
    # Danh sách ngắn gửi cho Gemini: giữ điểm cao nhưng phạt trùng kiểu áo, màu và phụ kiện để có đủ lựa chọn khác nhau.
    candidates = diverse_shortlist(candidates, ranks, n=9, colour_locked=len(wanted) == 1)   # nhiều màu thích: trải đều qua các màu đó
    # Include Spring's measured weather and available cultural sources in the AI request.
    prompt = json.dumps({"request": body.prompt, "eventCode": body.eventCode, "styleCode": body.styleCode,
                         "city": body.city, "weather": body.weather,
                         "culturalContext": body.culturalContext}, ensure_ascii=False)
    picked, source = await select_outfits(candidates, ctx, cat, svc._gemini_for(client_ip(request)),
                                          user_request=prompt, log=svc.log)

    concepts_out = []
    for o in picked:
        garment_name = cat.name("garments", o.state.garment)
        color_name = cat.name("colors", o.state.colors.main)
        style_name = cat.name("styles", o.state.style)
        event_name = cat.name("occasions", o.state.occasion)

        if source == "gemini" and o.title and o.whyChosen:
            concept_name = o.title.strip()
            reason = (o.whyChosen + " " + o.comment).strip()
        else:
            concept_name = f"{garment_name} {color_name} · {style_name}"
            cultural_text = ""
            knowledge_list = (body.culturalContext or {}).get(o.state.garment, [])
            for k in knowledge_list:
                if k.get("category") == "MEANING" and k.get("content"):
                    cultural_text = k["content"]
                    break
            if not cultural_text and knowledge_list:
                cultural_text = knowledge_list[0].get("content", "")

            weather_part = ""
            if body.weather and "temperature" in body.weather:
                temp = body.weather["temperature"]
                cond = body.weather.get("condition", "CLEAR")
                cond_str = "trời quang đãng" if cond == "CLEAR" else "thời tiết dễ chịu"
                weather_part = f"Thời tiết tại {body.city or 'địa phương'} hiện khoảng {temp}°C ({cond_str}), rất thuận lợi để mặc chất liệu truyền thống. "

            acc_part = ""
            if o.state.accessories:
                acc_names = [cat.name("accessories", a) for a in o.state.accessories]
                acc_part = f"Kết hợp cùng phụ kiện {', '.join(acc_names)} tạo điểm nhấn văn hóa tinh tế. "

            meaning_part = f"Ý nghĩa văn hóa: {cultural_text[:220]}..." if cultural_text else "Tôn vinh vẻ đẹp chuẩn mực và bản sắc trang phục Việt."

            reason = (
                f"{garment_name} sắc {color_name.lower()} là lựa chọn tuyệt vời cho dịp {event_name.lower()} theo tinh thần {style_name.lower()}. "
                f"{weather_part}{acc_part}{meaning_part}"
            )

        score = max(0, min(100, score_outfit(o.state, cat, ctx)[3].total))      # điểm hiển thị = thẻ 5 tiêu chí (điểm xếp hạng có thưởng nên có thể vượt 100)
        concepts_out.append({
            "conceptName": concept_name[:100],
            "outfitCode": o.state.garment,
            "colorCode": o.state.colors.main,
            "styleCode": o.state.style,
            "accessories": o.state.accessories,
            "matchScore": score,
            "reason": reason[:2000]
        })

    return {"concepts": concepts_out}


class Changes(BaseModel):
    model_config = ConfigDict(extra="forbid")
    colorCode: str | None = None
    styleCode: str | None = None
    removeAccessories: list[str] = Field(max_length=10)
    addAccessories: list[str] = Field(max_length=10)


class RemixOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    changes: Changes
    explanation: str = Field(min_length=1, max_length=2000)


def validate_remix(output: RemixOutput, current: Selection, cat: Catalog):
    change = output.changes
    removed, added, selected = set(change.removeAccessories), set(change.addAccessories), set(current.accessories)
    if (len(removed) != len(change.removeAccessories) or len(added) != len(change.addAccessories)
            or not removed <= selected or added & selected or removed & added):
        raise ValueError("Invalid accessory delta")
    look = current.model_copy(update={"colorCode": change.colorCode or current.colorCode,
                                      "styleCode": change.styleCode or current.styleCode,
                                      "accessories": sorted((selected - removed) | added)})
    validate_selection(look, cat)


def gemini_schema(model) -> dict:
    """Schema Pydantic → schema Gemini hiểu: gộp $ref, bỏ additionalProperties/title/$defs (Gemini từ chối các khoá này)."""
    raw = model.model_json_schema()
    defs = raw.get("$defs", {})

    def clean(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return clean(defs[node["$ref"].split("/")[-1]])
            return {k: clean(v) for k, v in node.items() if k not in ("additionalProperties", "title", "$defs", "default")}
        if isinstance(node, list):
            return [clean(v) for v in node]
        return node
    return clean(raw)


@router.post("/remix", response_model=RemixOutput)
async def remix(body: BackendRequest, request: Request, svc: StylistService = Depends(get_service)):
    cat = request_catalog(body.referenceData, svc.catalog.scoring or None)
    current = body.currentLook
    if current is None:
        raise HTTPException(422, "Current look is required")
    validate_selection(current, cat)
    try:
        raw, latency_ms = await svc._gemini_for(client_ip(request)).call_json(
            system="Đề xuất thay đổi theo yêu cầu. Giữ outfitCode và eventCode. Chỉ dùng mã trong referenceData và phụ kiện được hỗ trợ. Không bịa quy tắc văn hóa. Trả JSON changes và explanation.",
            contents=body.model_dump_json(exclude_none=True), schema=gemini_schema(RemixOutput), temperature=0.4)
        output = RemixOutput.model_validate(raw)
        validate_remix(output, current, cat)
        await svc.log("remix", svc.gemini.model, latency_ms, "gemini", True)
        return output
    except (AIError, ValueError, HTTPException) as exc:
        await svc.log("remix", svc.gemini.model, None, "fallback", False, str(exc)[:300])
        # Reuse the service's offline behavior while applying only explicit user wishes.
        colors, _ = requested_items(body.prompt, cat.colors, COLOR_ALIASES)
        styles, _ = requested_items(body.prompt, cat.styles)
        wanted, avoided = requested_items(body.prompt, cat.accessories)
        allowed = cat.garments[current.outfitCode]["allowedAccessories"]
        changes = Changes(colorCode=colors[0] if colors else None, styleCode=styles[0] if styles else None,
                          removeAccessories=[a for a in current.accessories if a in avoided],
                          addAccessories=[a for a in wanted if a in allowed and a not in current.accessories])
        output = RemixOutput(changes=changes, explanation="Đang dùng nhánh dự phòng: áp dụng màu, phong cách và phụ kiện được nêu rõ trong yêu cầu. Bạn có thể chỉnh thêm trong studio.")
        validate_remix(output, current, cat)
        return output
