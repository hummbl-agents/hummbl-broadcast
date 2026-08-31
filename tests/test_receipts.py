"""Receipt writer tests."""

import json
from pathlib import Path

from hummbl_broadcast.models import Receipt
from hummbl_broadcast.receipts import ReceiptWriter


def test_writes_one_jsonl_line(tmp_path: Path):
    path = tmp_path / "receipts.jsonl"
    w = ReceiptWriter(path)
    w.write(Receipt(event="submit", prompt_id="p1", task_id="t1"))
    w.write(Receipt(event="success", prompt_id="p1", task_id="t1", cost_usd=0.25))

    lines = path.read_text().splitlines()
    assert len(lines) == 2
    obj = json.loads(lines[0])
    assert obj["event"] == "submit"
    assert obj["prompt_id"] == "p1"


def test_creates_parent_dir(tmp_path: Path):
    path = tmp_path / "nested" / "deep" / "r.jsonl"
    ReceiptWriter(path).write(Receipt(event="x"))
    assert path.exists()
