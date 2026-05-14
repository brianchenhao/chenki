import httpx
import pytest
import respx

from chenki import ChenkiClient, Message

ENDPOINT = "https://chenki-llm.hf.space/v1"


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
