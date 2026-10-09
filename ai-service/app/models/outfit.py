"""Bộ đồ và kết quả đánh giá. Tên trường khớp hợp đồng JSON trong PLAN-DEV mục 6."""
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field

Level = Literal["ok", "consider", "risk"]        # Phù hợp / Nên cân nhắc / Dễ gây sai lệch
Gender = Literal["nu", "nam"]


class Colors(BaseModel):
    main: str
    bottom: str
    lining: Optional[str] = None
    accent: Optional[str] = None       # màu khăn / phụ kiện đội đầu


class OutfitState(BaseModel):
    v: int = 1
    garment: str
    gender: Gender
    occasion: str
    style: str
    colors: Colors
    colorHex: dict[str, Annotated[str, Field(pattern=r'^#[a-fA-F0-9]{6}$')]] = Field(default_factory=dict, max_length=3)
    pattern: str = "tron"              # hoạ tiết phủ lên vùng màu chính (data/patterns.json)
    accessories: list[str] = Field(default_factory=list)
    bottom: Optional[str] = None       # loại quần/váy: quan_dai_suong | quan_ong_rong | quan_dai | quan_bo | quan_lung | quan_ngan | vay_dai | vay_ngan | khong
    shoes: Optional[str] = None        # loại giày dép: giay_truyen_thong | giay_bet | giay_the_thao | dep | khong


class Suggestion(BaseModel):
    text: str
    patch: Optional[dict] = None


class Evaluation(BaseModel):
    id: str
    level: Level
    reason: str
    suggestion: Suggestion
    sources: list[str] = Field(default_factory=list)
    sourceVerified: bool = False
    sourceNote: str = ""


class ColorScore(BaseModel):
    score: int
    noteKey: str
    note: str


class Criterion(BaseModel):
    id: str                            # cau_truc | dac_trung | phu_kien | boi_canh | cach_tan
    name: str
    en: str = ""
    weight: int                        # trọng số % (data/scoring.json)
    score: int                         # 0–100
    ruleIds: list[str] = Field(default_factory=list)   # luật đã khớp thuộc tiêu chí này
    notes: list[str] = Field(default_factory=list)     # lý do ngắn không đến từ luật (màu, bảng màu dịp...)


class ScoreCard(BaseModel):
    total: int                         # 0–100, trung bình có trọng số của 5 tiêu chí
    band: str                          # chuan_bo | hop_dip | can_chinh
    bandText: str
    capped: bool = False               # bị chặn trần vì có luật "Dễ gây sai lệch"
    criteria: list[Criterion]


class StylistOutfit(BaseModel):
    outfitId: str
    state: OutfitState
    evaluations: list[Evaluation]
    color: ColorScore
    scoreCard: Optional[ScoreCard] = None
    title: str = ""
    comment: str = ""
    tip: str = ""
    whyChosen: str = ""                # lý do bộ này hợp bối cảnh (khi Gemini chọn 3 bộ)


class ReviewAlternative(StylistOutfit):
    changes: list[str] = Field(default_factory=list)   # mô tả ngắn những gì đã đổi so với bộ hiện tại
