import httpx
import respx

from chenki import ChenkiClient, DishClassification, OrderItem, ParsedOrder

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


@respx.mock
def test_classify_dish_returns_dataclass():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response(
            '{"cuisine":"Malay","spice_level":"medium",'
            '"dietary_tags":["contains_egg"]}'
        )
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    result = client.classify_dish("Nasi Lemak", "rice with sambal")
    assert result == DishClassification(
        cuisine="Malay",
        spice_level="medium",
        dietary_tags=["contains_egg"],
    )


@respx.mock
def test_parse_order_text_returns_dataclass():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response(
            '{"items":[{"name":"Pad Thai","quantity":2,"notes":"no peanuts"}],'
            '"notes":"dine-in"}'
        )
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    order = client.parse_order_text(
        "Two pad thai, no peanuts. Dine-in.", menu=[]
    )
    assert order == ParsedOrder(
        items=[OrderItem(name="Pad Thai", quantity=2, notes="no peanuts")],
        notes="dine-in",
    )
