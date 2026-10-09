"""Deterministic cultural check of the visible wardrobe, including custom RGB."""
from fastapi import APIRouter, Depends, HTTPException, Request
from copy import copy, deepcopy
from pydantic import BaseModel, ConfigDict, Field

from app.api.deps import client_ip, get_service
from app.catalog.backend_bridge import EVENTS, STYLES, native_catalog, nearest_color
from app.engine.color import score_pair
from app.engine.rules import evaluate
from app.engine.scoring import score_card
from app.models import Colors, Intent, OutfitState

router = APIRouter(tags=['backend integration'])

class Style(BaseModel):
    color: str | None = Field(default=None, pattern=r'^#[a-fA-F0-9]{6}$')
    pattern: str | None = Field(default=None, max_length=60)

class WardrobeSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    shirt: str | None = Field(max_length=60)
    pants: str | None = Field(max_length=60)
    shoes: str | None = Field(default=None, max_length=60)
    accessories: dict[str, str | None] = Field(default_factory=dict, max_length=20)
    styles: dict[str, Style] = Field(default_factory=dict, max_length=3)

class Wardrobe(BaseModel):
    character: str = Field(pattern=r'^(male|female)$')
    selection: WardrobeSelection

class ScoreRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    outfitCode: str
    colorCode: str
    styleCode: str
    eventCode: str
    accessories: list[str] = Field(max_length=10)
    wardrobe: Wardrobe

SHIRTS = {'navy': 'ao_dai', 'burgundy': 'ao_dai', 'teal': 'ao_dai', 'jade': 'ao_dai', 'rose': 'ao_dai',
          'tu-than': 'ao_tu_than', 'ngu-than': 'ao_ngu_than', 'nhat-binh': 'nhat_binh', 'ba-ba': 'ao_ba_ba'}
ORIGINAL = {'navy': '#23415b', 'burgundy': '#8b2635', 'teal': '#397c78', 'jade': '#39705b', 'rose': '#de91aa',
            'ivory': '#eee9dc', 'skirt-long-ivory': '#eee9dc', 'long-black': '#24242a',
            'long-navy': '#23415b', 'skirt-short-navy': '#23415b', 'shorts-denim': '#32679e'}
ITEMS = {'sneakers': 'sneaker', 'flats': 'giay_bup_be', 'tui-coi': 'tui', 'quat-giay': 'quat_giay',
         'bong-tai': 'trang_suc', 'vong-tay': 'trang_suc'}
CATEGORIES = {'cau_truc': 'STRUCTURE', 'dac_trung': 'GARMENT_CHARACTERISTICS', 'phu_kien': 'ACCESSORIES',
              'boi_canh': 'CONTEXT', 'cach_tan': 'MODERN_REMIX'}

class Built:
    """Bộ đồ đang mặc đã đổi sang OutfitState của AI (dùng chung cho chấm điểm và nhận xét)."""
    def __init__(self, cat, selection, garment, event, style, main_hex, bottom_hex, accessories, pattern, state):
        self.cat, self.selection, self.garment, self.event, self.style = cat, selection, garment, event, style
        self.main_hex, self.bottom_hex, self.accessories, self.pattern, self.state = main_hex, bottom_hex, accessories, pattern, state


def build_state(body: ScoreRequest, svc) -> Built | None:
    cat = deepcopy(native_catalog(svc.catalog))
    selection = body.wardrobe.selection
    garment = SHIRTS.get(selection.shirt)
    if not garment:
        return None
    event, style = EVENTS.get(body.eventCode), STYLES.get(body.styleCode)
    if event not in cat.occasions or style not in cat.styles:
        raise HTTPException(422, 'Unsupported cultural context')
    defaults = cat.garments[garment]['defaultColors']
    def hex_for(slot, item, fallback):
        custom = selection.styles.get(slot)
        return custom.color if custom and custom.color else ORIGINAL.get(item, cat.color_hex(fallback))
    main_hex = hex_for('shirt', selection.shirt, defaults['main'])
    bottom_hex = hex_for('pants', selection.pants, defaults.get('bottom', 'trang_nga'))
    accessories = list(dict.fromkeys(ITEMS.get(item, item.replace('-', '_'))
                                    for item in [selection.shoes, *selection.accessories.values()] if item))
    # These are modern wardrobe pieces, evaluated by the existing style preference
    # scale, rather than assigning invented cultural prohibitions to each item.
    modern = ['giay_the_thao', 'dep_crocs', 'dep_le', 'tai_nghe', 'mu_luoi_trai', 'moc_khoa_bong',
              'ba_lo', 'tui_tote', 'tui_deo_cheo', 'kinh_ram', 'day_xich_hong', 'gang_tay_ho_ngon',
              'mu_cao_boi', 'tui_xach_thoi_trang']
    cat.scoring['remix']['modernAccessories'] = list(dict.fromkeys([*cat.scoring['remix']['modernAccessories'], *modern]))
    pattern = selection.styles.get('shirt', Style()).pattern or 'tron'
    state = OutfitState(garment=garment, gender='nam' if body.wardrobe.character == 'male' else 'nu',
                        occasion=event, style=style, pattern=pattern.replace('-', '_'), accessories=accessories,
                        colors=Colors(main=nearest_color(main_hex, cat.colors), bottom=nearest_color(bottom_hex, cat.colors)))
    return Built(cat, selection, garment, event, style, main_hex, bottom_hex, accessories, pattern, state)


