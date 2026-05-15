import httpx
import pytest
import respx

from chenki import (
    ChenkiClient,
    ChenkiConfig,
    ChenkiRateLimited,
    ChenkiServerError,
    ChenkiTimeout,
    Message,
)

ENDPOINT = "https://brianchenhao-geyam-llm.hf.space/v1"


def _completion_response(content: str = "Hello world!", *, total_tokens: int = 42):
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"total_tokens": total_tokens},
        },
    )


def _fast_config() -> ChenkiConfig:
    return ChenkiConfig(endpoint=ENDPOINT, retry_backoff_base=0.0)


@respx.mock
def test_chat_returns_assistant_text():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response("Hello world!", total_tokens=42)
    )

    client = ChenkiClient(endpoint=ENDPOINT)
    reply = client.chat([Message(role="user", content="Hi")])

    assert reply.text == "Hello world!"
    assert reply.finish_reason == "stop"
    assert reply.tokens_used == 42


@pytest.mark.asyncio
@respx.mock
async def test_achat_returns_assistant_text():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response("Hi from async!", total_tokens=7)
    )

    client = ChenkiClient(endpoint=ENDPOINT)
    reply = await client.achat([Message(role="user", content="Hi")])

    assert reply.text == "Hi from async!"
    assert reply.finish_reason == "stop"
    assert reply.tokens_used == 7


@respx.mock
def test_chat_raises_timeout_on_httpx_timeout():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        side_effect=httpx.ConnectTimeout("connect timeout")
    )
    client = ChenkiClient(config=_fast_config())
    with pytest.raises(ChenkiTimeout):
        client.chat([Message(role="user", content="Hi")])


@respx.mock
def test_chat_raises_server_error_on_500():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=httpx.Response(500, json={"error": "boom"})
    )
    client = ChenkiClient(config=_fast_config())
    with pytest.raises(ChenkiServerError):
        client.chat([Message(role="user", content="Hi")])


@respx.mock
def test_chat_raises_rate_limited_on_429():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=httpx.Response(429, json={"error": "slow down"})
    )
    client = ChenkiClient(config=_fast_config())
    with pytest.raises(ChenkiRateLimited):
        client.chat([Message(role="user", content="Hi")])


@pytest.mark.asyncio
@respx.mock
async def test_achat_raises_timeout_on_httpx_timeout():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        side_effect=httpx.ReadTimeout("read timeout")
    )
    client = ChenkiClient(config=_fast_config())
    with pytest.raises(ChenkiTimeout):
        await client.achat([Message(role="user", content="Hi")])


@respx.mock
def test_chat_retries_once_on_500_then_succeeds():
    route = respx.post(f"{ENDPOINT}/chat/completions").mock(
        side_effect=[
            httpx.Response(500, json={"error": "boom"}),
            _completion_response("recovered", total_tokens=3),
        ]
    )

    client = ChenkiClient(config=_fast_config())
    reply = client.chat([Message(role="user", content="Hi")])

    assert reply.text == "recovered"
    assert route.call_count == 2


@respx.mock
def test_chat_gives_up_after_max_retries():
    route = respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=httpx.Response(500, json={"error": "boom"})
    )

    client = ChenkiClient(config=_fast_config())
    with pytest.raises(ChenkiServerError):
        client.chat([Message(role="user", content="Hi")])

    assert route.call_count == 2  # initial attempt + 1 retry


@pytest.mark.asyncio
@respx.mock
async def test_achat_retries_once_on_500_then_succeeds():
    route = respx.post(f"{ENDPOINT}/chat/completions").mock(
        side_effect=[
            httpx.Response(500, json={"error": "boom"}),
            _completion_response("recovered-async", total_tokens=4),
        ]
    )

    client = ChenkiClient(config=_fast_config())
    reply = await client.achat([Message(role="user", content="Hi")])

    assert reply.text == "recovered-async"
    assert route.call_count == 2


@respx.mock
def test_chat_stream_yields_content_deltas():
    sse_body = (
        'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n'
        'data: {"choices":[{"delta":{"content":" world"}}]}\n\n'
        "data: [DONE]\n\n"
    )
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=httpx.Response(
            200,
            content=sse_body.encode("utf-8"),
            headers={"content-type": "text/event-stream"},
        )
    )

    client = ChenkiClient(endpoint=ENDPOINT)
    chunks = list(client.chat_stream([Message(role="user", content="Hi")]))

    assert chunks == ["Hello", " world"]


@respx.mock
def test_chat_stream_raises_server_error_on_500():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=httpx.Response(500, json={"error": "boom"})
    )

    client = ChenkiClient(endpoint=ENDPOINT)
    with pytest.raises(ChenkiServerError):
        list(client.chat_stream([Message(role="user", content="Hi")]))
