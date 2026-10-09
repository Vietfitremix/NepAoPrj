"""Chấm điểm 5 tiêu chí (0–100), dựng trên cách chấm cũ — luật quyết định, AI chỉ diễn giải.

Đầu vào lấy nguyên từ cách chấm cũ:
  - điểm hài hoà màu OKLCH (color.py)            → góp phần lớn vào tiêu chí "dac_trung";
  - các luật đã khớp (rules.py), mỗi luật thuộc 1 tiêu chí (trường "criterion" trong data/rules.json)
    và cộng/trừ điểm tiêu chí đó theo mức: Phù hợp +, Nên cân nhắc −, Dễ gây sai lệch −−.
Thêm từ thang mới:
  - "boi_canh": màu chính nằm trong bảng màu của dịp thì cộng;
  - "phu_kien": không đeo phụ kiện là trung tính (không bị trừ);
  - "cach_tan": tính theo phong cách người dùng chọn (truyền thống: yếu tố hiện đại bị trừ; đường phố / tối giản:
    yếu tố hiện đại được cộng, luật "Nên cân nhắc" về cách tân trừ nhẹ);
  - trần nhạy cảm: có luật "Dễ gây sai lệch" thì tổng điểm không vượt riskCap.
Trọng số, điểm nền, bậc xếp loại đọc từ data/scoring.json.
"""
from app.models import Criterion, Evaluation, OutfitState, ScoreCard

DEFAULT_CRITERION = "boi_canh"


def _clamp(v: float) -> int:
    return max(0, min(100, round(v)))


def score_card(o: OutfitState, evals: list[Evaluation], color_score: int, catalog) -> ScoreCard:
    cfg = catalog.scoring
    pts = cfg["levelPoints"]
    rule_by_id = {r["id"]: r for r in catalog.rules}
    crit_of = {r["id"]: r.get("criterion", DEFAULT_CRITERION) for r in catalog.rules}
    by_crit: dict[str, list[Evaluation]] = {}
    for e in evals:
        by_crit.setdefault(crit_of.get(e.id, DEFAULT_CRITERION), []).append(e)

    remix = cfg["remix"]
    rs = remix["byStyle"].get(o.style, remix["byStyle"]["_khac"])
    modern = [a for a in o.accessories if a in remix["modernAccessories"]]
    if o.pattern in remix["modernPatterns"]:
        modern.append(o.pattern)

    criteria, risk = [], any(e.level == "risk" for e in evals)
    for c in cfg["criteria"]:
        cid, hits = c["id"], by_crit.get(c["id"], [])
        adj = 0
        for e in hits:
            p = rule_by_id.get(e.id, {}).get("points", pts[e.level])
            if cid == "cach_tan" and e.level == "consider" and rs.get("softConsider"):
                p = round(p / 3)                       # người chọn gu hiện đại: cách tân chỉ trừ nhẹ
            adj += p
        notes = []
        if cid == "dac_trung":
            share = c.get("colorShare", 0.6)
            value = share * color_score + (1 - share) * (c["base"] + adj)
            notes.append(f"Màu {color_score}/100")
        elif cid == "phu_kien":
            value = (c["base"] if o.accessories else c.get("baseNone", c["base"])) + adj
            if not o.accessories:
                notes.append("Chưa chọn phụ kiện")
        elif cid == "boi_canh":
            value = c["base"] + adj
            if o.colors.main in catalog.occasions.get(o.occasion, {}).get("palette", []):
                value += c.get("paletteBonus", 0)
                notes.append("Màu chính hợp bảng màu của dịp")
        elif cid == "cach_tan":
            value = rs["base"] + rs["perModern"] * min(len(modern), 4) + adj
            if modern:
                names = ", ".join(catalog.name("accessories", m) or catalog.name("patterns", m) for m in modern)
                notes.append(f"Yếu tố hiện đại: {names}")
        else:
            value = c["base"] + adj
        criteria.append(Criterion(id=cid, name=c["name"], en=c.get("en", ""), weight=c["weight"],
                                  score=_clamp(value), ruleIds=[e.id for e in hits], notes=notes))

    total_w = sum(c.weight for c in criteria) or 1
    total = _clamp(sum(c.weight * c.score for c in criteria) / total_w)
    cap_of = {r["id"]: r.get("cap") for r in catalog.rules}
    cap = min([cfg["riskCap"]] + [cap_of[e.id] for e in evals if e.level == "risk" and cap_of.get(e.id)])   # luật nặng có thể đặt trần thấp hơn
    capped = risk and total > cap
    if capped:
        total = cap
    band = next(b for b in cfg["bands"] if total >= b["min"])
    return ScoreCard(total=total, band=band["id"], bandText=band["text"], capped=capped, criteria=criteria)


def rank_bonus(o: OutfitState, intent, catalog) -> int:
    """Thưởng xếp hạng theo mong muốn người dùng (giữ từ cách chấm cũ; không hiện ra ngoài)."""
    if not intent:
        return 0
    b = catalog.scoring["rankBonus"]
    bonus = 0
    if intent.style and intent.style == o.style:
        bonus += b["style"]
    if o.colors.main in intent.preferredColors:
        bonus += b["preferredColor"]
    if intent.preferredGarment == o.garment:
        bonus += b["preferredGarment"]
    return bonus
