from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from chenki.prompts import RestaurantPrompts

if TYPE_CHECKING:
    from chenki.client import ChenkiClient


ORDER_SCHEMA_HINT = (
    '{"items":[{"name":"<menu name>","quantity":<int>,"notes":"<string>"}],'
    '"notes":"<string>"}'
)


@dataclass
class OrderItem:
    name: str
    quantity: int
    notes: str = ""


@dataclass
class ParsedOrder:
    items: list[OrderItem] = field(default_factory=list)
    notes: str = ""


def parse_order_text(
    client: ChenkiClient, text: str, menu: list[dict[str, Any]]
) -> ParsedOrder:
    """Parse free-form order text into structured items + notes."""
    messages = RestaurantPrompts.order_parse(text, menu)
    data = client._chat_for_json(messages, ORDER_SCHEMA_HINT)
    items = [
        OrderItem(
            name=str(item.get("name", "")),
            quantity=int(item.get("quantity", 0)),
            notes=str(item.get("notes", "")),
        )
        for item in data.get("items", [])
    ]
    return ParsedOrder(items=items, notes=str(data.get("notes", "")))
