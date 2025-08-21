import time
import math
import json
import requests
import config

HF_TOKEN = config.HF_TOKEN
API_URL = config.API_URL
HEADERS = config.HEADERS

def mean_pool_token_embeddings(token_matrix):
    # token_matrix: list[list[float]] with shape [num_tokens, hidden_size]
    if not token_matrix:
        return []
    dim = len(token_matrix[0])
    sums = [0.0] * dim
    for tok in token_matrix:
        for i, v in enumerate(tok):
            sums[i] += float(v)
    n = float(len(token_matrix))
    return [s / n for s in sums]

def l2_normalize(vec):
    norm = math.sqrt(sum(x*x for x in vec))
    return [x / norm for x in vec] if norm > 0 else vec

def get_embedding(text, retries=5, backoff=2.0):
    payload = {
        "inputs": [text],           # list or string both ok; list => batch of size 1
        "normalize": True,          # let HF normalize if supported
        # "truncate": True,         # optional
        # "prompt_name": "query",   # optional if the model defines prompts; not needed here
    }
    for attempt in range(1, retries + 1):
        r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        if r.status_code == 200:
            data = r.json()
            # Two possibilities:
            # (A) Already pooled: [[384 floats]]
            # (B) Token features: [[[...token1 384...], [...token2 384...], ...]]
            if isinstance(data, list) and data and isinstance(data[0], list):
                first = data[0]
                # Case A: vector already length 384
                if first and isinstance(first[0], (int, float)) and len(first) == 384:
                    vec = first
                # Case B: token-level -> mean pool then L2 normalize
                elif first and isinstance(first[0], list):
                    vec = mean_pool_token_embeddings(first)
                    vec = l2_normalize(vec)
                else:
                    raise RuntimeError(f"Unexpected response shape: {type(first)}")
                return vec

            raise RuntimeError(f"Unexpected response type: {type(data)}; body={data!r}")

        # Handle “model is loading”/queue or other transient issues
        try:
            err = r.json()
        except Exception:
            err = {"error": r.text}

        if r.status_code in (503, 529) or ("loading" in str(err).lower()):
            if attempt < retries:
                time.sleep(backoff ** (attempt - 1))
                continue

        # For any other error, raise with context
        raise RuntimeError(
            f"HF API error (status {r.status_code}): {json.dumps(err, ensure_ascii=False)}"
        )
