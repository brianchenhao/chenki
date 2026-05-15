from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from chenki.exceptions import ChenkiParseError
from chenki.prompts import RestaurantPrompts

if TYPE_CHECKING:
    from chenki.client import ChenkiClient

_ALLOWED_SPICE = frozenset({"none", "mild", "medium", "hot"})

CLASSIFY_SCHEMA_HINT = (
    '{"cuisine":"<string>","spice_level":"none|mild|medium|hot",'
    '"dietary_tags":["<string>",...]}'
)


@dataclass
class DishClassification:
    cuisine: str
    spice_level: str
    dietary_tags: list[str]

    def __post_init__(self) -> None:
        if self.spice_level not in _ALLOWED_SPICE:
            raise ChenkiParseError(
                f"invalid spice_level: {self.spice_level!r}"
            )


def classify_dish(
    client: ChenkiClient, name: str, description: str
) -> DishClassification:
    """Classify a dish into cuisine, spice level, and dietary tags."""
    messages = RestaurantPrompts.classify(name, description)
    data = client._chat_for_json(messages, CLASSIFY_SCHEMA_HINT)
    return DishClassification(
        cuisine=str(data.get("cuisine", "")),
        spice_level=str(data.get("spice_level", "")),
        dietary_tags=[str(t) for t in data.get("dietary_tags", [])],
    )
