"""Prompt queue tests."""

import asyncio

import pytest

from hummbl_broadcast.models import Prompt
from hummbl_broadcast.queue import PromptQueue


@pytest.mark.asyncio
async def test_put_and_get_fifo_within_priority():
    q = PromptQueue()
    await q.put(Prompt(id="a", text="x", priority=1))
    await q.put(Prompt(id="b", text="y", priority=1))
    assert (await q.get()).id == "a"
    assert (await q.get()).id == "b"


@pytest.mark.asyncio
async def test_priority_ordering():
    q = PromptQueue()
    await q.put(Prompt(id="low", text="x", priority=0))
    await q.put(Prompt(id="high", text="y", priority=10))
    assert (await q.get()).id == "high"
    assert (await q.get()).id == "low"


@pytest.mark.asyncio
async def test_dedup():
    q = PromptQueue()
    assert await q.put(Prompt(id="x", text="a")) is True
    assert await q.put(Prompt(id="x", text="b")) is False


@pytest.mark.asyncio
async def test_get_blocks_when_empty():
    q = PromptQueue()

    async def producer() -> None:
        await asyncio.sleep(0.05)
        await q.put(Prompt(id="x", text="y"))

    asyncio.create_task(producer())
    p = await asyncio.wait_for(q.get(), timeout=1.0)
    assert p.id == "x"
