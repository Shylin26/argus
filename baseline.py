"""
Phase 0 baseline — naive, single-request generation, no batching, no custom
scheduler. Every later optimization gets compared back to these numbers.

Run on wall power, with swap usage confirmed near-zero (check with
`sysctl vm.swapusage` first — swap thrashing invalidates any benchmark).
"""

from mlx_lm import load, generate

MODEL = "mlx-community/Qwen2.5-1.5B-Instruct-4bit"
PROMPT = "Explain unified memory in one sentence."
MAX_TOKENS = 200

if __name__ == "__main__":
    model, tokenizer = load(MODEL)
    response = generate(
        model, tokenizer, prompt=PROMPT, max_tokens=MAX_TOKENS, verbose=True
    )