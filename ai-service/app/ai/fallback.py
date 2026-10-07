"""Nhánh dự phòng khi không gọi được Gemini: bắt từ khóa để hiểu ý, và câu nhận xét viết sẵn."""
import re
import unicodedata

from app.engine.rules import LEVEL_LABEL
from app.models import CONTEXT_FIELDS, Clarification, ClarifyOption, Evaluation, Intent, OutfitState


def norm(s: str) -> str:
    """Chữ thường, bỏ dấu tiếng Việt, gộp khoảng trắng: 'Đi chùa mùng 1' -> 'di chua mung 1'."""
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


# Thứ tự kiểm tra quan trọng: "đi chùa mùng 1" phải ra le_hoi_chua trước khi khớp "mung 1" của Tết
OCCASION_KEYWORDS = [
    ("ky_yeu", ["ky yeu", "tot nghiep", "chup lop", "graduation", "ra truong"]),
    ("dam_cuoi", ["dam cuoi", "an hoi", "be trap", "dam hoi", "dam cuoi", "le cuoi", "cuoi hoi"]),
    ("le_hoi_chua", ["chua", "le hoi", "hoi lang", "su kien", "le phat", "di le"]),
    ("tet", ["tet", "du xuan", "mung 1", "nam moi", "giao thua"]),
    ("dao_pho", ["dao pho", "di choi", "song ao", "cafe", "ca phe", "chup anh", "pho co"]),
]
UNSUPPORTED_OCCASION = ["dam tang", "dam ma", "tang le"]

STYLE_KEYWORDS = [
    ("pastel", ["nhe nhang", "diu dang", "pastel", "ngot ngao", "diu"]),
    ("toi_gian", ["don gian", "basic", "minimal", "toi gian", "gon gang"]),
    ("duong_pho", ["ca tinh", "street", "nang dong", "duong pho", "streetwear"]),
    ("truyen_thong", ["truyen thong", "co dien", "chuan xua", "phong cach xua", "xua"]),
]

# Tên màu đầy đủ (không trùng nghĩa) khớp trực tiếp
COLOR_FULL = [
    ("do_son", ["do son", "do tuoi", "do do"]), ("vang_hoang", ["vang hoang", "vang nghe"]),
    ("nau_dat", ["nau dat"]), ("hong_dao", ["hong dao", "hong pastel"]), ("trang_nga", ["trang nga"]),
    ("xanh_ngoc", ["xanh ngoc", "xanh mint"]), ("xanh_lam", ["xanh lam", "xanh duong", "xanh navy"]),
    ("xanh_reu", ["xanh reu"]), ("den_tuyen", ["den tuyen"]), ("be_kem", ["be kem"]), ("tim_hue", ["tim hue"]),
]
# Tên màu ngắn dễ trùng nghĩa khi bỏ dấu (do/đó, trang/trắng, tim/tìm, be/bé...) chỉ tính khi có ngữ cảnh màu
COLOR_SHORT = [
    ("do_son", "do"), ("vang_hoang", "vang"), ("nau_dat", "nau"), ("hong_dao", "hong"),
    ("trang_nga", "trang"), ("xanh_reu", "reu"), ("den_tuyen", "den"), ("be_kem", "be"),
    ("be_kem", "kem"), ("tim_hue", "tim"), ("xanh_lam", "xanh"),
]
COLOR_CONTEXT = r"(mau|tong|ao|quan|khan|vay|sac|gam)"

ACCESSORY_KEYWORDS = [
    ("non_quai_thao", ["non quai thao", "quai thao", "non ba tam"]), ("non_la", ["non la"]),
    ("khan_mo_qua", ["khan mo qua", "mo qua"]), ("khan_xep", ["khan xep", "khan dong"]),
    ("hoa_cai_toc", ["hoa cai toc", "cai hoa", "kep hoa"]), ("khan_van", ["khan van", "khan"]),
    ("sneaker", ["sneaker", "giay the thao"]), ("hai_theu", ["hai theu", "giay hai", "doi hai"]),
    ("giay_bup_be", ["giay bup be", "bup be"]), ("giay_ta", ["giay ta", "giay vai"]), ("guoc", ["guoc"]),
    ("tui", ["tui coi", "tui xach", "tui deo", "tui cam tay", "tui vai", "vi cam tay"]),
    ("quat_giay", ["quat giay", "quat xep", "cam quat"]),
    ("kieng_bac", ["kieng", "vong co"]),
    ("trang_suc", ["trang suc", "vong tay", "khuyen tai", "bong tai", "day chuyen"]),
]

