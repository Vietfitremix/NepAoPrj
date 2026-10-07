"""Bộ luật văn hóa: kiểm tra điều kiện của từng luật trên bộ đồ (+ bối cảnh) và trả về đánh giá 3 mức."""
from app.models import Evaluation, Intent, OutfitState, Suggestion

LEVEL_ORDER = {"risk": 0, "consider": 1, "ok": 2}
LEVEL_LABEL = {"ok": "Phù hợp", "consider": "Nên cân nhắc", "risk": "Dễ gây sai lệch"}

# Điều kiện lá đọc từ bối cảnh (quiz) thay vì từ bộ đồ
CONTEXT_KEYS = ("weather", "setting", "timeOfDay", "role")


def _colors(o: OutfitState) -> list[str]:
    return [c for c in o.colors.model_dump().values() if c]


def matches(cond: dict, o: OutfitState, ctx: Intent | None = None) -> bool:
    """Điều kiện dạng cây: all / any / not và các phép so sánh lá (xem data/rules.json).

    Lá về bối cảnh (weather, setting, timeOfDay, role) chỉ đúng khi có bối cảnh và giá trị khớp;
    không có bối cảnh thì luật đó không áp dụng.
    """
    if "all" in cond:
        return all(matches(c, o, ctx) for c in cond["all"])
    if "any" in cond:
        return any(matches(c, o, ctx) for c in cond["any"])
    if "not" in cond:
        return not matches(cond["not"], o, ctx)
    for key in CONTEXT_KEYS:
        if key in cond:
            return bool(ctx) and getattr(ctx, key) in cond[key]
    if "garment" in cond:
        return o.garment in cond["garment"]
    if "occasion" in cond:
        return o.occasion in cond["occasion"]
    if "style" in cond:
        return o.style in cond["style"]
    if "gender" in cond:                      # nhận cả "nam" lẫn ["nam"]
        g = cond["gender"]
        return o.gender in g if isinstance(g, list) else o.gender == g
    if "pattern" in cond:
        return o.pattern in cond["pattern"]
    if "hasAccessory" in cond:
        return cond["hasAccessory"] in o.accessories
    if "mainColorIn" in cond:
        return o.colors.main in cond["mainColorIn"]
    if "allColorsIn" in cond:
        return all(c in cond["allColorsIn"] for c in _colors(o))
    return False


def evaluate(o: OutfitState, rules: list[dict], ctx: Intent | None = None) -> list[Evaluation]:
    hits = [r for r in rules if matches(r["when"], o, ctx)]
    evals = [
        Evaluation(id=r["id"], level=r["level"], reason=r["reason"],
                   suggestion=Suggestion(**r["suggestion"]), sources=r.get("sources", []))
        for r in hits
    ]
    return sorted(evals, key=lambda e: LEVEL_ORDER[e.level])


def worst_level(evals: list[Evaluation]) -> str:
    return evals[0].level if evals else "ok"


def count_levels(evals: list[Evaluation]) -> dict[str, int]:
    out = {"ok": 0, "consider": 0, "risk": 0}
    for e in evals:
        out[e.level] += 1
    return out
