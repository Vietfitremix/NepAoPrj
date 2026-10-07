import json

import pytest

from app.ai import norm, parse_by_keywords
from app.core.config import SERVICE_DIR

CASES = json.loads((SERVICE_DIR / "tests" / "understand_cases.json").read_text(encoding="utf-8"))


def test_norm_removes_accents():
    assert norm("Đi chùa mùng 1, Tết!") == "di chua mung 1 tet"


def test_ambiguous_words_are_not_colors(catalog):
    # "đó" không phải màu đỏ, "trang phục" không phải màu trắng, "tui" không phải túi
    i = parse_by_keywords("tui muốn tìm trang phục gì đó cho đẹp", catalog)
    assert i.preferredColors == [] and i.mustHave == []


def test_nam_moi_is_not_male(catalog):
    assert parse_by_keywords("du xuân năm mới", catalog).gender == "khong_ro"


@pytest.mark.parametrize("case", CASES, ids=[c["text"] for c in CASES])
def test_occasion_from_keywords(case, catalog):
    """Bắt từ khóa phải đúng dịp cho cả 20 câu (mục tiêu của Gemini cao hơn: đủ các trường)."""
    assert parse_by_keywords(case["text"], catalog).occasion == case["expect"]["occasion"]
