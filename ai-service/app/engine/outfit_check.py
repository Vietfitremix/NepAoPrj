"""Kiểm tra một bộ đồ gửi từ client: mọi mã phải có trong catalog, mỗi vị trí chỉ một phụ kiện."""
from app.models import OutfitState


class InvalidOutfit(ValueError):
    pass


def validate_outfit(o: OutfitState, catalog) -> OutfitState:
    errors = []
    if o.garment not in catalog.garments:
        errors.append(f"garment '{o.garment}' không có trong catalog")
    elif o.gender not in catalog.garments[o.garment].get("genders", []):
        errors.append(f"garment '{o.garment}' không dành cho gender '{o.gender}'")
    if o.occasion not in catalog.occasions:
        errors.append(f"occasion '{o.occasion}' không có trong catalog")
    if o.style not in catalog.styles:
        errors.append(f"style '{o.style}' không có trong catalog")
    for slot, c in o.colors.model_dump().items():
        if c and c not in catalog.colors:
            errors.append(f"màu {slot} '{c}' không có trong catalog")
    if o.pattern not in catalog.patterns:
        errors.append(f"hoạ tiết '{o.pattern}' không có trong catalog")
    elif (only := catalog.patterns[o.pattern].get("garments")) and o.garment not in only:
        errors.append(f"hoạ tiết '{o.pattern}' không dùng cho '{o.garment}'")
    elif (who := catalog.patterns[o.pattern].get("genders")) and o.gender not in who:
        errors.append(f"hoạ tiết '{o.pattern}' không dành cho '{o.gender}'")
    seen_slots = {}
    for a in o.accessories:
        acc = catalog.accessories.get(a)
        if not acc:
            errors.append(f"phụ kiện '{a}' không có trong catalog")
            continue
        if acc["slot"] in seen_slots:
            errors.append(f"'{a}' và '{seen_slots[acc['slot']]}' cùng vị trí {acc['slot']}")
        seen_slots[acc["slot"]] = a
    if errors:
        raise InvalidOutfit("; ".join(errors))
    return o


def apply_patch(o: OutfitState, patch: dict | None) -> OutfitState:
    """Áp gợi ý thay thế của luật (suggestion.patch) lên bộ đồ."""
    if not patch:
        return o
    data = o.model_dump()
    for k, v in patch.items():
        if k == "colors" and isinstance(v, dict):
            data["colors"].update(v)
        else:
            data[k] = v
    return OutfitState.model_validate(data)
