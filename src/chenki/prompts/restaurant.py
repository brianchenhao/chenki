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


class RestaurantPrompts:
    """Pre-built restaurant prompts."""

    @staticmethod
    def menu_qa(question: str, menu: list[dict[str, Any]]) -> list[Message]:
        return MenuQAPrompt().render(question=question, menu=menu)