GARMENT_KEYWORDS = [
    ("ao_ngu_than", ["ngu than"]), ("ao_tu_than", ["tu than"]), ("nhat_binh", ["nhat binh"]),
    ("ao_ba_ba", ["ba ba"]), ("ao_dai", ["ao dai"]),
]

# Bối cảnh (giá trị khớp data/quiz.json). Tránh từ trùng nghĩa khi bỏ dấu: "mua" (mưa/mùa/mua), "toi" (tối/tôi), "dong" (đông/động)
CONTEXT_KEYWORDS = {
    "weather": [
        ("mua", ["troi mua", "mua phun", "co mua", "mua bao", "ngay mua", "mua rao", "duoi mua", "mua to"]),
        ("lanh", ["troi lanh", "se lanh", "ret", "lanh", "mua dong", "gio mua"]),
        ("nang_nong", ["nang nong", "troi nang", "oi buc", "nong buc", "nang", "nong", "mua he"]),
        ("mat_me", ["mat me", "troi mat", "de chiu", "mua thu"]),
    ],
    "setting": [
        ("ca_hai", ["ca trong lan ngoai", "trong nha va ngoai troi", "ngoai troi va trong nha"]),
        ("ngoai_troi", ["ngoai troi", "cong vien", "bai bien", "san truong", "ngoai pho", "outdoor", "vuon"]),
        ("trong_nha", ["trong nha", "nha hang", "hoi truong", "studio", "indoor", "khach san", "trung tam tiec"]),
    ],
    "timeOfDay": [
        ("buoi_toi", ["buoi toi", "ban dem", "tiec toi", "toi nay", "luc toi", "ve dem"]),
        ("ban_ngay", ["ban ngay", "buoi sang", "buoi chieu", "buoi trua", "sang som", "chieu muon"]),
    ],
    "role": [
        ("be_trap", ["be trap", "phu dau", "phu re", "phu dau phu re"]),
        ("nhan_vat_chinh", ["co dau", "chu re", "tan lang", "tan nuong", "nhan vat chinh", "le tot nghiep cua minh"]),
        ("nhom", ["ca lop", "ca nhom", "dong phuc", "theo nhom", "ca nha"]),
        ("khach", ["di du", "du dam", "du tiec", "khach moi", "lam khach", "dam cuoi ban"]),
        ("chup_anh", ["chup anh", "song ao", "photo", "di choi"]),
    ],
}

NEGATION = re.compile(r"\b(khong thich|khong muon|ghet|tranh|khong can|bo qua|khong)\b")
FEMALE = re.compile(r"\b(nu|con gai|nu sinh|co gai|ban nu|minh la gai)\b")
MALE = re.compile(r"\b(con trai|nam gioi|chang trai|nam sinh|ban nam|minh la nam|la nam)\b")
MALE_WORD = re.compile(r"\bnam\b(?!\s*(moi|nay|nao|sau|truoc|hoc|ngoai|bo))")
NOT_GENDER_NAM = re.compile(r"\b(dau|cuoi|moi|mot|hai|ba|bon)\s+nam\b")


def _has(text: str, kw: str) -> bool:
    return re.search(rf"\b{re.escape(kw)}\b", text) is not None


def _find_all(text: str, table) -> list[str]:
    found, used = [], text
    for code, kws in table:
        for kw in kws:
            if _has(used, kw):
                found.append(code)
                used = re.sub(rf"\b{re.escape(kw)}\b", " ", used)   # "xanh ngoc" không bị khớp lại thành "xanh"
                break
    return found


def _find_colors(text: str) -> list[str]:
    found = _find_all(text, COLOR_FULL)
    for code, short in COLOR_SHORT:
        if code not in found and re.search(rf"\b{COLOR_CONTEXT}\s+(?:\w+\s+)?{short}\b", text):
            found.append(code)
    return found


def default_clarification() -> Clarification:
    return Clarification(
        question="Bạn định mặc Việt phục vào dịp nào nè?",
        options=[
            ClarifyOption(label="Chụp kỷ yếu", occasion="ky_yeu"),
            ClarifyOption(label="Đi chơi Tết", occasion="tet"),
            ClarifyOption(label="Đi chùa, lễ hội", occasion="le_hoi_chua"),
            ClarifyOption(label="Dạo phố chụp ảnh", occasion="dao_pho"),
        ],
    )


