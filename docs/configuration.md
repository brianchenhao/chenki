# Configuration

Every knob lives on `ChenkiConfig`. Defaults are tuned for the public `brianchenhao-chenki-llm.hf.space` Space.

## ChenkiConfig

```python
from chenki import ChenkiClient, ChenkiConfig

config = ChenkiConfig(
    endpoint="https://brianchenhao-chenki-llm.hf.space/v1",
    model="qwen2.5-1.5b-instruct",
    timeout=60.0,
    temperature=0.7,
    max_retries=1,
    retry_backoff_base=0.5,
    cache_enabled=False,
    cache_path="chenki_cache.db",
)
client = ChenkiClient(config=config)
```

### Fields

| Field | Type | Default | What it controls |
|---|---|---|---|
| `endpoint` | `str` | `"https://brianchenhao-chenki-llm.hf.space/v1"` | Base URL of any OpenAI-compatible server. Chenki POSTs to `{endpoint}/chat/completions`. |
| `model` | `str` | `"qwen2.5-1.5b-instruct"` | Model name sent in the request payload. The server may ignore it (llama-server reports `model.gguf` regardless). |
| `timeout` | `float` | `60.0` | Total per-request timeout in seconds. Triggers `ChenkiTimeout` on expiry. |
| `temperature` | `float` | `0.7` | Sampling temperature. Override per-call with `client.chat(messages, temperature=0.1)`. |
| `max_retries` | `int` | `1` | Retries on 5xx responses. `0` disables retries. 429 (rate-limited) is never retried — it raises `ChenkiRateLimited` immediately. |
| `retry_backoff_base` | `float` | `0.5` | Seconds before the first retry; doubles on each subsequent attempt (`0.5s`, `1s`, `2s`, ...). |
| `cache_enabled` | `bool` | `False` | Turn on the local SQLite prompt cache. **Off by default** — no `chenki_cache.db` is created unless you opt in. |
| `cache_path` | `str` | `"chenki_cache.db"` | Where to store the cache SQLite file. Relative paths resolve against the process's working directory. |

## Per-call overrides

`chat`, `achat`, and `chat_stream` accept `model=` and `temperature=` kwargs that override the config for that call only:

```python
client.chat(messages, model="llama3.2:3b", temperature=0.1)
```

This is useful for structured-output tasks where you want low temperature for the JSON-shaped helpers and higher temperature for free-form chat.

## Caching

The optional prompt cache stores `(SHA-256(messages, model, temperature), response_text)` pairs in a local SQLite database. To turn it on:

```python
client = ChenkiClient(
    config=ChenkiConfig(cache_enabled=True, cache_path="my_cache.db")
)
```

Behavior:

- The first identical call hits the network and writes to the cache.
- Subsequent identical calls return from disk in under 5 ms.
- Every cache hit bumps `hit_count` and updates `last_hit_at` on that row.
- WAL journal mode is set automatically — multiple readers don't block each other.

Schema details live in the [chenki-cache module](https://github.com/brianchenhao/chenki/blob/main/src/chenki/cache.py).

## Environment variables

Chenki does **not** read any environment variables itself — every knob is passed explicitly through `ChenkiConfig`. If you want env-driven config in your app, the standard pattern is:

```python
import os
from chenki import ChenkiClient, ChenkiConfig

client = ChenkiClient(
    config=ChenkiConfig(
        endpoint=os.environ.get("CHENKI_ENDPOINT", ChenkiConfig().endpoint),
        timeout=float(os.environ.get("CHENKI_TIMEOUT", "60")),
    )
)
```

This keeps configuration explicit in tests and avoids surprises when env vars leak across processes.

## Exceptions

| Exception | When it raises |
|---|---|
| `ChenkiTimeout` | The request didn't complete before `timeout` seconds. |
| `ChenkiServerError` | The server returned a 5xx after `max_retries` attempts. |
| `ChenkiRateLimited` | The server returned 429. Never retried. |
| `ChenkiParseError` | A structured-output helper couldn't parse JSON even after one retry with a stricter prompt. The original raw response is on `.raw`. |
| `ChenkiError` | Base class — catch this if you want a single `except` clause for any chenki-specific failure. |
