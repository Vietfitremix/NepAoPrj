"""Request / response của các endpoint /ai/*."""
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

from .intent import ClarifyOption, Intent
from .outfit import ColorScore, Evaluation, ScoreCard, OutfitState, ReviewAlternative, StylistOutfit

Source = Literal["gemini", "fallback", "cache"]


# ------------------------------------------------------------------ quiz
class QuizOption(BaseModel):
    value: str
    label: str
    hex: Optional[str] = None          # chỉ có ở câu chọn màu


class QuizQuestion(BaseModel):
    id: str
    field: str
    type: Literal["single", "multi"]
    required: bool
    question: str
    options: list[QuizOption]
    placeholder: str = ""


class QuizAnswer(BaseModel):
    """Một câu trả lời: chọn đáp án có sẵn (value) và/hoặc gõ tự do (text)."""
    questionId: str
    value: Optional[Union[str, list[str]]] = None
    text: Optional[str] = Field(default=None, max_length=300)


# ------------------------------------------------------------------ /ai/stylist
class Override(BaseModel):
    occasion: Optional[str] = None
    style: Optional[str] = None
    gender: Optional[Literal["nu", "nam"]] = None


class StylistRequest(BaseModel):
    """Gửi câu trả lời quiz (answers), hoặc một câu gõ nhanh (text), hoặc cả hai."""
    text: Optional[str] = Field(default=None, max_length=300)
    answers: list[QuizAnswer] = Field(default_factory=list)
    override: Optional[Override] = None

    @model_validator(mode="after")
    def need_input(self):
        if not (self.text and self.text.strip()) and not self.answers:
            raise ValueError("Cần ít nhất câu trả lời quiz hoặc một câu mô tả")
        return self


class ClarifyResponse(BaseModel):
    kind: Literal["clarify"] = "clarify"
    question: str
    options: list[ClarifyOption]
    intent: Intent
    source: Source


class OutfitsResponse(BaseModel):
    kind: Literal["outfits"] = "outfits"
    intent: Intent
    outfits: list[StylistOutfit]
    source: Source


# ------------------------------------------------------------------ studio
class EvaluateRequest(BaseModel):
    state: OutfitState
    context: Optional[Intent] = None   # bối cảnh từ quiz: để luật thời tiết, vai trò… áp dụng


class EvaluateResponse(BaseModel):
    evaluations: list[Evaluation]
    color: ColorScore
    scoreCard: ScoreCard


class ExplainRequest(BaseModel):
    state: OutfitState
    context: Optional[Intent] = None
    userRequest: Optional[str] = Field(default=None, max_length=300)


class ExplainResponse(BaseModel):
    title: str
    comment: str
    tip: str
    evaluations: list[Evaluation]
    color: ColorScore
    scoreCard: Optional[ScoreCard] = None
    source: Source


class ReviewRequest(BaseModel):
    """Nút "Hỏi stylist": bộ đồ đang mặc + toàn bộ bối cảnh từ quiz."""
    state: OutfitState
    context: Optional[Intent] = None
    userRequest: Optional[str] = Field(default=None, max_length=300)


class ReviewResponse(BaseModel):
    verdict: Literal["hop", "nen_chinh"]
    verdictText: str                   # "Hợp bối cảnh" | "Nên chỉnh 1 điểm" ...
    current: StylistOutfit
    alternatives: list[ReviewAlternative]
    source: Source
