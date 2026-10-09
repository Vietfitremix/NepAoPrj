"""AI Remix cho tủ đồ: phân tích bối cảnh và nói thẳng yêu cầu có hợp không, thay vì chỉ làm theo.

Quy trình (luật quyết định, AI diễn giải):
  1. Gemini chỉ đọc yêu cầu của người dùng và đổi thành một bộ đồ mới ("ý định"), dùng đúng mã món trong tủ đồ.
  2. Bộ luật chấm điểm bộ hiện tại và bộ theo yêu cầu (cùng bối cảnh, cùng luật như thẻ điểm).
  3. Yêu cầu hợp (không thêm luật nặng, điểm không tụt đáng kể) thì áp dụng; không hợp thì KHÔNG áp dụng nguyên văn, mà đưa
     phương án gần ý người dùng nhất mà luật chấp nhận, kèm vài lựa chọn khác có điểm cao hơn (đều đã chấm bằng luật).
  4. Gemini viết phần phân tích bằng lời dựa trên các kết luận trên; không có Gemini thì dùng câu dựng sẵn.
"""
import json
import re
from copy import copy

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.ai import AIError
from app.ai.fallback import norm
from app.api.deps import client_ip, get_service
from app.api.routers.wardrobe_score import Built, ScoreRequest, Style, WardrobeSelection, build_state
from app.engine.color import color_metrics, score_colors
from app.engine.kinds import BOTTOM_LABEL, SHOES_LABEL
from app.engine.rules import evaluate
from app.engine.scoring import score_card
from app.models import Intent

router = APIRouter(tags=['backend integration'])


class Item(BaseModel):
    id: str = Field(max_length=60)
    name: str = Field(max_length=80)
    slot: str | None = Field(default=None, max_length=30)


class WardrobeOptions(BaseModel):
    outfits: list[Item] = Field(max_length=40)
    pants: list[Item] = Field(max_length=40)
    shoes: list[Item] = Field(max_length=40)
    accessories: list[Item] = Field(max_length=60)


class RemixBody(ScoreRequest):
    prompt: str = Field(min_length=1, max_length=1500)
    context: Intent | None = None
    options: WardrobeOptions


def _names(options: WardrobeOptions) -> dict[str, str]:
    return {i.id: i.name for group in (options.outfits, options.pants, options.shoes, options.accessories) for i in group}


def _score(body: RemixBody, selection: WardrobeSelection, svc):
    """Chấm một bộ tủ đồ (cùng cách với /wardrobe-score), trả (Built, thẻ điểm, đánh giá, điểm hài hoà màu)."""
    probe = body.model_copy(update={'wardrobe': body.wardrobe.model_copy(update={'selection': selection})})
    b = build_state(probe, svc)
    if b is None:
        return None
    harmony = score_colors(b.state, b.cat)
    evaluations = evaluate(b.state, b.cat.rules, body.context, color_metrics(b.state, b.cat, harmony.score))
    return b, score_card(b.state, evaluations, harmony.score, b.cat), evaluations, harmony


def _describe(selection: WardrobeSelection, names: dict[str, str]) -> dict:
    acc = [names.get(i, i) for i in selection.accessories.values() if i]
    return {'áo': names.get(selection.shirt or '', 'chưa chọn'), 'quần/váy': names.get(selection.pants or '', 'chưa phối'),
            'giày dép': names.get(selection.shoes or '', 'đi chân trần'), 'phụ kiện': acc or ['không có']}


def _clone(sel: WardrobeSelection, **kw) -> WardrobeSelection:
    data = sel.model_dump()
    for k, v in kw.items():
        data[k] = v
    return WardrobeSelection.model_validate(data)


def _intent_schema() -> dict:
    s = {'type': 'string'}
    return {'type': 'object', 'properties': {
        'shirt': s, 'pants': s, 'shoes': s, 'shirtColor': s, 'pantsColor': s,
        'accessories': {'type': 'array', 'items': {'type': 'object', 'properties': {'slot': s, 'id': s}, 'required': ['slot', 'id']}},
    }}


