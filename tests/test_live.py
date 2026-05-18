"""Smoke tests against the real chenki-llm HF Space.

Skipped by default. Run with: `pytest --live`. CI runs these on tag pushes only.
"""
import pytest

from chenki import ChenkiClient, DishClassification, Message

pytestmark = pytest.mark.live


def test_chat_returns_nonempty_string():
    client = ChenkiClient()
    reply = client.chat(
        [Message(role="user", content="Reply with exactly the word: ok")],
        temperature=0.1,
    )
    assert isinstance(reply.text, str)
    assert reply.text.strip()


def test_classify_dish_returns_valid_dataclass():
    client = ChenkiClient()
    result = client.classify_dish(
        "Margherita Pizza", "tomato sauce, mozzarella, basil"
    )
    assert isinstance(result, DishClassification)
    assert isinstance(result.cuisine, str) and result.cuisine
    assert result.spice_level in {"none", "mild", "medium", "hot"}
    assert isinstance(result.dietary_tags, list)


def test_ask_about_menu_grounded_in_input():
    client = ChenkiClient()
    menu = [
        {"name": "Nasi Lemak", "description": "rice with sambal and anchovies"},
        {"name": "Roti Canai", "description": "flaky bread with curry"},
    ]
    answer = client.ask_about_menu("anything with rice?", menu)
    assert isinstance(answer, str)
    assert answer.strip()
