"""Catalog: kho tri thức văn hóa đã nạp vào bộ nhớ. Mọi mã (id) dùng trong engine và AI đều lấy từ đây."""
from dataclasses import dataclass, field


@dataclass
class Catalog:
    occasions: dict[str, dict]
    styles: dict[str, dict]
    garments: dict[str, dict]
    accessories: dict[str, dict]
    colors: dict[str, dict]
    rules: list[dict]                       # chỉ luật đang active
    culture_cards: dict[str, dict]          # theo garmentId
    fallback: dict = field(default_factory=dict)   # {by_garment_occasion, by_garment, by_rule, default_tip}
    patterns: dict[str, dict] = field(default_factory=dict)
    quiz: list[dict] = field(default_factory=list)
    version: str = "json"

    # --- tra tên tiếng Việt -------------------------------------------------
    def name(self, kind: str, id_: str | None) -> str:
        table = getattr(self, kind)
        return table.get(id_, {}).get("name", id_ or "") if id_ else ""

    def color_hex(self, id_: str | None, default: str = "#CCCCCC") -> str:
        return self.colors.get(id_ or "", {}).get("hex", default)

    # --- bối cảnh từ quiz ---------------------------------------------------
    def quiz_question(self, field_name: str) -> dict | None:
        return next((q for q in self.quiz if q["field"] == field_name), None)

    def context_values(self, field_name: str) -> list[str]:
        """Giá trị hợp lệ cho một trường bối cảnh (weather, setting, timeOfDay, role) theo quiz."""
        q = self.quiz_question(field_name)
        return [o["value"] for o in q["options"]] if q and isinstance(q["options"], list) else []

    def context_label(self, field_name: str, value: str | None) -> str:
        q = self.quiz_question(field_name)
        if not q or not value or not isinstance(q["options"], list):
            return ""
        return next((o["label"] for o in q["options"] if o["value"] == value), value)

    @property
    def wearable_garments(self) -> dict[str, dict]:
        """Trang phục đã có hình SVG để mặc lên người mẫu."""
        return {k: g for k, g in self.garments.items() if g.get("hasSvg")}

    def counts(self) -> dict[str, int]:
        return {
            "occasions": len(self.occasions), "styles": len(self.styles),
            "garments": len(self.garments), "accessories": len(self.accessories),
            "colors": len(self.colors), "rules": len(self.rules), "cultureCards": len(self.culture_cards),
            "patterns": len(self.patterns), "quizQuestions": len(self.quiz),
        }

    def public_view(self) -> dict:
        """Dữ liệu catalog gửi cho giao diện (không gồm luật nội bộ và câu dự phòng)."""
        return {
            "version": self.version,
            "occasions": list(self.occasions.values()),
            "styles": list(self.styles.values()),
            "garments": list(self.garments.values()),
            "accessories": list(self.accessories.values()),
            "colors": list(self.colors.values()),
            "patterns": list(self.patterns.values()),
            "cultureCards": list(self.culture_cards.values()),
        }
