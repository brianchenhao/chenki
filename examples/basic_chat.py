"""Minimal connect-and-chat example for chenki."""

from chenki import ChenkiClient, Message

client = ChenkiClient(endpoint="https://brianchenhao-geyam-llm.hf.space/v1")
reply = client.chat(
    [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Say hello in one short sentence."),
    ]
)
print(reply.text)
