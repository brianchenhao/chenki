import sqlite3

from chenki.cache import PromptCache, hash_request


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
