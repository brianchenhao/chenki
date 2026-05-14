from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Iterable, Iterator

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
        payload = self._build_payload(messages, model, temperature)
        url = self._completions_url()
        for attempt in range(self.config.max_retries + 1):
            try:
                return _sync_request(url, payload, self.config.timeout)
            except ChenkiServerError:
                if attempt >= self.config.max_retries:
                    raise
                time.sleep(_retry_delay(attempt, self.config.retry_backoff_base))
        raise RuntimeError("retry loop exited without return")

    async def achat(
        self,
        messages: Iterable[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> ChatCompletion:
        payload = self._build_payload(messages, model, temperature)
        url = self._completions_url()
        for attempt in range(self.config.max_retries + 1):
            try:
                return await _async_request(url, payload, self.config.timeout)
            except ChenkiServerError:
                if attempt >= self.config.max_retries:
                    raise
                await asyncio.sleep(
                    _retry_delay(attempt, self.config.retry_backoff_base)
                )
        raise RuntimeError("retry loop exited without return")

    def chat_stream(
        self,
        messages: Iterable[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        payload = self._build_payload(messages, model, temperature, stream=True)
        return _sync_stream(self._completions_url(), payload, self.config.timeout)

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


def _sync_request(url: str, payload: dict[str, Any], timeout: float) -> ChatCompletion:
    try:
        response = httpx.post(url, json=payload, timeout=timeout)
    except httpx.TimeoutException as exc:
        raise ChenkiTimeout(str(exc)) from exc
    _raise_for_status(response)
    return _parse_chat_completion(response.json())


async def _async_request(
    url: str, payload: dict[str, Any], timeout: float
) -> ChatCompletion:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
    except httpx.TimeoutException as exc:
        raise ChenkiTimeout(str(exc)) from exc
    _raise_for_status(response)
    return _parse_chat_completion(response.json())


def _sync_stream(
    url: str, payload: dict[str, Any], timeout: float
) -> Iterator[str]:
    try:
        with httpx.stream("POST", url, json=payload, timeout=timeout) as response:
            if response.status_code >= 400:
                response.read()
                _raise_for_status(response)
            for line in response.iter_lines():
                delta = _parse_sse_content(line)
                if delta is _SSE_DONE:
                    return
                if delta:
                    yield delta
    except httpx.TimeoutException as exc:
        raise ChenkiTimeout(str(exc)) from exc


_SSE_DONE = object()


def _parse_sse_content(line: str) -> Any:
    if not line or not line.startswith("data: "):
        return None
    data = line[6:].strip()
    if data == "[DONE]":
        return _SSE_DONE
    try:
        chunk = json.loads(data)
    except json.JSONDecodeError:
        return None
    choices = chunk.get("choices") or [{}]
    return choices[0].get("delta", {}).get("content")


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


def _retry_delay(attempt: int, base: float) -> float:
    return base * (2 ** attempt)


def _parse_chat_completion(body: dict[str, Any]) -> ChatCompletion:
    choice = body["choices"][0]
    usage = body.get("usage") or {}
    return ChatCompletion(
        text=choice["message"]["content"],
        finish_reason=choice.get("finish_reason"),
        tokens_used=usage.get("total_tokens"),
        raw=body,
    )
