# Architecture

## Components

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│ prompt queue│───▶│  adapter    │───▶│  cost gov.   │───▶│  composer    │
│  (priority) │    │ (H3/H3Max)  │    │ (hour+day)   │    │ (brand+fcai) │
└─────────────┘    └─────────────┘    └──────────────┘    └──────────────┘
                          │                                       │
                          ▼                                       ▼
                   ┌─────────────┐                         ┌──────────────┐
                   │  poller     │                         │  publisher   │
                   │  (10s loop) │                         │ (file/rtmp)  │
                   └─────────────┘                         └──────────────┘
                          │                                       │
                          ▼                                       ▼
                   ┌─────────────────────────────────────────────────────┐
                   │           receipt writer (JSONL audit log)         │
                   └─────────────────────────────────────────────────────┘
```

## State machine (per prompt)

```
QUEUED ─submit─▶ SUBMITTED ─poll─▶ POLLING ─succeed─▶ READY ─publish─▶ BROADCAST
                  │                  │                            │
                  └─failed─▶ DROPPED └─failed─▶ DROPPED            └─error─▶ RETRY (with backoff)
```

## Invariants

1. **Buffer ahead of broadcast clock ≥ `buffer.min_buffer_seconds`** at all times.
   Violation ⇒ daemon halts publication until buffer refills.
2. **Inflight generation tasks ≤ `cost.max_inflight_tasks`** (default 20, API max 30).
3. **Cost per hour ≤ `cost.max_cost_per_hour_usd`** and per day ≤ `cost.max_cost_per_day_usd`.
4. **Every state transition emits a `Receipt`** to `receipts_path`.
5. **Kill switch is checked between every phase.** Tripping stops new submissions,
   lets inflight tasks drain, halts publication.

## Why async + buffered (not realtime)

- MiniMax video API is **async-only** by design (POST → poll → download).
- Generation latency is **seconds to minutes** per 4-15s clip (no published numbers
  yet — see `benchmarks.md`).
- Therefore the pipeline buffers clips ahead of the broadcast clock and replays
  them. Buffer size = `target_buffer_seconds` (default 180s = 3 minutes).

## What a real implementation needs (TODO before going live)

- [ ] Run benchmarks to measure actual generation latency per tier/resolution
- [ ] Wire up real ffmpeg composition (currently PIL stub produces PNG)
- [ ] Implement clip download from `content.url` and local cache
- [ ] Persistent prompt queue (currently in-memory)
- [ ] Rolling concat: stitch clips into a continuous stream instead of one-clip-per-publish
- [ ] Health probe endpoint (`/healthz`) for monitoring
- [ ] Prometheus metrics export
- [ ] RTMP key rotation
- [ ] Multi-region failover
