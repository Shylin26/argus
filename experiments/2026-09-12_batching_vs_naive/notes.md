# Experiment: continuous batching vs. naive concurrent requests

**Hypothesis:** BatchGenerator's continuous batching beats both sequential
requests and naive multi-threaded concurrent requests on the same hardware.

**Method:** 2 prompts (ocean poem, photosynthesis), max_tokens=150 each,
compared across three approaches on the same M4/16GB machine, wall power,
swap confirmed near-zero.

**Results:**
- Sequential (1 at a time): ~5.4s total (2 x 2.7s)
- Naive concurrent threads (2 FastAPI requests at once): 6.6s EACH (worse than sequential - bandwidth contention)
- BatchGenerator (continuous batching): 3.34s total for both

**Conclusion:** Continuous batching gave ~38% speedup over sequential and
~2x speedup over naive concurrency, on identical hardware/model/prompts.
Confirms the core motivation for Phase 1's batching work.

**Bug found + fixed along the way:** BatchGenerator doesn't auto-respect
EOS tokens like generate() does - stop_tokens must be passed explicitly as
Sequence[Sequence[int]] (list of single-token-lists, not a flat list).

## 2026-09-12 — Session: batching server working

Built a real HTTP server using BatchGenerator, backed by a dedicated
scheduler thread (queue.Queue + threading.Event pattern) since
BatchGenerator isn't thread-safe for concurrent insert()/next() calls.

Confirmed via server logs: two concurrent requests get admitted together
and finish together, instead of one blocking the other (the naive
single-threaded bottleneck from earlier this week).

Learned: BatchGenerator doesn't auto-handle EOS tokens like generate()
does — had to pass stop_tokens explicitly as list-of-single-token-lists.


# Experiment: 8 concurrent requests load test

**Hypothesis:** the batching server scales throughput roughly linearly
with concurrent requests, not just for 2 at a time.

**Method:** 8 distinct prompts, max_tokens=100 each, fired concurrently
via ThreadPoolExecutor against the running server.

**Result:** all 8 completed in 6.40s combined. Naive sequential estimate:
~51.22s. ~8x speedup.

**Caveat:** ThreadPoolExecutor.map reports results in submission order
once ALL are complete, so per-request timing here isn't precise -
this measures combined throughput, not individual latency. A proper
per-request latency breakdown is Phase 2's job (telemetry).