# Quickstart

Five minutes from `pip install` to your first response.

## 1. Install

```bash
pip install chenki
```

Optional extras:

```bash
pip install "chenki[test]"   # pytest + respx + pytest-cov for development
pip install "chenki[docs]"   # mkdocs + material theme for building these docs
```

Chenki has exactly **one runtime dependency**: [`httpx`](https://www.python-httpx.org). Everything else is stdlib.

## 2. Send a chat completion

```python
from chenki import ChenkiClient, Message

client = ChenkiClient()
reply = client.chat([Message(role="user", content="Say hi in one sentence.")])
print(reply.text)
```

The first call wakes the default Space (a cold start adds ~30 s); subsequent calls usually return in 5–15 s on Qwen 2.5 1.5B Q4_K_M.

## 3. Stream tokens as they arrive

```python
for chunk in client.chat_stream(
    [Message(role="user", content="Count from 1 to 5, one per line.")]
):
    print(chunk, end="", flush=True)
print()
```

`chat_stream` yields content deltas from the server-sent-events feed, ending automatically on the `[DONE]` sentinel.

## 4. Use the async client

```python
import asyncio
from chenki import ChenkiClient, Message

async def main():
    client = ChenkiClient()
    reply = await client.achat([Message(role="user", content="Hello async!")])
    print(reply.text)

asyncio.run(main())
```

`achat` mirrors `chat` exactly but uses `httpx.AsyncClient`. Use it inside FastAPI route handlers, async background jobs, anywhere you don't want to block the event loop.

## 5. Restaurant helper: menu Q&A

```python
menu = [
    {"name": "Nasi Lemak", "description": "rice with sambal and anchovies"},
    {"name": "Roti Canai",  "description": "flaky bread with curry dip"},
    {"name": "Teh Tarik",   "description": "pulled milk tea"},
]
answer = client.ask_about_menu("Anything with rice?", menu)
print(answer)
```

See [Restaurant helpers](helpers.md) for `classify_dish` and `parse_order_text`.

## 6. Point at a different endpoint

```python
from chenki import ChenkiClient, ChenkiConfig

client = ChenkiClient(
    config=ChenkiConfig(
        endpoint="https://my-self-hosted-llm.example.com/v1",
        timeout=30.0,
        max_retries=1,
    )
)
```

Any OpenAI-compatible `/v1/chat/completions` server works — local Ollama, vLLM, llama.cpp's `llama-server`, LM Studio, OpenAI itself.

See [Configuration](configuration.md) for the full list of knobs.
