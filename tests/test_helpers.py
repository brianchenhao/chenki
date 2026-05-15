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

ENDPOINT = "https://brianchenhao-geyam-llm.hf.space/v1"


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


def test_dish_classification_rejects_invalid_spice_level():
    with pytest.raises(ChenkiParseError):
        DishClassification(
            cuisine="Italian", spice_level="extreme", dietary_tags=[]
        )


@respx.mock
def test_classify_dish_raises_on_invalid_spice_level_from_llm():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response(
            '{"cuisine":"Italian","spice_level":"extreme","dietary_tags":[]}'
        )
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    with pytest.raises(ChenkiParseError):
        client.classify_dish("Margherita", "cheese")


@respx.mock
def test_parse_order_text_handles_multiple_items():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response(
            '{"items":['
            '{"name":"Pad Thai","quantity":2,"notes":""},'
            '{"name":"Green Curry","quantity":1,"notes":"mild"},'
            '{"name":"Spring Rolls","quantity":3,"notes":""}'
            '],"notes":""}'
        )
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    order = client.parse_order_text("a big order", menu=[])
    assert len(order.items) == 3
    assert order.items[0] == OrderItem(name="Pad Thai", quantity=2, notes="")
    assert order.items[1] == OrderItem(name="Green Curry", quantity=1, notes="mild")
    assert order.items[2] == OrderItem(name="Spring Rolls", quantity=3, notes="")


@respx.mock
def test_parse_order_text_handles_empty_items():
    respx.post(f"{ENDPOINT}/chat/completions").mock(
        return_value=_completion_response(
            '{"items":[],"notes":"customer browsing"}'
        )
    )
    client = ChenkiClient(endpoint=ENDPOINT)
    order = client.parse_order_text("just looking", menu=[])
    assert order == ParsedOrder(items=[], notes="customer browsing")