def parse_by_keywords(text: str, catalog) -> Intent:
    t = norm(text)
    intent = Intent()

    if not any(_has(t, k) for k in UNSUPPORTED_OCCASION):
        for code, kws in OCCASION_KEYWORDS:
            if any(_has(t, k) for k in kws):
                intent.occasion = code
                break
    for code, kws in STYLE_KEYWORDS:
        if any(_has(t, k) for k in kws):
            intent.style = code
            break

    if FEMALE.search(t):
        intent.gender = "nu"
    elif MALE.search(t) or (MALE_WORD.search(t) and not NOT_GENDER_NAM.search(t)):
        intent.gender = "nam"

    garments = _find_all(t, GARMENT_KEYWORDS)
    intent.preferredGarment = garments[0] if garments else None

    for field, table in CONTEXT_KEYWORDS.items():
        for code, kws in table:
            if any(_has(t, k) for k in kws):
                setattr(intent, field, code)
                break

    # Chia câu thành các vế; vế có từ phủ định thì màu/phụ kiện trong đó là thứ cần tránh
    for clause in re.split(r"\b(nhung|ma|va)\b|,|\.", t):
        if not clause or clause in ("nhung", "ma", "va"):
            continue
        colors, accs = _find_colors(clause), _find_all(clause, ACCESSORY_KEYWORDS)
        if NEGATION.search(clause):
            intent.avoidColors += colors
            intent.avoidAccessories += accs
        else:
            intent.preferredColors += colors
            intent.mustHave += accs

    return finalize_intent(intent, catalog)


def finalize_intent(intent: Intent, catalog) -> Intent:
    """Lọc mã theo catalog, bỏ mâu thuẫn, gắn câu hỏi làm rõ khi thiếu dịp. Dùng cho cả Gemini và fallback."""
    def keep(ids, table):
        out = []
        for i in ids:
            if i in table and i not in out:
                out.append(i)
        return out

    intent.occasion = intent.occasion if intent.occasion in catalog.occasions else None
    intent.style = intent.style if intent.style in catalog.styles else None
    intent.preferredGarment = intent.preferredGarment if intent.preferredGarment in catalog.garments else None
    for field in CONTEXT_FIELDS:
        allowed = catalog.context_values(field)
        if getattr(intent, field) not in allowed:
            setattr(intent, field, None)
    intent.avoidColors = keep(intent.avoidColors, catalog.colors)
    intent.avoidAccessories = keep(intent.avoidAccessories, catalog.accessories)
    intent.preferredColors = [c for c in keep(intent.preferredColors, catalog.colors) if c not in intent.avoidColors][:3]
    intent.mustHave = [a for a in keep(intent.mustHave, catalog.accessories) if a not in intent.avoidAccessories]

    if intent.occasion:
        intent.needsClarification = None
    elif intent.needsClarification is None or not intent.needsClarification.options:
        intent.needsClarification = default_clarification()
    else:
        for o in intent.needsClarification.options:
            o.occasion = o.occasion if o.occasion in catalog.occasions else None
            o.style = o.style if o.style in catalog.styles else None
    return intent


def fallback_comment(o: OutfitState, evals: list[Evaluation], color_note: str, catalog) -> tuple[str, str, str]:
    """(title, comment, tip) viết sẵn cho một bộ đồ."""
    fb = catalog.fallback
    c1, c2 = catalog.name("colors", o.colors.main), catalog.name("colors", o.colors.bottom)
    item = (fb.get("by_garment_occasion", {}).get(f"{o.garment}|{o.occasion}")
            or fb.get("by_garment", {}).get(o.garment)
            or {"title": catalog.name("garments", o.garment),
                "comment": f"{catalog.name('garments', o.garment)} phối {{color1}} với {{color2}} khá hợp dịp này."})
    comment = item["comment"].replace("{color1}", c1.lower()).replace("{color2}", c2.lower())

    worst = next((e for e in evals if e.level != "ok"), None)
    if worst:
        extra = fb.get("by_rule", {}).get(worst.id) or f"{LEVEL_LABEL[worst.level]}: {worst.reason}."
        comment = f"{comment} {extra}"
        tip = worst.suggestion.text
    else:
        comment = f"{comment} {color_note}"
        tip = fb.get("default_tip") or "Bạn có thể vào studio để đổi màu và phụ kiện theo ý mình."
    return item.get("title") or catalog.name("garments", o.garment), comment.strip(), tip
