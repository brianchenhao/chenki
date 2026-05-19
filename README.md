# chenki

[![Tests](https://github.com/brianchenhao/chenki/actions/workflows/test.yml/badge.svg)](https://github.com/brianchenhao/chenki/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/brianchenhao/chenki/graph/badge.svg)](https://codecov.io/gh/brianchenhao/chenki)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/chenki)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Self-hostable LLM client for restaurant tech. A thin Python library that talks to any OpenAI-compatible `/v1/chat/completions` endpoint, with restaurant-domain helpers (menu Q&A, dish classification, order parsing) built on top.

By default it points at **brianchenhao-chenki-llm.hf.space** — a free Hugging Face Space running Qwen 2.5 1.5B Instruct (Q4_K_M) behind `llama.cpp`. Self-hosters can deploy their own Space using the included `server/Dockerfile`.

## Status

`chenki` is under active development. `v0.0.1` reserves the PyPI name; `v0.1.0` is the first functional release.

## Install

```bash
pip install chenki
```

## Quickstart

```python
from chenki import ChenkiClient, Message

client = ChenkiClient()  # defaults to https://brianchenhao-chenki-llm.hf.space/v1
reply = client.chat([Message(role="user", content="Hello!")])
print(reply.text)
```

## Website

[chenki.com](https://chenki.com) (coming soon)

## License

MIT
