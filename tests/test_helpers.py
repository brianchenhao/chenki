import httpx
import pytest
import respx

from chenki import (
    ChenkiClient,
    ChenkiParseError,
    DishClassification,
    OrderItem,
    ParsedOrder,
)

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


@respx.mock
def test_classify_dish_retries_on_invalid_json():
    route = respx.post(f"{ENDPOINT}/chat/completions").mock(
        side_effect=[
            _completion_response("Sure! Here is the classification: rice."),
            _completion_response(
                '{"cuisine":"Italian","spice_level":"none","dietary_tags":["vegetarian"]}'
            ),
        ]
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    result = client.classify_dish("Margherita", "cheese and tomato")
    assert result == DishClassification(
        cuisine="Italian",
        spice_level="none",
        dietary_tags=["vegetarian"],
    )
    assert route.call_count == 2


@respx.mock
def test_classify_dish_raises_after_failed_retry():
    route = respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response("nothing structured here at all")
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    with pytest.raises(ChenkiParseError):
        client.classify_dish("Margherita", "cheese and tomato")
    assert route.call_count == 2  # initial + retry


@respx.mock
def test_classify_dish_extracts_json_from_markdown_fence():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response(
            "Here you go:\n```json\n"
            '{"cuisine":"Thai","spice_level":"hot",'
            '"dietary_tags":["contains_peanut"]}\n'
            "```\nAnything else?"
        )
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    result = client.classify_dish("Pad Thai", "noodles with peanut sauce")
    assert result == DishClassification(
        cuisine="Thai",
        spice_level="hot",
        dietary_tags=["contains_peanut"],
    )
