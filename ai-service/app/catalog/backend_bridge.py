"""Attach the existing cultural catalog to Spring codes without losing context."""
from copy import deepcopy

from app.catalog.sources import load_from_json
from app.core.config import get_settings

EVENTS = {"TET": "tet", "GRADUATION": "ky_yeu", "CULTURAL_EVENT": "dam_cuoi",
          "FESTIVAL": "le_hoi_chua", "PHOTOSHOOT": "dao_pho"}
STYLES = {"TRADITIONAL": "truyen_thong", "MINIMAL": "toi_gian", "GEN_Z": "duong_pho", "ELEGANT": "pastel", "VINTAGE": "truyen_thong"}
ACCESSORIES = {"WHITE_SNEAKERS": "sneaker", "MINIMAL_BAG": "tui", "FAN": "quat_giay"}


def native_catalog(catalog):
    return catalog if catalog.garments else load_from_json(get_settings().data_dir)


def nearest_color(hex_value, colors):
    rgb = lambda h: tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
    value = rgb(hex_value)
    return min(colors, key=lambda c: sum((a-b)**2 for a, b in zip(value, rgb(colors[c]["hex"]))))


def enrich_catalog(cat, native):
    """Request-local copies: aliases never mutate the shared database catalog."""
    aliases = {code.lower(): code for code in cat.garments}
    aliases.update({value: code for code, value in EVENTS.items() if code in cat.occasions})
    for code, value in STYLES.items():
        if code in cat.styles:
            aliases.setdefault(value, code)
    aliases.update({ACCESSORIES.get(code, code.lower()): code for code in cat.accessories})
    aliases.update({code: nearest_color(row["hex"], cat.colors) for code, row in native.colors.items()})

    def translate(value):
        if isinstance(value, dict):
            return {k: translate(v) for k, v in value.items()}
        if isinstance(value, list):
            return list(dict.fromkeys(translate(v) for v in value)) if all(isinstance(v, str) for v in value) else [translate(v) for v in value]
        return aliases.get(value, value) if isinstance(value, str) else value

    for code, row in cat.occasions.items():
        data = native.occasions.get(EVENTS.get(code), {})
        row["palette"] = translate(data.get("palette", []))
        row["defaultAccessories"] = {aliases.get(g, g): translate(accs) for g, accs in data.get("defaultAccessories", {}).items()}
    for code, row in cat.styles.items():
        row["preferColors"] = translate(native.styles.get(STYLES.get(code), {}).get("preferColors", []))
    for code, row in cat.garments.items():
        data = native.garments.get(code.lower(), {})
        row.update({"genders": data.get("genders", ["nu", "nam"]), "occasions": translate(data.get("occasions", []))})
    for code, row in cat.accessories.items():
        data = native.accessories.get(ACCESSORIES.get(code, code.lower()), {})
        row.update({k: deepcopy(v) for k, v in data.items() if k not in ("id", "name")})
    cat.rules = [{**deepcopy(r), "when": translate(r["when"]),
                  "suggestion": translate(r["suggestion"])} for r in native.rules]
    cat.quiz = deepcopy(native.quiz)
    cat.scoring = deepcopy(cat.scoring)
    remix = cat.scoring["remix"]
    by_style = remix['byStyle']
    remix["byStyle"] = {'_khac': by_style['_khac'], **{code: deepcopy(by_style.get(STYLES.get(code), by_style['_khac'])) for code in cat.styles}}
    remix["modernAccessories"] = translate(remix["modernAccessories"])
    return cat
