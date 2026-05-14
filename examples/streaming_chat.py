"""Stream tokens from chenki-llm and print them as they arrive."""

from chenki import ChenkiClient, Message

client = ChenkiClient(endpoint="https://brianchenhao-geyam-llm.hf.space/v1")
for chunk in client.chat_stream(
    [Message(role="user", content="Count from 1 to 5, one number per line.")]
):
    print(chunk, end="", flush=True)
print()
