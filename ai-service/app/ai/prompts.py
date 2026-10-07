"""Đọc prompt từ thư mục prompts/ (file .txt để sửa lời mà không đụng vào code)."""
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


@lru_cache
def load_prompt(name: str) -> str:
    path: Path = get_settings().prompts_dir / f"{name}.txt"
    return path.read_text(encoding="utf-8").strip()
