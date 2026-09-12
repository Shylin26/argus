import threading
import queue
import time
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from mlx_lm import load
from mlx_lm.generate import BatchGenerator

MODEL_NAME = "mlx-community/Qwen2.5-1.5B-Instruct-4bit"

app = FastAPI()

print("Loading model...")
model, tokenizer = load(MODEL_NAME)
print("Model loaded.")

eos_ids = tokenizer.eos_token_ids if hasattr(tokenizer, "eos_token_ids") else {tokenizer.eos_token_id}
endoftext_ids = tokenizer.encode("<|endoftext|>")
STOP_IDS = [[eid] for eid in eos_ids] + [[eid] for eid in endoftext_ids]

bg = BatchGenerator(model, stop_tokens=STOP_IDS)

incoming_queue = queue.Queue()
lock = threading.Lock()
events = {}          # request_id -> threading.Event
results = {}         # request_id -> list of output tokens
uid_to_request = {}  # bg's internal uid -> our request_id


def scheduler_loop():
    while True:
        new_items = []
        while True:
            try:
                new_items.append(incoming_queue.get_nowait())
            except queue.Empty:
                break

        if new_items:
            prompts = [item["tokens"] for item in new_items]
            max_toks = [item["max_tokens"] for item in new_items]
            uids = bg.insert(prompts, max_tokens=max_toks)
            with lock:
                for uid, item in zip(uids, new_items):
                    uid_to_request[uid] = item["request_id"]
                    print(f"[scheduler] admitted request {item['request_id'][:8]} as uid {uid}")

        prompt_resps, gen_resps = bg.next()

        for r in gen_resps:
            if r.finish_reason is not None:
                with lock:
                    request_id = uid_to_request.pop(r.uid, None)
                if request_id:
                    results[request_id] = r.all_tokens
                    events[request_id].set()
                    print(f"[scheduler] finished request {request_id[:8]} (uid {r.uid})")

        if not new_items and not prompt_resps and not gen_resps:
            time.sleep(0.005)  # nothing to do, avoid burning CPU spinning


threading.Thread(target=scheduler_loop, daemon=True).start()


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 200


@app.post("/generate")
def generate_text(req: GenerateRequest):
    request_id = str(uuid.uuid4())
    tokens = tokenizer.encode(req.prompt)
    event = threading.Event()

    with lock:
        events[request_id] = event

    incoming_queue.put({
        "request_id": request_id,
        "tokens": tokens,
        "max_tokens": req.max_tokens,
    })

    event.wait()  # this HTTP request's thread blocks here until the scheduler finishes it

    with lock:
        result_tokens = results.pop(request_id)
        events.pop(request_id, None)

    return {"response": tokenizer.decode(result_tokens)}