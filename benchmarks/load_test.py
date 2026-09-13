import time
import requests
import concurrent.futures

URL = "http://127.0.0.1:8000/generate"

PROMPTS = [
    "Write a short poem about the ocean.",
    "Explain photosynthesis briefly.",
    "What causes rain?",
    "Describe a sunset in one paragraph.",
    "What is machine learning?",
    "Write a haiku about mountains.",
    "Explain gravity simply.",
    "What is the capital of France?",
]

def send_request(prompt):
    start = time.time()
    resp = requests.post(URL, json={"prompt": prompt, "max_tokens": 100})
    elapsed = time.time() - start
    return {
        "prompt": prompt[:30],
        "elapsed": elapsed,
        "status": resp.status_code,
    }

if __name__ == "__main__":
    n_users = len(PROMPTS)
    print(f"Firing {n_users} concurrent requests...")

    overall_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_users) as executor:
        results = list(executor.map(send_request, PROMPTS))
    overall_elapsed = time.time() - overall_start

    print(f"\nAll {n_users} requests completed in {overall_elapsed:.2f}s total\n")
    for r in results:
        print(f"  {r['elapsed']:.2f}s  [{r['status']}]  {r['prompt']}")

    avg = sum(r["elapsed"] for r in results) / len(results)
    print(f"\nAverage per-request time: {avg:.2f}s")
    print(f"If run sequentially instead, rough estimate: {avg * n_users:.2f}s")