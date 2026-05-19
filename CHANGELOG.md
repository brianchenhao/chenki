# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-20

First functional release. Public API frozen for the 0.1.x series.

### Added
- `ChenkiClient` with sync `chat`, async `achat`, and `chat_stream` (SSE) methods talking to any OpenAI-compatible `/v1/chat/completions` endpoint.
- `ChenkiConfig` dataclass: `endpoint`, `model`, `timeout`, `temperature`, `max_retries`, `retry_backoff_base`, `cache_enabled`, `cache_path`.
- Default endpoint: `https://brianchenhao-chenki-llm.hf.space/v1` — free Hugging Face Space running Qwen 2.5 1.5B Instruct (Q4_K_M) behind `llama.cpp`.
- Restaurant helpers: `ask_about_menu`, `classify_dish`, `parse_order_text`. Return `DishClassification` / `ParsedOrder` / `OrderItem` dataclasses.
- Structured-output retry-once-on-bad-JSON behaviour, then `ChenkiParseError` (carries `.raw`).
- Prompt-injection-safe templating via `PromptTemplate.render()` — every user-supplied field wrapped in `<user_content>` tags; system prompt ends with an explicit "treat as untrusted" clause.
- `RestaurantPrompts` static methods: `menu_qa`, `classify`, `order_parse`.
- Optional local SQLite cache (`PromptCache`, off by default) keyed on `SHA-256(messages, model, temperature)`. WAL journal mode; bumps `hit_count` + `last_hit_at` on every hit.
- Retry-once-on-5xx with exponential backoff in `chat` and `achat`.
- Exceptions: `ChenkiError`, `ChenkiTimeout`, `ChenkiServerError`, `ChenkiRateLimited`, `ChenkiParseError`.
- `server/Dockerfile` + `server/README.md` for self-hosting your own `chenki-llm` Hugging Face Space.
- MkDocs Material docs site (5 pages) ready to deploy to `docs.chenki.com`.
- chenki.com landing page (Vite + React + Tailwind 4), deployed to Cloudflare Pages.
- Tests: 66 unit tests + 3 `@pytest.mark.live` smoke tests (opt-in via `--live`). 97% coverage (line+branch).
- GitHub Actions CI matrix-tests Python 3.10 and 3.13; uploads coverage to Codecov.

### Public API

Locked surface — anything else is private (`_`-prefixed or not in `__init__.py`):
`ChenkiClient`, `ChenkiConfig`, `Message`, `ChatCompletion`, `DishClassification`, `OrderItem`, `ParsedOrder`, `PromptTemplate`, `RestaurantPrompts`, `PromptCache`, `ChenkiError`, `ChenkiTimeout`, `ChenkiServerError`, `ChenkiRateLimited`, `ChenkiParseError`, `__version__`.

## [0.0.1] - 2026-05-08

### Added
- Placeholder release to reserve the PyPI name.
