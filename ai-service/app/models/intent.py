"""Bối cảnh của người dùng (Intent): lấy từ quiz, từ câu gõ tự do (Gemini hoặc bắt từ khóa), hoặc cả hai."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ClarifyOption(BaseModel):
    label: str
    occasion: Optional[str] = None
    style: Optional[str] = None


class Clarification(BaseModel):
    question: str
    options: list[ClarifyOption]


class Intent(BaseModel):
    # dịp và phong cách
    occasion: Optional[str] = None
    style: Optional[str] = None
    gender: Literal["nu", "nam", "khong_ro"] = "khong_ro"
    # bối cảnh (giá trị hợp lệ lấy từ data/quiz.json)
    weather: Optional[str] = None        # nang_nong | mat_me | lanh | mua
    setting: Optional[str] = None        # ngoai_troi | trong_nha | ca_hai
    timeOfDay: Optional[str] = None      # ban_ngay | buoi_toi
    role: Optional[str] = None           # khach | nhan_vat_chinh | be_trap | nhom | chup_anh
    # mong muốn về trang phục
    preferredGarment: Optional[str] = None
    preferredColors: list[str] = Field(default_factory=list)
    mustHave: list[str] = Field(default_factory=list)
    avoidAccessories: list[str] = Field(default_factory=list)
    avoidColors: list[str] = Field(default_factory=list)
    needsClarification: Optional[Clarification] = None


# Các trường bối cảnh có danh sách giá trị cố định trong quiz
CONTEXT_FIELDS = ("weather", "setting", "timeOfDay", "role")
