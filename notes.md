
## 2026-09-13 — Session: batching server + first real stress test

**What shipped:**
- Continuous batching server (server.py) using mlx_lm's BatchGenerator,
  backed by a dedicated scheduler thread (queue.Queue + threading.Event
  pattern) since BatchGenerator isn't thread-safe for concurrent access.
- Confirmed via server logs: concurrent requests get admitted together
  and finish together instead of blocking each other.
- 8-concurrent-request load test: 6.40s combined vs ~51s estimated
  sequential (~8x speedup). Logged in experiments/2026-09-13_load_test_8_concurrent/.

**What I learned:**
- BatchGenerator doesn't auto-handle EOS tokens like generate() does -
  had to find and pass stop_tokens explicitly as a list of single-token
  lists (Sequence[Sequence[int]]).
- Reading a library's actual source (via inspect.getsource) beats
  guessing at an API shape from a docstring - saved real time once
  I started doing this instead of trial-and-error.
- ThreadPoolExecutor.map() reports all results in submission order once
  the WHOLE batch is done, not as each individual request finishes -
  a benchmark-script quirk, not a server bug. Worth remembering for
  Phase 2's telemetry, which needs real per-request timestamps instead.

**Open problem — not yet resolved:**
- Ran a 20-concurrent-request stress test (300 max_tokens each) and got
  118.34s total (~50 tok/s combined) - much worse than the 8-request
  test's ~125 tok/s combined. BUT swap was already at 12.8GB/13.3GB
  used BEFORE the test even started, so this result is likely
  contaminated by system-level memory pressure unrelated to the server
  itself, same failure mode as the Phase 0 baseline issue.
- Need: full restart, verify swap is near-zero, re-run stress test on
  a clean machine before drawing any real conclusion about whether
  16GB can handle 20 concurrent requests or whether max_kv_size limits
  are actually needed.

**Next session:** clean-environment stress test re-run, then decide on
memory limits based on real (uncontaminated) numbers.
