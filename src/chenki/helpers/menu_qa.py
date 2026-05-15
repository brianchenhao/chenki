from __future__ import annotations

from typing import TYPE_CHECKING, Any

from chenki.prompts import RestaurantPrompts

if TYPE_CHECKING:
    from chenki.client import ChenkiClient


def ask_about_menu(
    client: ChenkiClient, question: str, menu: list[dict[str, Any]]
) -> str:
    """Ask a free-form question about a restaurant menu."""
    messages = RestaurantPrompts.menu_qa(question, menu)
    return client.chat(messages).text
