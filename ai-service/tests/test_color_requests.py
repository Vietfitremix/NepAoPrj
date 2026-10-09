"""Màu người dùng muốn/tránh được hiểu đúng từ lời nhắn của quiz và câu kể tự do."""
import pytest

from app.api.routers.backend import COLOR_ALIASES, requested_items

COLORS = {code: {"name": name} for code, name in {
    "RED": "Đỏ", "DARK_RED": "Đỏ sẫm", "WHITE": "Trắng", "BLUE": "Xanh dương", "YELLOW": "Vàng", "BLACK": "Đen",
    "CREAM": "Kem", "GREEN": "Xanh lá", "PINK": "Hồng", "PURPLE": "Tím", "BROWN": "Nâu"}.items()}


def parse(text):
    return requested_items(text, COLORS, COLOR_ALIASES)


def test_quiz_colours_are_wanted_not_avoided():
    wanted, avoided = parse("Dịp: Tết. Màu ưa thích: Xanh lá, Vàng. Phong cách: Truyền thống")
    assert wanted == ["GREEN", "YELLOW"] and avoided == []


def test_skip_hint_in_question_text_does_not_avoid_the_first_colour():
    # Câu hỏi cũ "(chọn tối đa 3, có thể bỏ qua)" từng làm màu đầu tiên bị loại.
    wanted, avoided = parse("Màu bạn thích? (chọn tối đa 3, có thể bỏ qua) Đỏ, Hồng")
    assert wanted == ["RED", "PINK"] and avoided == []


def test_noun_bo_is_not_a_negation():
    wanted, avoided = parse("cần một bộ áo dài màu đỏ cho Tết")
    assert wanted == ["RED"] and avoided == []


@pytest.mark.parametrize("text, wanted, avoided", [
    ("không thích màu đỏ nhưng thích xanh dương", ["BLUE"], ["RED"]),
    ("Tết, tránh màu đen và thích vàng", ["YELLOW"], ["BLACK"]),
    ("không thích đỏ, đen", [], ["RED", "BLACK"]),                 # danh sách sau lời phủ định giữ ý phủ định
    ("Màu ưa thích: Vàng, Tím. không thích đỏ", ["YELLOW", "PURPLE"], ["RED"]),
])
def test_negation(text, wanted, avoided):
    assert parse(text) == (wanted, avoided)


@pytest.mark.parametrize("text, expected", [
    ("áo dài đỏ sẫm", ["DARK_RED"]),                  # tên dài khớp trước, không lẫn với "đỏ"
    ("áo xanh lá cây", ["GREEN"]),
    ("thích màu xanh", ["BLUE"]),                     # "xanh" đứng một mình hiểu là xanh dương
    ("hồng đào pastel", ["PINK"]),
    ("tông nâu đất", ["BROWN"]),
    ("tím Huế", ["PURPLE"]),
    ("trắng ngà", ["CREAM"]),
])
def test_colour_names_and_aliases(text, expected):
    assert parse(text)[0] == expected


def test_colour_requested_and_avoided_resolves_to_avoided():
    wanted, avoided = parse("Màu ưa thích: Hồng. không thích hồng")
    assert wanted == [] and avoided == ["PINK"]
