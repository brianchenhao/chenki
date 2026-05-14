from __future__ import annotations

from typing import Any, Iterable

import httpx

from chenki.config import ChenkiConfig
from chenki.messages import ChatCompletion, Message


class ChenkiClient:
    """Synchronous client for an OpenAI-compatible chat completions endpoint."""

    def __init__(
        self,
        endpoint: str | None = None,
        *,
        config: ChenkiConfig | None = None,
    ) -> None:
        self.config = config or ChenkiConfig()
        if endpoint is not None:
            self.config.endpoint = endpoint

    def chat(
        self,
        messages: Iterable[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> ChatCompletion:
        url = f"{self.config.endpoint.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": model or self.config.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": (
                temperature if temperature is not None else self.config.temperature
            ),
            "stream": False,
        }
        response = httpx.post(url, json=payload, timeout=self.config.timeout)
        response.raise_for_status()
        return _parse_chat_completion(response.json())


def _parse_chat_completion(body: dict[str, Any]) -> ChatCompletion:
    choice = body["choices"][0]
    usage = body.get("usage") or {}
    return ChatCompletion(
        text=choice["message"]["content"],
        finish_reason=choice.get("finish_reason"),
        tokens_used=usage.get("total_tokens"),
        raw=body,
    )
