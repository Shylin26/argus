from mlx_lm import load
from mlx_lm.generate import BatchGenerator

MODEL = "mlx-community/Qwen2.5-1.5B-Instruct-4bit"

model, tokenizer = load(MODEL)

prompt1 = tokenizer.encode("Write a short poem about the ocean.")
prompt2 = tokenizer.encode("Explain photosynthesis briefly.")

bg = BatchGenerator(model, max_tokens=20)
bg.insert([prompt1, prompt2])

for step in range(40):
    prompt_resps, gen_resps = bg.next()
    if gen_resps:
        print(f"--- step {step} ---")
        for r in gen_resps:
            print(r)
    if not prompt_resps and not gen_resps:
        print(f"step {step}: nothing left, stopping")
        break