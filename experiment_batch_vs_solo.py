import time
from mlx_lm import load
from mlx_lm.generate import BatchGenerator

MODEL = "mlx-community/Qwen2.5-1.5B-Instruct-4bit"

model, tokenizer = load(MODEL)
eos_ids = tokenizer.eos_token_ids if hasattr(tokenizer, "eos_token_ids") else {tokenizer.eos_token_id}
print("EOS ids:", eos_ids)

endoftext_ids = tokenizer.encode("<|endoftext|>")
print("<|endoftext|> ids:", endoftext_ids)

stop_ids = [[eid] for eid in eos_ids] + [[eid] for eid in endoftext_ids]
print("Stop ids:", stop_ids)

bg_warmup = BatchGenerator(model, max_tokens=5)
bg_warmup.insert([tokenizer.encode("hello")])
while True:
    p, g = bg_warmup.next()
    if not p and not g:
        break

prompts = [
    "Write a short poem about the ocean.",
    "Explain photosynthesis briefly.",
]
encoded = [tokenizer.encode(p) for p in prompts]

start = time.time()
bg = BatchGenerator(
    model,
    max_tokens=150,
    stop_tokens=stop_ids,
)
bg.insert(encoded)

results = {}
while True:
    prompt_resps, gen_resps = bg.next()
    for r in gen_resps:
        if r.finish_reason is not None:
            results[r.uid] = r.all_tokens
    if not prompt_resps and not gen_resps:
        break
end = time.time()

total_tokens = sum(len(toks) for toks in results.values())
elapsed = end - start
print(f"\nBatched: {len(prompts)} sequences, {total_tokens} total tokens, {elapsed:.2f}s wall clock")
print(f"Effective throughput: {total_tokens/elapsed:.1f} tokens/sec combined\n")

for uid, toks in results.items():
    print(f"--- uid {uid} ---")
    print(tokenizer.decode(toks))
    print()