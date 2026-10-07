"""responseSchema cho Gemini. Danh sách enum lấy từ catalog đang nạp nên AI chỉ chọn được mã có thật."""
from app.models import CONTEXT_FIELDS


def _enum(ids, nullable=False):
    s = {"type": "STRING", "enum": list(ids)}
    if nullable:
        s["nullable"] = True
    return s


def intent_schema(cat) -> dict:
    occ, sty = list(cat.occasions), list(cat.styles)
    props = {
        "occasion": _enum(occ, nullable=True),
        "style": _enum(sty, nullable=True),
        "gender": _enum(["nu", "nam", "khong_ro"]),
        **{f: _enum(cat.context_values(f), nullable=True) for f in CONTEXT_FIELDS},
        "preferredGarment": _enum(cat.garments, nullable=True),
        "preferredColors": {"type": "ARRAY", "items": _enum(cat.colors)},
        "mustHave": {"type": "ARRAY", "items": _enum(cat.accessories)},
        "avoidAccessories": {"type": "ARRAY", "items": _enum(cat.accessories)},
        "avoidColors": {"type": "ARRAY", "items": _enum(cat.colors)},
        "needsClarification": {
            "type": "OBJECT", "nullable": True,
            "properties": {
                "question": {"type": "STRING"},
                "options": {"type": "ARRAY", "items": {
                    "type": "OBJECT",
                    "properties": {"label": {"type": "STRING"},
                                   "occasion": _enum(occ, nullable=True),
                                   "style": _enum(sty, nullable=True)},
                    "required": ["label"],
                }},
            },
            "required": ["question", "options"],
        },
    }
    return {"type": "OBJECT", "properties": props, "required": list(props)}


def _comment_props() -> dict:
    return {
        "outfitId": {"type": "STRING"},
        "title": {"type": "STRING"},
        "comment": {"type": "STRING"},
        "tip": {"type": "STRING"},
        "ruleIds": {"type": "ARRAY", "items": {"type": "STRING"}},
    }


def explain_schema() -> dict:
    return {
        "type": "OBJECT",
        "properties": {"outfits": {"type": "ARRAY", "items": {
            "type": "OBJECT", "properties": _comment_props(),
            "required": ["outfitId", "title", "comment", "tip", "ruleIds"],
        }}},
        "required": ["outfits"],
    }


def select_schema() -> dict:
    """Gemini chọn đúng 3 bộ trong danh sách ứng viên, kèm lý do hợp bối cảnh và lời nhận xét."""
    return {
        "type": "OBJECT",
        "properties": {"picks": {"type": "ARRAY", "items": {
            "type": "OBJECT",
            "properties": {**_comment_props(), "whyChosen": {"type": "STRING"}},
            "required": ["outfitId", "whyChosen", "title", "comment", "tip", "ruleIds"],
        }}},
        "required": ["picks"],
    }
