import sqlite3

import httpx
import pytest
import respx

from chenki import ChenkiClient, ChenkiConfig, Message
from chenki.cache import PromptCache, hash_request

ENDPOINT = "https://chenki-llm.hf.space/v1"


def _completion_response(content: str):
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"total_tokens": 1},
        },
    )


def test_promptcache_creates_db_file(tmp_path):
    path = tmp_path / "cache.db"
    PromptCache(path=path)
    assert path.exists()


def test_promptcache_uses_wal_journal_mode(tmp_path):
    path = tmp_path / "cache.db"
    PromptCache(path=path)
    conn = sqlite3.connect(path)
    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    conn.close()
    assert mode == "wal"


def test_promptcache_set_then_get_returns_value(tmp_path):
    cache = PromptCache(path=tmp_path / "cache.db")
    cache.set("key1", "response one")
    assert cache.get("key1") == "response one"


def test_promptcache_get_returns_none_for_missing_key(tmp_path):
    cache = PromptCache(path=tmp_path / "cache.db")
    assert cache.get("nonexistent") is None


def test_promptcache_set_overwrites_existing_value(tmp_path):
    cache = PromptCache(path=tmp_path / "cache.db")
    cache.set("key1", "first")
    cache.set("key1", "second")
    assert cache.get("key1") == "second"


_MESSAGES_A = [{"role": "user", "content": "hello"}]
_MESSAGES_B = [{"role": "user", "content": "goodbye"}]


def test_hash_request_is_deterministic():
    h1 = hash_request(_MESSAGES_A, "qwen2.5", 0.7)
    h2 = hash_request(_MESSAGES_A, "qwen2.5", 0.7)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex digest


def test_hash_request_differs_on_messages():
    h1 = hash_request(_MESSAGES_A, "qwen2.5", 0.7)
    h2 = hash_request(_MESSAGES_B, "qwen2.5", 0.7)
    assert h1 != h2


def test_hash_request_differs_on_model():
    h1 = hash_request(_MESSAGES_A, "qwen2.5", 0.7)
    h2 = hash_request(_MESSAGES_A, "llama3", 0.7)
    assert h1 != h2


def test_hash_request_differs_on_temperature():
    h1 = hash_request(_MESSAGES_A, "qwen2.5", 0.7)
    h2 = hash_request(_MESSAGES_A, "qwen2.5", 0.1)
    assert h1 != h2


@respx.mock
def test_chat_hits_cache_on_second_call(tmp_path):
    route = respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response("cached response")
    )
    config = ChenkiConfig(
        endpoint=ENDPOINT,
        cache_enabled=True,
        cache_path=str(tmp_path / "cache.db"),
    )
    client = ChenkiClient(config=config)

    first = client.chat([Message(role="user", content="Hello")])
    second = client.chat([Message(role="user", content="Hello")])

    assert first.text == "cached response"
    assert second.text == "cached response"
    assert route.call_count == 1


@respx.mock
def test_chat_miss_writes_to_cache(tmp_path):
    cache_path = tmp_path / "cache.db"
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response("first response")
    )
    config = ChenkiConfig(
        endpoint=ENDPOINT,
        cache_enabled=True,
        cache_path=str(cache_path),
    )
    client = ChenkiClient(config=config)

    client.chat([Message(role="user", content="Hi")])

    conn = sqlite3.connect(cache_path)
    count = conn.execute("SELECT COUNT(*) FROM prompt_cache").fetchone()[0]
    conn.close()
    assert count == 1


@pytest.mark.asyncio
@respx.mock
async def test_achat_hits_cache_on_second_call(tmp_path):
    route = respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response("async cached")
    )
    config = ChenkiConfig(
        endpoint=ENDPOINT,
        cache_enabled=True,
        cache_path=str(tmp_path / "cache.db"),
    )
    client = ChenkiClient(config=config)

    first = await client.achat([Message(role="user", content="Async hi")])
    second = await client.achat([Message(role="user", content="Async hi")])

    assert first.text == "async cached"
    assert second.text == "async cached"
    assert route.call_count == 1
