"""Cache kết quả /ai/stylist theo câu người dùng.

- Câu demo (data/demo-cache.json) được ghim: luôn trả ngay, không hết hạn.
- MemoryCache: chạy local. PostgresCache: bảng ai.ai_cache (PLAN-DEV mục 4.2).
"""
import hashlib
import json
import time
from pathlib import Path

from app.ai.fallback import norm


def cache_key(text: str, override: dict | None) -> str:
    raw = norm(text) + "|" + json.dumps(override or {}, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def load_demo_cache(data_dir: Path) -> dict[str, dict]:
    """demo-cache.json: {"<câu>": <response>} -> {key: response}."""
    p = data_dir / "demo-cache.json"
    if not p.exists():
        return {}
    raw = json.loads(p.read_text(encoding="utf-8"))
    return {cache_key(text, None): resp for text, resp in raw.items()}


class MemoryCache:
    def __init__(self, ttl_s: int, pinned: dict[str, dict] | None = None, max_items: int = 500):
        self.ttl_s, self.max_items = ttl_s, max_items
        self.pinned = pinned or {}
        self._items: dict[str, tuple[float, dict]] = {}

    async def get(self, key: str) -> dict | None:
        if key in self.pinned:
            return self.pinned[key]
        hit = self._items.get(key)
        if hit and hit[0] > time.time():
            return hit[1]
        self._items.pop(key, None)
        return None

    async def set(self, key: str, text: str, response: dict, source: str) -> None:
        if len(self._items) >= self.max_items:
            self._items.pop(next(iter(self._items)))
        self._items[key] = (time.time() + self.ttl_s, response)


class PostgresCache(MemoryCache):
    """Đọc ghim + bộ nhớ trước, rồi tới bảng ai.ai_cache. Ghi lỗi thì bỏ qua (không làm hỏng request)."""

    def __init__(self, pool, ttl_s: int, pinned: dict[str, dict] | None = None):
        super().__init__(ttl_s, pinned, max_items=200)
        self.pool = pool

    async def get(self, key: str) -> dict | None:
        hit = await super().get(key)
        if hit:
            return hit
        try:
            async with self.pool.connection() as conn:
                cur = await conn.execute(
                    "UPDATE ai.ai_cache SET hits = hits + 1 WHERE key = %s "
                    "AND (pinned OR created_at > now() - make_interval(secs => %s)) RETURNING response",
                    (key, self.ttl_s))
                row = await cur.fetchone()
            return row[0] if row else None
        except Exception:
            return None

    async def set(self, key: str, text: str, response: dict, source: str, pinned: bool = False) -> None:
        await super().set(key, text, response, source)
        try:
            from psycopg.types.json import Jsonb
            async with self.pool.connection() as conn:
                await conn.execute(
                    "INSERT INTO ai.ai_cache (key, request_text, response, source, pinned) VALUES (%s, %s, %s, %s, %s) "
                    "ON CONFLICT (key) DO UPDATE SET response = EXCLUDED.response, source = EXCLUDED.source, "
                    "pinned = ai.ai_cache.pinned OR EXCLUDED.pinned, created_at = now()",
                    (key, text, Jsonb(response), source, pinned))
        except Exception:
            pass
