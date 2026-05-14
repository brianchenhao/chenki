from __future__ import annotations

from typing import Any, Iterable

import httpx

from chenki.config import ChenkiConfig
from chenki.exceptions import ChenkiRateLimited, ChenkiServerError, ChenkiTimeout
from chenki.messages import ChatCompletion, Message


class ChenkiClient:
    """Client for an OpenAI-compatible chat completions endpoint."""

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
        try:
            response = httpx.post(
                self._completions_url(),
                json=self._build_payload(messages, model, temperature),
                timeout=self.config.timeout,
            )
        except httpx.TimeoutException as exc:
            raise ChenkiTimeout(str(exc)) from exc
        _raise_for_status(response)
        return _parse_chat_completion(response.json())

    async def achat(
        self,
        messages: Iterable[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> ChatCompletion:
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    self._completions_url(),
                    json=self._build_payload(messages, model, temperature),
                )
        except httpx.TimeoutException as exc:
            raise ChenkiTimeout(str(exc)) from exc
        _raise_for_status(response)
        return _parse_chat_completion(response.json())

    def _completions_url(self) -> str:
        return f"{self.config.endpoint.rstrip('/')}/chat/completions"

    def _build_payload(
        self,
        messages: Iterable[Message],
        model: str | None,
        temperature: float | None,
        *,
        stream: bool = False,
    ) -> dict[str, Any]:
        return {
            "model": model or self.config.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": (
                temperature if temperature is not None else self.config.temperature
            ),
            "stream": stream,
        }


def _raise_for_status(response: httpx.Response) -> None:
    status = response.status_code
    if 200 <= status < 300:
        return
    if status == 429:
        raise ChenkiRateLimited(f"chenki-llm returned 429: rate limited")
    if 500 <= status < 600:
        raise ChenkiServerError(
            f"chenki-llm returned {status}: {response.text[:200]}"
        )
    response.raise_for_status()


def _parse_chat_completion(body: dict[str, Any]) -> ChatCompletion:
    choice = body["choices"][0]
    usage = body.get("usage") or {}
    return ChatCompletion(
        text=choice["message"]["content"],
        finish_reason=choice.get("finish_reason"),
        tokens_used=usage.get("total_tokens"),
        raw=body,
    )
