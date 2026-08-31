"""Publisher protocol + file/rtmp implementations."""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import Protocol

from .models import Clip


class Publisher(Protocol):
    async def publish(self, clip_path: Path) -> None: ...
    async def aclose(self) -> None: ...


class FilePublisher:
    """Writes clips to a directory. Real impl will concatenate into a rolling buffer."""

    def __init__(self, output_dir: str) -> None:
        self._dir = Path(output_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    async def publish(self, clip_path: Path) -> None:
        # For skeleton we just symlink/copy. Real impl appends to a rolling concat.
        target = self._dir / clip_path.name
        if target.exists():
            target.unlink()
        target.symlink_to(clip_path.resolve())

    async def aclose(self) -> None:
        pass


class RTMPPublisher:
    """ffmpeg-based RTMP push. Requires ffmpeg in PATH."""

    def __init__(self, rtmp_url: str, rtmp_key: str | None = None) -> None:
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg not found in PATH; required for RTMP publisher")
        url = rtmp_url
        if rtmp_key:
            url = f"{rtmp_url.rstrip('/')}/{rtmp_key}"
        self._url = url
        self._proc: subprocess.Popen[bytes] | None = None

    async def publish(self, clip_path: Path) -> None:
        # Real impl would maintain a single persistent ffmpeg process that reads
        # from a stdin pipe; this skeleton just verifies the binary exists.
        cmd = [
            "ffmpeg",
            "-re",
            "-i",
            str(clip_path),
            "-c",
            "copy",
            "-f",
            "flv",
            self._url,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        await proc.wait()

    async def aclose(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
            self._proc = None
