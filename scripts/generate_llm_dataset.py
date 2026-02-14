
import json, random
from datetime import datetime, timedelta

MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4-legacy", "codex-lite", "gpt-4-cheap", "gpt-3.5-cheap", "gpt-4-highlatency"]
ERR_RATE = 0.03
N = 500

start = datetime.utcnow()
out = []
for i in range(N):
    model = random.choice(MODELS)
    prompt_tokens = max(1, int(random.gauss(180, 120)))
    completion_tokens = max(0, int(random.gauss(320, 400)))
    base = {"gpt-4o-mini":80, "gpt-3.5-turbo":120, "gpt-4-legacy":350, "gpt-4o":220, "codex-lite":90, "gpt-4-cheap":300, "gpt-3.5-cheap":150, "gpt-4-highlatency":900}[model]
    latency_ms = max(30, int(random.gauss(base + (completion_tokens*0.4), base*0.25)))
    error = None
    status = "ok"
    if random.random() < ERR_RATE:
        error = random.choice(["timeout","rate_limit","internal_error"])
        status = "error"
    ts = (start + timedelta(seconds=i*2)).isoformat() + "Z"
    price_prompt_per_1k = 0.03
    price_completion_per_1k = 0.06
    cost_usd = (prompt_tokens/1000.0)*price_prompt_per_1k + (completion_tokens/1000.0)*price_completion_per_1k
    record = {
        "timestamp": ts,
        "request_id": f"req_{i:06d}",
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "latency_ms": latency_ms,
        "status": status,
        "error": error,
        "input_chars": random.randint(50, 8000),
        "output_chars": max(0, completion_tokens*4),
        "cost_usd": round(cost_usd, 6)
    }
    out.append(record)

with open("data/llm_api_responses.jsonl","w",encoding="utf-8") as fh:
    for r in out:
        fh.write(json.dumps(r) + "\n")
print("Wrote data/llm_api_responses.jsonl:", len(out), "rows")
