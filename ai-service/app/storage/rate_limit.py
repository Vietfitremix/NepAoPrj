"""Giới hạn số lượt gọi AI theo IP (cửa sổ trượt 60 giây). Vượt giới hạn thì service trả câu dự phòng."""
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, per_minute: int):
        self.per_minute = per_minute
        self._hits: dict[str, deque] = defaultdict(deque)

    def allow(self, ip: str) -> bool:
        now, q = time.monotonic(), self._hits[ip]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= self.per_minute:
            return False
        q.append(now)
        return True
