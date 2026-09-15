
## 2026-09-13
### Added
- Continuous batching HTTP server (server.py) via mlx_lm's BatchGenerator
- Scheduler thread with queue-based request admission
- Load test script (benchmarks/load_test.py) - 8 concurrent requests, ~8x speedup confirmed
- Stress test script (benchmarks/stress_test.py) - 20 concurrent requests

### Known issues
- Stress test results under investigation - possible system-level swap
  contamination, needs clean-environment re-run before trusting the numbers
# Changelog

## 2026-09-13
### Added
- Continuous batching HTTP server (server.py) via mlx_lm's BatchGenerator
- Scheduler thread with queue-based request admission
- Load test script (benchmarks/load_test.py) - 8 concurrent requests, ~8x speedup confirmed
- Stress test script (benchmarks/stress_test.py) - 20 concurrent requests

### Known issues
- Stress test results under investigation - possible system-level swap
  contamination, needs clean-environment re-run before trusting the numbers

## 2026-09-10/11
### Added
- Phase 0: MLX verified on GPU, baseline.py, first working inference (55.1 tok/s generation)
