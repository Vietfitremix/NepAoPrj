"""Bộ luật văn hóa: kiểm tra điều kiện của từng luật trên bộ đồ (+ bối cảnh) và trả về đánh giá 3 mức."""
from app.models import Evaluation, Intent, OutfitState, Suggestion

LEVEL_ORDER = {"risk": 0, "consider": 1, "ok": 2}
LEVEL_LABEL = {"ok": "Phù hợp", "consider": "Nên cân nhắc", "risk": "Dễ gây sai lệch"}

# Điều kiện lá đọc từ bối cảnh (quiz) thay vì từ bộ đồ
CONTEXT_KEYS = ("weather", "setting", "timeOfDay", "role")


def _colors(o: OutfitState) -> list[str]:
    return [c for c in o.colors.model_dump().values() if c]


def _in_range(value, bounds: dict) -> bool | None:
    if value is None:
        return None
    return ("min" not in bounds or value >= bounds["min"]) and ("max" not in bounds or value <= bounds["max"])


def _matches(cond: dict, o: OutfitState, ctx: Intent | None, metrics: dict) -> bool | None:
    # Unknown inputs remain unknown through negation; missing quiz answers are not faults.
    if "all" in cond or "any" in cond:
        key = "all" if "all" in cond else "any"
        values = [_matches(c, o, ctx, metrics) for c in cond[key]]
        if key == "all":
            return False if False in values else None if None in values else True
        return True if True in values else None if None in values else False
    if "not" in cond:
        value = _matches(cond["not"], o, ctx, metrics)
        return None if value is None else not value
    for key in CONTEXT_KEYS:
        if key in cond:
            value = getattr(ctx, key, None) if ctx else None
            return None if value is None else value in cond[key]
    if "accessoryCount" in cond:
        bounds = cond["accessoryCount"]
        items = set(o.accessories)
        if "items" in bounds:
            items &= set(bounds["items"])
        return _in_range(len(items), bounds)
    if "metric" in cond:
        bounds = cond["metric"]
        return _in_range(metrics.get(bounds["name"]), bounds)
    if "bottom" in cond:
        return None if o.bottom is None else o.bottom in cond["bottom"]
    if "shoes" in cond:
        return None if o.shoes is None else o.shoes in cond["shoes"]
    if "garment" in cond:
        return o.garment in cond["garment"]
    if "occasion" in cond:
        return o.occasion in cond["occasion"]
    if "style" in cond:
        return o.style in cond["style"]
    if "gender" in cond:
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
    return None


def matches(cond: dict, o: OutfitState, ctx: Intent | None = None, metrics: dict | None = None) -> bool:
    """Điều kiện dạng cây: all / any / not và các phép so sánh lá (xem data/rules.json).

    Lá về bối cảnh (weather, setting, timeOfDay, role) chỉ đúng khi có bối cảnh và giá trị khớp;
    không có bối cảnh thì luật đó không áp dụng.
    """
    return _matches(cond, o, ctx, metrics or {}) is True


def evaluate(o: OutfitState, rules: list[dict], ctx: Intent | None = None, metrics: dict | None = None) -> list[Evaluation]:
    hits = [r for r in rules if r.get("active", True) and matches(r["when"], o, ctx, metrics)]
    # One issue contributes once, even when a general rule and a specific rule both match.
    groups = {}
    for r in hits:
        key = r.get("group") or r["id"]
        order = (-LEVEL_ORDER[r["level"]], r.get("priority", 0), abs(r.get("points", 0)))
        old = groups.get(key)
        if old is None or order > old[0]:
            groups[key] = (order, r)
    hits = [value[1] for value in groups.values()]
    evals = [
        Evaluation(id=r["id"], level=r["level"], reason=r["reason"],
                   suggestion=Suggestion(**r["suggestion"]), sources=r.get("sources", []),
                   sourceVerified=bool(r.get("verified", False)), sourceNote=r.get("sourceNote", ""))
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
