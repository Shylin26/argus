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