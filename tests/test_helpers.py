import httpx
import respx

from chenki import ChenkiClient

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


@respx.mock
def test_ask_about_menu_returns_assistant_text():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response("Try the spicy curry.")
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    answer = client.ask_about_menu(
        "Anything spicy?",
        menu=[{"name": "Curry", "description": "spicy"}],
    )
    assert answer == "Try the spicy curry."
