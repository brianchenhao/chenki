from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class ChatCompletion:
    text: str
    finish_reason: str | None = None
    tokens_used: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)
