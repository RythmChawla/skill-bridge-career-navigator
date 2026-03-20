"""Very small in-memory rate limiter (per IP + endpoint)."""
import time
from collections import defaultdict, deque
from typing import Deque, Tuple


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.events: dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    def allow(self, key: Tuple[str, str]) -> bool:
        now = time.time()
        dq = self.events[key]
        while dq and dq[0] <= now - self.window:
            dq.popleft()
        if len(dq) >= self.limit:
            return False
        dq.append(now)
        return True