def _keyword_intent(prompt: str, options: WardrobeOptions, current: WardrobeSelection) -> WardrobeSelection:
    """Dự phòng khi không có Gemini: tìm tên món trong yêu cầu ("bỏ/không/tránh" = bỏ món đó)."""
    sel = current.model_copy(deep=True)
    for clause in re.split(r'[,.;\n]|\bnhưng\b|\bvà\b', prompt, flags=re.IGNORECASE):
        text = norm(clause)
        removing = bool(re.search(r'\b(bo|khong|tranh|ghet)\b', text))
        for group, field in ((options.outfits, 'shirt'), (options.pants, 'pants'), (options.shoes, 'shoes')):
            for item in sorted(group, key=lambda i: -len(i.name)):
                if re.search(rf'\b{re.escape(norm(item.name))}\b', text):
                    setattr(sel, field, None if removing else item.id)
                    break
        for item in options.accessories:
            if item.slot and re.search(rf'\b{re.escape(norm(item.name))}\b', text):
                sel.accessories = {**sel.accessories, item.slot: None if removing else item.id}
    return sel


def _apply_intent(raw: dict, options: WardrobeOptions, current: WardrobeSelection) -> WardrobeSelection:
    ids = lambda group: {i.id for i in group}                                   # noqa: E731
    sel = current.model_copy(deep=True)
    none = lambda v: None if v in (None, '', 'none', 'null') else v            # noqa: E731
    if raw.get('shirt') and none(raw['shirt']) in ids(options.outfits):
        sel.shirt = raw['shirt']
    if 'pants' in raw and (none(raw['pants']) is None or raw['pants'] in ids(options.pants)):
        sel.pants = none(raw['pants'])
    if 'shoes' in raw and (none(raw['shoes']) is None or raw['shoes'] in ids(options.shoes)):
        sel.shoes = none(raw['shoes'])
    by_slot = {i.id: i.slot for i in options.accessories}
    for a in raw.get('accessories') or []:
        slot, item = a.get('slot'), none(a.get('id'))
        if item is None and slot:
            sel.accessories = {**sel.accessories, slot: None}
        elif item in by_slot and by_slot[item] == slot:
            sel.accessories = {**sel.accessories, slot: item}
    for field, key in (('shirt', 'shirtColor'), ('pants', 'pantsColor')):
        color = raw.get(key)
        if isinstance(color, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', color):
            sel.styles = {**sel.styles, field: Style(color=color, pattern=(sel.styles.get(field) or Style()).pattern)}
    return sel


def _alternatives(body: RemixBody, base: WardrobeSelection, requested: WardrobeSelection, svc, floor: int):
    """Các bộ gần với yêu cầu nhất mà luật chấp nhận: đổi MỘT món (quần/váy, giày dép, bỏ phụ kiện) so với bộ gốc để chấm lại."""
    out = []
    tries = [('pants', i.id) for i in body.options.pants] + [('shoes', i.id) for i in body.options.shoes] + [('shoes', None)]
    for slot, value in tries:
        if getattr(base, slot) == value:
            continue
        cand = _clone(base, **{slot: value})
        res = _score(body, cand, svc)
        if res:
            out.append((res[1].total, slot, value, cand, res))
    for slot, item in base.accessories.items():
        if item:
            cand = _clone(base, accessories={**base.accessories, slot: None})
            res = _score(body, cand, svc)
            if res:
                out.append((res[1].total, 'accessory', slot, cand, res))
    out.sort(key=lambda t: -t[0])
    return [o for o in out if o[0] >= floor]


def _label(slot: str, value, names: dict[str, str]) -> str:
    if slot == 'accessory':
        return f'Bỏ {names.get(value, value)}'
    if slot == 'shoes' and value is None:
        return 'Đi chân trần'
    return f"Đổi {'quần/váy' if slot == 'pants' else 'giày dép'} sang {names.get(value, value)}"


@router.post('/wardrobe-remix')
async def wardrobe_remix(body: RemixBody, request: Request, svc=Depends(get_service)):
    if not body.wardrobe.selection.shirt:
        raise HTTPException(422, 'Chọn áo trước khi nhờ stylist remix.')
    if not svc.catalog.garments:                      # BACKEND_COMPAT_ONLY: dùng catalog JSON của AI
        from app.catalog.backend_bridge import native_catalog

        class _Fixed:
            def get(self, _c=native_catalog(svc.catalog)):
                return _c
        svc = copy(svc)
        svc.catalogs = _Fixed()
    names = _names(body.options)
    current = body.wardrobe.selection
    here = _score(body, current, svc)
    if here is None:
        raise HTTPException(422, 'Chọn áo trước khi nhờ stylist remix.')
    gemini = svc._gemini_for(client_ip(request))

    # 1) hiểu yêu cầu -> bộ đồ người dùng muốn
    source = 'fallback'
    try:
        raw, _ = await gemini.call_json(
            system=('Bạn đổi yêu cầu của người dùng thành một bộ đồ mới. Chỉ dùng mã (id) có trong "options"; để bỏ một món thì '
                    'ghi "none". Chỉ ghi những món người dùng THỰC SỰ muốn đổi, giữ nguyên phần còn lại. Màu ghi dạng #RRGGBB. '
                    'Không bịa mã. Trả JSON.'),
            contents=json.dumps({'yêuCầu': body.prompt, 'bộHiệnTại': current.model_dump(), 'options': body.options.model_dump()}, ensure_ascii=False),
            schema=_intent_schema(), temperature=0.2)
        requested = _apply_intent(raw, body.options, current)
        source = 'gemini'
    except (AIError, ValueError):
        requested = _keyword_intent(body.prompt, body.options, current)
    there = _score(body, requested, svc) if requested != current else here

    # 2) quyết định bằng luật
    risk_ids = lambda r: {e.id for e in r[2] if e.level == 'risk'}              # noqa: E731
    new_risk = risk_ids(there) - risk_ids(here)
    unchanged = requested == current
    request_ok = (not unchanged) and not new_risk and there[1].total >= here[1].total - 5 and there[1].band != 'can_chinh'
    floor = max(60, here[1].total - 5)
    alts = _alternatives(body, requested if not unchanged else current, requested, svc, floor)
    options = [{'label': _label(slot, value, names), 'score': total, 'band': res[1].bandText,
                'selection': cand.model_dump(), 'why': next((e.reason for e in res[2] if e.level != 'ok'), 'Không còn điểm lệch nào.')}
               for total, slot, value, cand, res in alts[:3]]
    if request_ok:
        applied, final, final_res, status = True, requested, there, 'hop'
        options = [o for o in options if o['score'] > there[1].total + 2]
    elif unchanged:
        applied, final, final_res, status = False, current, here, 'chua_ro'
    else:
        # không làm theo nguyên văn: lấy phương án tốt nhất đổi một món từ bộ theo yêu cầu, nếu luật chấp nhận
        best = alts[0] if alts and alts[0][0] >= max(here[1].total - 5, 60) else None
        if best:
            applied, final, final_res, status = True, best[3], best[4], 'dieu_chinh'
            options = [o for o in options if o['selection'] != final.model_dump()]
        else:
            applied, final, final_res, status = False, current, here, 'khong_hop'

    # 3) lời phân tích
    facts = {
        'yêuCầu': body.prompt, 'bốiCảnh': {'dịp': body.eventCode, 'phongCách': body.styleCode, **(body.context.model_dump(exclude_none=True) if body.context else {})},
        'bộHiệnTại': {**_describe(current, names), 'điểm': here[1].total, 'xếpLoại': here[1].bandText},
        'bộTheoYêuCầu': {**_describe(requested, names), 'điểm': there[1].total, 'xếpLoại': there[1].bandText,
                        'lýDoLệch': [e.reason for e in there[2] if e.level != 'ok']},
        'kếtLuận': {'hop': 'yêu cầu hợp, đã áp dụng', 'dieu_chinh': 'yêu cầu chưa hợp, đã áp dụng phương án gần ý nhất mà luật chấp nhận',
                    'khong_hop': 'yêu cầu không hợp và chưa có phương án đủ tốt, không thay đổi gì',
                    'chua_ro': 'chưa hiểu yêu cầu đổi món nào, không thay đổi gì'}[status],
        'bộSauKhiXửLý': {**_describe(final, names), 'điểm': final_res[1].total},
        'lựaChọnKhác': [{'tên': o['label'], 'điểm': o['score']} for o in options],
    }
    analysis = explanation = None
    try:
        out, _ = await gemini.call_json(
            system=('Bạn là stylist Việt phục của "Nếp Áo", xưng "mình", gọi "bạn". Viết lời nhận định THẲNG THẮN, công tâm. '
                    'analysis (2–3 câu): phân tích bối cảnh (dịp, thời tiết, nơi, vai trò, phong cách) và nói rõ yêu cầu của bạn '
                    'có hợp không, vì sao, dựa ĐÚNG vào "lýDoLệch" và điểm. Yêu cầu không hợp thì nói thẳng là chưa/không hợp, không '
                    'khen vòng vo; hợp thì nói hợp. CHỈ nêu điểm lệch có trong "lýDoLệch"; nếu "lýDoLệch" trống thì không tự bịa thêm điểm chê. explanation (1–2 câu): mình đã làm gì và vì sao, nêu lựa chọn khác nếu có. '
                    'Không bịa luật hay nguồn văn hoá. Không dùng emoji. Tiếng Việt có dấu đầy đủ, không đọc lại số điểm quá nhiều. Trả JSON.'),
            contents=json.dumps(facts, ensure_ascii=False),
            schema={'type': 'object', 'properties': {'analysis': {'type': 'string'}, 'explanation': {'type': 'string'}}, 'required': ['analysis', 'explanation']},
            temperature=0.5)
        analysis, explanation = str(out.get('analysis', '')).strip(), str(out.get('explanation', '')).strip()
        source = 'gemini'
    except (AIError, ValueError):
        pass
    if not analysis or not explanation:
        issue = next((e.reason for e in there[2] if e.level != 'ok'), '')
        analysis = {'hop': 'Yêu cầu của bạn hợp với bối cảnh và không làm bộ đồ bị lệch luật.',
                    'dieu_chinh': f'Mình nói thẳng: yêu cầu này chưa phù hợp vì {issue[:1].lower() + issue[1:]}.' if issue else 'Yêu cầu này chưa phù hợp với bộ đồ hiện tại.',
                    'khong_hop': f'Mình nói thẳng: yêu cầu này không phù hợp{(" vì " + issue[:1].lower() + issue[1:]) if issue else ""}.',
                    'chua_ro': 'Mình chưa hiểu bạn muốn đổi món nào. Hãy nêu rõ món (áo, quần/váy, giày dép hoặc phụ kiện).'}[status]
        explanation = {'hop': 'Mình đã áp dụng đúng yêu cầu của bạn.',
                       'dieu_chinh': 'Mình áp dụng phương án gần ý bạn nhất mà vẫn hợp bối cảnh; bạn xem thêm các lựa chọn bên dưới.',
                       'khong_hop': 'Mình giữ nguyên bộ hiện tại; bạn thử các lựa chọn phù hợp hơn bên dưới.',
                       'chua_ro': 'Mình giữ nguyên bộ hiện tại.'}[status]
    return {'status': status, 'applied': applied, 'analysis': analysis, 'explanation': explanation, 'source': source,
            'scoreBefore': here[1].total, 'scoreRequested': there[1].total, 'scoreAfter': final_res[1].total,
            'selection': final.model_dump(), 'options': options}
