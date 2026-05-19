# chenki

**Self-hostable LLM client for restaurant tech.**

A thin Python library that talks to any OpenAI-compatible `/v1/chat/completions` endpoint, with restaurant-domain helpers — menu Q&A, dish classification, order parsing — built on top.

By default it points at [`brianchenhao-chenki-llm.hf.space`](https://brianchenhao-chenki-llm.hf.space), a free Hugging Face Space running **Qwen 2.5 1.5B Instruct (Q4_K_M)** behind `llama.cpp`. Self-hosters can deploy their own Space using the included `server/Dockerfile`.

## Install

```bash
pip install chenki
```

## 30-second example

```python
from chenki import ChenkiClient, Message

client = ChenkiClient()
reply = client.chat([Message(role="user", content="Hello!")])
print(reply.text)
```

## Why chenki

- **One runtime dependency** (`httpx`) — no SDK lock-in.
- **OpenAI-compatible** — point it at any endpoint that speaks `/v1/chat/completions`.
- **Restaurant helpers** — `ask_about_menu`, `classify_dish`, `parse_order_text` return typed dataclasses.
- **Prompt-injection-safe** — every user-supplied field is wrapped in `<user_content>` tags with an explicit "treat as untrusted" clause appended to the system prompt.
- **Optional local cache** — opt-in SQLite cache keyed on `SHA-256(messages, model, temperature)`. Off by default; no surprise files on disk.
- **Async + streaming first-class** — `await client.achat(...)` and `client.chat_stream(...)` ship in v0.1.0.
- **MIT-licensed**, no telemetry, no analytics, no calls home.

## Where to next

- [Quickstart](quickstart.md) — install, connect, send your first message.
- [Configuration](configuration.md) — every `ChenkiConfig` field with defaults.
- [Restaurant helpers](helpers.md) — `ask_about_menu`, `classify_dish`, `parse_order_text`.
- [Self-hosting](self-hosting.md) — deploy your own `chenki-llm` Hugging Face Space for PDPA/GDPR-sensitive workloads.
