"""Tạo data/demo-cache.json cho 5 câu trong kịch bản demo (luôn trả ngay, không phụ thuộc mạng).

Chạy sau khi đã có GEMINI_API_KEY và prompt đã ổn:  python -m scripts.build_demo_cache
Đọc lại từng kết quả trong file trước khi commit.
"""
import asyncio
import json

from app.ai import GeminiClient
from app.catalog import CatalogStore
from app.core.config import get_settings
from app.services.stylist import StylistService
from app.storage.cache import MemoryCache
from app.storage.call_log import MemoryCallLog
from app.storage.rate_limit import RateLimiter

DEMO_SENTENCES = [
    "lớp mình chụp kỷ yếu tháng 12, muốn nhẹ nhàng, thích đi sneaker",
    "đi chùa mùng 1 với mẹ",
    "mai đi đám cưới bạn thân, mình là con trai",
    "dạo phố Hội An, muốn cá tính một chút",
    "muốn mặc gì đó cho đẹp",
]


async def main():
    s = get_settings()
    catalogs = CatalogStore(s)
    await catalogs.reload()
    svc = StylistService(s, catalogs, GeminiClient(s), MemoryCache(0), MemoryCallLog(), RateLimiter(10_000))
    out = {}
    for text in DEMO_SENTENCES:
        resp = await svc.stylist(text, None)
        out[text] = resp
        print(f"[{resp['source']:8}] {resp['kind']:8} {text}")
    path = s.data_dir / "demo-cache.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Đã ghi", path)


if __name__ == "__main__":
    asyncio.run(main())
