"""Quiz và bối cảnh.

build_quiz(): danh sách câu hỏi cho giao diện (đáp án màu lấy từ bảng màu trong catalog).
build_context(): gộp câu trả lời quiz + câu gõ tự do thành một Intent:
  - đáp án bấm chọn được dùng thẳng (không tốn lượt gọi Gemini);
  - phần gõ tự do được Gemini đọc hiểu (lỗi thì bắt từ khóa), chỉ điền vào các trường còn trống.
"""
from app.ai import finalize_intent, understand
from app.models import Intent, QuizAnswer, QuizOption, QuizQuestion

LIST_FIELDS = ("preferredColors", "mustHave", "avoidAccessories", "avoidColors")


def build_quiz(catalog) -> list[QuizQuestion]:
    out = []
    for q in catalog.quiz:
        if q["options"] == "palette":
            opts = [QuizOption(value=c["id"], label=c["name"], hex=c["hex"]) for c in catalog.colors.values()]
        else:
            opts = [QuizOption(**o) for o in q["options"]]
        out.append(QuizQuestion(id=q["id"], field=q["field"], type=q["type"], required=q["required"],
                                question=q["question"], options=opts, placeholder=q.get("placeholder", "")))
    return out


def _from_choices(answers: list[QuizAnswer], catalog) -> tuple[Intent, list[str]]:
    """Đáp án bấm chọn -> Intent; gom phần gõ tự do kèm câu hỏi để Gemini hiểu đúng ngữ cảnh."""
    intent, texts = Intent(), []
    by_id = {q["id"]: q for q in catalog.quiz}
    for a in answers:
        q = by_id.get(a.questionId)
        if not q:
            continue
        if a.value:
            if q["type"] == "multi":
                values = a.value if isinstance(a.value, list) else [a.value]
                setattr(intent, q["field"], list(values)[:3])
            else:
                setattr(intent, q["field"], a.value if isinstance(a.value, str) else a.value[0])
        if a.text and a.text.strip():
            texts.append(f"{q['question']} -> {a.text.strip()}")
    return intent, texts


def _merge(base: Intent, parsed: Intent) -> Intent:
    """Trường đã chọn trong quiz được giữ; trường còn trống lấy từ phần gõ tự do; danh sách thì gộp."""
    data = base.model_dump()
    for k, v in parsed.model_dump().items():
        if k == "needsClarification":
            continue
        if k in LIST_FIELDS:
            data[k] = list(dict.fromkeys((data[k] or []) + (v or [])))
        elif k == "gender":
            data[k] = data[k] if data[k] != "khong_ro" else v
        elif data.get(k) in (None, "") and v not in (None, ""):
            data[k] = v
    return Intent.model_validate(data)


async def build_context(answers: list[QuizAnswer], text: str | None, catalog, gemini, log=None) -> tuple[Intent, str | None]:
    """Trả về (intent, source của bước hiểu ý). source = None khi chỉ có đáp án bấm chọn (không gọi AI)."""
    intent, texts = _from_choices(answers, catalog)
    if text and text.strip():
        texts.insert(0, text.strip())
    source = None
    if texts:
        parsed, source = await understand("\n".join(texts)[:600], catalog, gemini, log)
        intent = _merge(intent, parsed)
    return finalize_intent(intent, catalog), source
