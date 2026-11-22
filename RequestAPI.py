from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
import os

client = Anthropic(
    api_key=os.getenv("LITELLM_MASTER_KEY"),
    base_url="http://127.0.0.1:4011"
)
model = "claude-opus-4-6"

with client.messages.stream(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What is quantum computing? Answer in one sentence"
        }
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    print()