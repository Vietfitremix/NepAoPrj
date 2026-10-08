"""Nạp catalog từ file JSON (chạy local) hoặc từ PostgreSQL schema catalog (trên VPS).

Hai nguồn trả về cùng một cấu trúc Catalog để phần còn lại của service không cần phân biệt.
"""
import json
from pathlib import Path

from .catalog import Catalog


def _by_id(rows: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in rows}


def _fallback_from_json(raw: dict) -> dict:
    return {
        "by_garment_occasion": raw.get("byGarmentOccasion", {}),
        "by_garment": raw.get("byGarment", {}),
        "by_rule": raw.get("byRule", {}),
        "default_tip": raw.get("defaultTip", ""),
    }


def load_from_json(data_dir: Path) -> Catalog:
    def read(name, default=None):
        p = data_dir / name
        if not p.exists():
            if default is not None:
                return default
            raise FileNotFoundError(p)
        return json.loads(p.read_text(encoding="utf-8"))

    rules = [r for r in read("rules.json") if r.get("active", True)]
    cards = read("culture-cards.json", [])
    patterns, quiz, scoring, checklist = load_ui_data(data_dir)
    return Catalog(
        occasions=_by_id(read("occasions.json")),
        styles=_by_id(read("styles.json")),
        garments=_by_id(read("garments.json")),
        accessories=_by_id(read("accessories.json")),
        colors=_by_id(read("palettes.json")),
        rules=rules,
        culture_cards={c["garmentId"]: c for c in cards},
        fallback=_fallback_from_json(read("fallback-comments.json", {})),
        patterns=patterns, quiz=quiz, scoring=scoring, checklist=checklist,
        version="json",
    )


def load_ui_data(data_dir: Path) -> tuple[dict, list, dict, dict]:
    """Hoạ tiết, quiz, thang điểm, gợi ý checklist luôn đọc từ file JSON (cả khi catalog chính ở Postgres)."""
    def read(name, default):
        p = data_dir / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

    patterns = _by_id(read("patterns.json", [{"id": "tron", "name": "Trơn", "tile": 0, "motif": ""}]))
    return patterns, read("quiz.json", []), read("scoring.json", {}), read("checklist.json", {})


async def load_from_postgres(pool, data_dir: Path) -> Catalog:
    """Đọc schema catalog (bảng do Spring Boot tạo bằng Flyway, xem PLAN-DEV mục 4.2)."""
    async with pool.connection() as conn:
        async def rows(sql):
            cur = await conn.execute(sql)
            cols = [c.name for c in cur.description]
            return [dict(zip(cols, r)) for r in await cur.fetchall()]

        occasions = [{"id": r["id"], "name": r["name"], "palette": list(r["palette"]),
                      "defaultAccessories": r["default_accessories"] or {}}
                     for r in await rows("SELECT id, name, palette, default_accessories FROM catalog.occasions")]
        styles = [{"id": r["id"], "name": r["name"], "preferColors": list(r["prefer_colors"])}
                  for r in await rows("SELECT id, name, prefer_colors FROM catalog.styles")]
        garments = [{"id": r["id"], "name": r["name"], "genders": list(r["genders"]),
                     "occasions": list(r["occasions"]), "hasSvg": r["has_svg"],
                     "defaultColors": r["default_colors"] or {}, "cultureCardId": r["culture_card_id"]}
                    for r in await rows("SELECT * FROM catalog.garments")]
        # uses_accent, by_gender là cột tuỳ chọn: bảng cũ chưa có thì dùng mặc định
        accessories = [{"id": r["id"], "name": r["name"], "slot": r["slot"], "genders": list(r["genders"]),
                        "usesAccent": bool(r.get("uses_accent", r["slot"] in ("head", "hair"))),
                        "byGender": bool(r.get("by_gender", False))}
                       for r in await rows("SELECT * FROM catalog.accessories")]
        colors = [{"id": r["id"], "name": r["name"], "hex": r["hex"]}
                  for r in await rows("SELECT id, name, hex FROM catalog.colors")]
        rules = [{"id": r["id"], "level": r["level"], "when": r["when_cond"], "reason": r["reason"],
                  "suggestion": r["suggestion"], "sources": list(r["sources"] or []), "verified": r["verified"]}
                 for r in await rows("SELECT * FROM catalog.rules WHERE active")]
        cards = [{"id": r["id"], "garmentId": r["garment_id"], "title": r["title"], "body": r["body"],
                  "sources": r["sources"] or []}
                 for r in await rows("SELECT * FROM catalog.culture_cards")]
        fb_rows = await rows("SELECT key, title, comment FROM catalog.fallback_comments")
        meta = {r["k"]: r["v"] for r in await rows("SELECT k, v FROM catalog.meta")}

    fallback = {"by_garment_occasion": {}, "by_garment": {}, "by_rule": {}, "default_tip": ""}
    for r in fb_rows:                      # key: "ao_ngu_than|ky_yeu" | "garment:ao_dai" | "rule:R07" | "default_tip"
        k = r["key"]
        if k == "default_tip":
            fallback["default_tip"] = r["comment"]
        elif k.startswith("garment:"):
            fallback["by_garment"][k[8:]] = {"title": r["title"], "comment": r["comment"]}
        elif k.startswith("rule:"):
            fallback["by_rule"][k[5:]] = r["comment"]
        else:
            fallback["by_garment_occasion"][k] = {"title": r["title"], "comment": r["comment"]}

    patterns, quiz, scoring, checklist = load_ui_data(data_dir)
    # bảng rules trên Postgres có thể chưa có cột criterion: lấy theo mã luật trong data/rules.json
    crit = {r["id"]: r.get("criterion") for r in json.loads((data_dir / "rules.json").read_text(encoding="utf-8"))}         if (data_dir / "rules.json").exists() else {}
    for r in rules:
        r["criterion"] = r.get("criterion") or crit.get(r["id"])
    return Catalog(
        occasions=_by_id(occasions), styles=_by_id(styles), garments=_by_id(garments),
        accessories=_by_id(accessories), colors=_by_id(colors), rules=rules,
        culture_cards={c["garmentId"]: c for c in cards}, fallback=fallback,
        patterns=patterns, quiz=quiz, scoring=scoring, checklist=checklist,
        version=meta.get("catalog_version", "db"),
    )
