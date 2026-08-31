"""VideoAdapter protocol — every backend must satisfy this."""

from __future__ import annotations

from typing import Protocol

from ..models import Clip, Prompt, Task


class VideoAdapter(Protocol):
    """Async video generation adapter.

    Lifecycle:
        submit(prompt) -> Task
        poll(task) -> Task (status updated)
        on success, task.status == "succeeded" and task has download URL somewhere
        download(task) -> Clip
    """

    async def submit(self, prompt: Prompt) -> Task: ...
    async def poll(self, task: Task) -> Task: ...
    async def download(self, task: Task) -> Clip: ...
    async def aclose(self) -> None: ...
