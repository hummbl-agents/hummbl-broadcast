"""Adapter contract tests — same expectations for mock and real."""

import asyncio

import pytest

from hummbl_broadcast.adapters import make_adapter
from hummbl_broadcast.models import ModelTier, Prompt, Resolution


@pytest.mark.asyncio
async def test_mock_submit_then_succeed():
    a = make_adapter("mock", poll_interval_seconds=0.1)
    p = Prompt(id="p1", text="a dancer", tier=ModelTier.H3_MAX_480P,
               resolution=Resolution.P480, duration_seconds=5)
    task = await a.submit(p)
    assert task.status == "queued"
    assert task.task_id

    # wait for synthetic completion
    for _ in range(20):
        await asyncio.sleep(0.05)
        task = await a.poll(task)
        if task.status == "succeeded":
            break
    assert task.status == "succeeded"

    clip = await a.download(task)
    assert clip.tier == ModelTier.H3_MAX_480P
    assert clip.duration_seconds == 5
    assert clip.cost_usd == 0.0  # mock has no cost
    await a.aclose()


@pytest.mark.asyncio
async def test_minimax_adapter_requires_api_key():
    with pytest.raises(ValueError, match="MINIMAX_API_KEY"):
        make_adapter("minimax-h3-max", api_key=None)
