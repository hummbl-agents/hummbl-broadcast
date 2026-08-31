"""Receipt writer — append-only JSONL audit log."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Receipt


class ReceiptWriter:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, r: Receipt) -> None:
        with self._path.open("a", encoding="utf-8") as f:
            f.write(r.model_dump_json() + "\n")
