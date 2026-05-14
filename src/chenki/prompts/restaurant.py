from __future__ import annotations

from typing import Any

from chenki.messages import Message
from chenki.prompts.base import PromptTemplate


class MenuQAPrompt(PromptTemplate):
    """Answer a question about a restaurant menu."""

    def build_messages(
        self, *, question: str, menu: list[dict[str, Any]]
    ) -> list[Message]:
        return [
            Message(
                role="system",
                content=(
                    "You are a restaurant assistant. Here is the menu (JSON):\n"
                    f"{self._wrap_json(menu)}\n\n"
                    "Answer using only items from the menu above. "
                    "If the menu does not cover the question, say so briefly."
                ),
            ),
            Message(role="user", content=self._wrap(question)),
        ]


class ClassifyDishPrompt(PromptTemplate):
    """Classify a dish into cuisine/spice/dietary tags as strict JSON."""

    def build_messages(self, *, name: str, description: str) -> list[Message]:
        return [
            Message(
                role="system",
                content=(
                    "Classify the dish. Respond with JSON only matching:\n"
                    '{"cuisine":"<string>",'
                    '"spice_level":"none|mild|medium|hot",'
                    '"dietary_tags":["<string>",...]}\n'
                    'Example: {"cuisine":"Italian","spice_level":"none",'
                    '"dietary_tags":["vegetarian"]}\n'
                    "No prose, no markdown fences."
                ),
            ),
            Message(
                role="user",
                content=(
                    f"Name: {self._wrap(name)}\n"
                    f"Description: {self._wrap(description)}"
                ),
            ),
        ]


class RestaurantPrompts:
    """Pre-built restaurant prompts."""

    @staticmethod
    def menu_qa(question: str, menu: list[dict[str, Any]]) -> list[Message]:
        return MenuQAPrompt().render(question=question, menu=menu)

    @staticmethod
    def classify(name: str, description: str) -> list[Message]:
        return ClassifyDishPrompt().render(name=name, description=description)
