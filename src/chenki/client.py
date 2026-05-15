from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Any, Iterable, Iterator

import httpx

from chenki.config import ChenkiConfig
from chenki.exceptions import (
    ChenkiParseError,
    ChenkiRateLimited,
    ChenkiServerError,
    ChenkiTimeout,
)
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
        self._cache: Any = None
        if self.config.cache_enabled:
            from chenki.cache import PromptCache

            self._cache = PromptCache(path=self.config.cache_path)

    def chat(
        self,
        messages: Iterable[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> ChatCompletion:
        payload = self._build_payload(messages, model, temperature)
        cache_key = self._cache_key(payload)
        cached = self._cache_lookup(cache_key)
        if cached is not None:
            return cached
        url = self._completions_url()
        for attempt in range(self.config.max_retries + 1):
            try:
                completion = _sync_request(url, payload, self.config.timeout)
                self._cache_store(cache_key, completion)
                return completion
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
        cache_key = self._cache_key(payload)
        cached = self._cache_lookup(cache_key)
        if cached is not None:
            return cached
        url = self._completions_url()
        for attempt in range(self.config.max_retries + 1):
            try:
                completion = await _async_request(url, payload, self.config.timeout)
                self._cache_store(cache_key, completion)
                return completion
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

    def ask_about_menu(self, question: str, menu: list[dict[str, Any]]) -> str:
        from chenki.helpers.menu_qa import ask_about_menu

        return ask_about_menu(self, question, menu)

    def classify_dish(self, name: str, description: str):
        from chenki.helpers.classify import classify_dish

        return classify_dish(self, name, description)

    def parse_order_text(self, text: str, menu: list[dict[str, Any]]):
        from chenki.helpers.order_parse import parse_order_text

        return parse_order_text(self, text, menu)

    def _chat_for_json(
        self,
        messages: list[Message],
        schema_hint: str,
        *,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        response = self.chat(messages, temperature=temperature)
        parsed = _try_parse_json(response.text)
        if parsed is not None:
            return parsed
        retry_messages = list(messages) + [
            Message(role="assistant", content=response.text),
            Message(
                role="user",
                content=(
                    f"Your previous response was not valid JSON: "
                    f"{response.text[:200]!r}. "
                    f"Respond with ONLY a JSON object matching: {schema_hint}"
                ),
            ),
        ]
        response = self.chat(retry_messages, temperature=temperature)
        parsed = _try_parse_json(response.text)
        if parsed is not None:
            return parsed
        raise ChenkiParseError(raw=response.text)

    def _cache_key(self, payload: dict[str, Any]) -> str | None:
        if self._cache is None:
            return None
        from chenki.cache import hash_request

        return hash_request(
            payload["messages"], payload["model"], payload["temperature"]
        )

    def _cache_lookup(self, cache_key: str | None) -> ChatCompletion | None:
        if cache_key is None or self._cache is None:
            return None
        cached = self._cache.get(cache_key)
        if cached is None:
            return None
        return ChatCompletion(text=cached)

    def _cache_store(
        self, cache_key: str | None, completion: ChatCompletion
    ) -> None:
        if cache_key is None or self._cache is None:
            return
        self._cache.set(cache_key, completion.text)

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


def _try_parse_json(raw: str) -> dict[str, Any] | None:
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _parse_chat_completion(body: dict[str, Any]) -> ChatCompletion:
    choice = body["choices"][0]
    usage = body.get("usage") or {}
    return ChatCompletion(
        text=choice["message"]["content"],
        finish_reason=choice.get("finish_reason"),
        tokens_used=usage.get("total_tokens"),
        raw=body,
    )
