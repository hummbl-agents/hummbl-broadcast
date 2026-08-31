# benchmarks.md — what we need to measure before going live

## Status: NOT RUN

This skeleton has **no real benchmarks yet**. The `cost_usd` field on clips from
the mock adapter is `0.0`. The `latency_seconds` field is a synthetic 2s.

We need actual measurements before this can ship to a real broadcast.

## What to measure

### Per-tier latency (wall-clock submit → succeeded)

For each (model, resolution) pair below, run **N=30 generations** with the same
prompt and record:
- `submit_latency_seconds`: time to POST /v2/video_generation return task_id
- `time_to_first_poll_success_seconds`: time to first 200 from poll endpoint
- `time_to_succeeded_seconds`: time from submit to status="succeeded"
- `time_to_downloaded_seconds`: time to fetch content.url to local file

Pairs:
- MiniMax-H3 @ 768P, 5s clip
- MiniMax-H3 @ 768P, 10s clip
- MiniMax-H3 @ 2K, 5s clip
- MiniMax-H3-Max @ 480P, 5s clip
- MiniMax-H3-Max @ 480P, 10s clip
- MiniMax-H3-Max @ 768P, 5s clip

### Concurrency behavior

For each tier:
- Submit 30 tasks in parallel (the API max)
- Record queue wait time, total elapsed, failure rate
- Verify our `cost.max_inflight_tasks=20` safety margin is safe

### Quality assessment (subjective, requires human review)

- Does H3 Max 480P meet HUMMBL brand bar?
- Does text rendering in H3 2K actually work for logo overlays?
- Are 5s clips long enough for our content type?

## How to run (once we have API key)

```bash
export MINIMAX_API_KEY=...
cd ~/PROJECTS/hummbl-broadcast
uv pip install -e ".[dev]"
python -m benchmarks.run --output docs/benchmarks-raw.json
python -m benchmarks.analyze docs/benchmarks-raw.json > docs/benchmarks-summary.md
```

(Benchmark scripts not yet written — see TODO in `scripts/`.)

## Acceptance gate

`standards.md` cannot move from DRAFT to FINAL until:
- [ ] All 6 latency benchmarks above completed
- [ ] Concurrency test completed with success rate ≥ 95%
- [ ] At least one human-reviewed quality pass per tier
- [ ] Cost projections match MiniMax's published rates within ±5%