@router.post('/wardrobe-score')
def wardrobe_score(body: ScoreRequest, svc=Depends(get_service)):
    b = build_state(body, svc)
    if b is None:
        return dict(score=None, level='INSUFFICIENT_DATA', breakdown={}, warnings=[],
                    missingCategories=['STRUCTURE'], explanation='Chọn áo để kiểm tra đầy đủ bản phối.')
    cat, selection, garment, style = b.cat, b.selection, b.garment, b.style
    main_hex, bottom_hex, accessories, pattern, state = b.main_hex, b.bottom_hex, b.accessories, b.pattern, b.state
    evaluations = evaluate(state, cat.rules)
    shoe_color = selection.styles.get('shoes', Style()).color if selection.shoes else None
    harmony = score_pair(main_hex, bottom_hex, shoe_color)
    card = score_card(state, evaluations, harmony.score, cat)
    breakdown_keys = ['structure', 'garmentCharacteristics', 'accessories', 'context', 'modernRemix']
    values = {c.id: c.score for c in card.criteria}
    warnings = []
    by_id = {r['id']: r for r in cat.rules}
    for e in evaluations:
        if e.level == 'ok':
            continue
        warnings.append(dict(severity='HIGH' if e.level == 'risk' else 'MEDIUM', category=CATEGORIES[by_id[e.id].get('criterion', 'boi_canh')],
                             message=e.reason, suggestion=e.suggestion.text,
                             sourceUrl=e.sources[0] if e.sources else None, sourceVerified=e.sourceVerified, sourceNote=e.sourceNote))
    selected_modern = [a for a in accessories if a in cat.scoring['remix']['modernAccessories']]
    if pattern.replace('-', '_') in cat.scoring['remix']['modernPatterns']:
        selected_modern.append(pattern)
    style_scale = cat.scoring['remix']['byStyle'].get(style, cat.scoring['remix']['byStyle']['_khac'])
    if selected_modern and style_scale['perModern'] < 0 and not any(w['category'] == 'MODERN_REMIX' for w in warnings):
        warnings.append(dict(severity='MEDIUM', category='MODERN_REMIX',
            message='Bản phối có yếu tố hiện đại trong khi bạn chọn phong cách truyền thống.',
            suggestion='Giảm phụ kiện hoặc họa tiết hiện đại nếu muốn giữ tổng thể truyền thống; chọn phong cách Gen Z nếu muốn nhấn mạnh cách tân.',
            sourceVerified=False, sourceNote='Gợi ý phối đồ theo phong cách của ứng dụng, không phải quy định văn hóa bắt buộc.'))
    if harmony.score < 60:
        warnings.append(dict(severity='LOW', category='GARMENT_CHARACTERISTICS', message=harmony.note,
            suggestion='Thử tăng tương phản giữa áo và quần/váy, hoặc dùng một màu trung tính.',
            sourceVerified=False, sourceNote='Gợi ý dựa trên độ tương phản và hài hòa màu của bản phối.'))
    level = 'WELL_PRESERVED' if card.total >= 90 else 'SUITABLE' if card.total >= 75 else 'WARNING' if card.total >= 60 else 'HIGH_RISK'
    return dict(score=card.total, level=level, breakdown=dict(zip(breakdown_keys, (values[c] for c in CATEGORIES))),
                warnings=warnings, missingCategories=[],
                explanation=f"Đã kiểm tra {cat.name('garments', garment)}; phụ kiện: {', '.join(cat.name('accessories', a).replace('_', ' ') for a in accessories) or 'không có'}; màu áo {main_hex}, màu quần/váy {bottom_hex}. Hài hòa màu {harmony.score}/100. {harmony.note} Điểm theo quy tắc phối đồ tham khảo.")


class ReviewBody(ScoreRequest):
    context: Intent | None = None      # bối cảnh từ quiz (thời tiết, nơi, buổi, vai trò…)


@router.post('/wardrobe-review')
async def wardrobe_review(body: ReviewBody, request: Request, svc=Depends(get_service)):
    """Nút "Hỏi stylist" cho bộ đồ trong tủ đồ: lời nhận xét, mẹo (Recommend) và thẻ điểm 5 tiêu chí.
    Chấm điểm và chọn mức đánh giá do luật; Gemini chỉ diễn giải bằng lời."""
    b = build_state(body, svc)
    if b is None:
        raise HTTPException(422, 'Chọn áo để stylist nhận xét.')
    if not svc.catalog.garments:                      # chế độ BACKEND_COMPAT_ONLY: catalog gốc để trống → dùng bản JSON của AI
        class _Fixed:
            def get(self, _cat=native_catalog(svc.catalog)):
                return _cat
        svc = copy(svc); svc.catalogs = _Fixed()
    res = await svc.review(b.state, body.context, None, ip=client_ip(request))
    return dict(verdict=res['verdict'], verdictText=res['verdictText'], source=res['source'], current=res['current'])
