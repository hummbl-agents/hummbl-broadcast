"""Prompt queue with priority + dedup."""

from __future__ import annotations

import asyncio
import heapq
from dataclasses import dataclass, field

from .models import Prompt


@dataclass(order=True)
class _Item:
    priority: int
    seq: int
    prompt: Prompt = field(compare=False)


class PromptQueue:
    """Async priority queue. Higher priority value = processed first. FIFO within priority."""

    def __init__(self, max_size: int = 1000) -> None:
        self._heap: list[_Item] = []
        self._seen: set[str] = set()
        self._max = max_size
        self._seq = 0
        self._cond = asyncio.Condition()

    async def put(self, prompt: Prompt) -> bool:
        """Returns False if duplicate or queue full."""
        async with self._cond:
            if prompt.id in self._seen:
                return False
            if len(self._heap) >= self._max:
                return False
            self._seen.add(prompt.id)
            self._seq += 1
            heapq.heappush(self._heap, _Item(-prompt.priority, self._seq, prompt))
            self._cond.notify()
            return True

    async def get(self) -> Prompt:
        async with self._cond:
            while not self._heap:
                await self._cond.wait()
            item = heapq.heappop(self._heap)
            self._seen.discard(item.prompt.id)
            return item.prompt

    def qsize(self) -> int:
        return len(self._heap)
