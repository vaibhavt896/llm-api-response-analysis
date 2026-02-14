#!/usr/bin/env python3
import json, os
import pandas as pd
import numpy as np
import matplotlib
# use non-interactive backend so script runs in terminal without display
matplotlib.use('Agg')
import matplotlib.pyplot as plt

IN = "data/llm_api_responses.jsonl"
OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return pd.json_normalize(rows)

df = load_jsonl(IN)

# ensure numeric types
for c in ["prompt_tokens","completion_tokens","total_tokens","latency_ms","cost_usd","input_chars","output_chars"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# keep expected statuses
df = df[df["status"].isin(["ok","error"])]

# per-model aggregations
agg = df.groupby("model").agg(
    requests=("request_id","count"),
    errors=("status", lambda s: (s=="error").sum()),
    median_latency_ms=("latency_ms","median"),
    p95_latency_ms=("latency_ms", lambda x: np.percentile(x.dropna(),95) if x.dropna().size else np.nan),
    mean_total_tokens=("total_tokens","mean"),
    median_cost_usd=("cost_usd","median"),
    total_cost_usd=("cost_usd","sum")
).reset_index()

agg.to_csv(os.path.join(OUT,"model_summary.csv"), index=False)

# top 20 costly requests
df.sort_values("cost_usd", ascending=False).head(20).to_csv(os.path.join(OUT,"top_20_costly_requests.csv"), index=False)

# plots
plt.figure(figsize=(8,4))
df["latency_ms"].dropna().hist(bins=60)
plt.title("Latency distribution (ms)")
plt.xlabel("ms")
plt.ylabel("count")
plt.tight_layout()
plt.savefig(os.path.join(OUT,"latency_hist.png"))

plt.figure(figsize=(8,4))
df.groupby("model")["cost_usd"].sum().sort_values(ascending=False).plot(kind="bar")
plt.title("Total cost by model")
plt.ylabel("USD")
plt.tight_layout()
plt.savefig(os.path.join(OUT,"cost_by_model.png"))

plt.figure(figsize=(8,4))
(df[df["status"]=="error"].groupby("model")["request_id"].count()).sort_values(ascending=False).plot(kind="bar")
plt.title("Errors by model")
plt.ylabel("error count")
plt.tight_layout()
plt.savefig(os.path.join(OUT,"errors_by_model.png"))

print("Wrote outputs to", OUT)
