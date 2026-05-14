import httpx
import respx

from chenki import ChenkiClient, Message


@respx.mock
def test_chat_returns_assistant_text():
    endpoint = "https://chenki-llm.hf.space/v1"
    respx.post(f"{endpoint}/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Hello world!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"total_tokens": 42},
            },
        )
    )

    client = ChenkiClient(endpoint=endpoint)
    reply = client.chat([Message(role="user", content="Hi")])

    assert reply.text == "Hello world!"
    assert reply.finish_reason == "stop"
    assert reply.tokens_used == 42
