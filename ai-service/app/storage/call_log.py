"""Nhật ký mỗi lần gọi Gemini: số liệu cho phần "chỉ số đo" (độ trễ, tỉ lệ dùng dự phòng)."""
import time
from collections import Counter, deque


class MemoryCallLog:
    def __init__(self, max_items: int = 1000):
        self.items: deque = deque(maxlen=max_items)

    async def __call__(self, endpoint: str, model: str | None, latency_ms: int | None,
                       source: str, ok: bool, error: str | None = None) -> None:
        self.items.append({"endpoint": endpoint, "model": model, "latencyMs": latency_ms,
                           "source": source, "ok": ok, "error": error, "at": time.time()})

    async def stats(self) -> dict:
        items = list(self.items)
        lat = sorted(i["latencyMs"] for i in items if i["latencyMs"] is not None)
        return {
            "calls": len(items),
            "bySource": dict(Counter(i["source"] for i in items)),
            "byEndpoint": dict(Counter(i["endpoint"] for i in items)),
            "avgLatencyMs": round(sum(lat) / len(lat)) if lat else None,
            "p95LatencyMs": lat[int(len(lat) * 0.95) - 1] if len(lat) >= 2 else (lat[0] if lat else None),
            "recentErrors": [i["error"] for i in items if i["error"]][-5:],
        }


class PostgresCallLog(MemoryCallLog):
    """Ghi thêm vào bảng ai.ai_calls; lỗi ghi thì bỏ qua."""

    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def __call__(self, endpoint, model, latency_ms, source, ok, error=None):
        await super().__call__(endpoint, model, latency_ms, source, ok, error)
        try:
            async with self.pool.connection() as conn:
                await conn.execute(
                    "INSERT INTO ai.ai_calls (endpoint, model, latency_ms, source, ok, error) VALUES (%s,%s,%s,%s,%s,%s)",
                    (endpoint, model, latency_ms, source, ok, error))
        except Exception:
            pass
