import os
from dotenv import load_dotenv
from anthropic import (
    Anthropic,
    AnthropicError,
    APITimeoutError,
    APIConnectionError,
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    APIStatusError,
)

from chat_storage import ChatSession

load_dotenv()

# Timeout configuration (in seconds)
DEFAULT_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30.0"))

client = Anthropic(
    api_key=os.getenv("LITELLM_MASTER_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:4011"),
    timeout=DEFAULT_TIMEOUT,
)
model = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-6")


def handle_api_error(err: Exception) -> str:
    """Format user-friendly error messages based on exception type."""
    if isinstance(err, APITimeoutError):
        return (
            f"Request timed out after {DEFAULT_TIMEOUT}s. "
            "The model took too long to respond. Please try again or increase REQUEST_TIMEOUT."
        )
    if isinstance(err, APIConnectionError):
        return (
            "Network connection failed. "
            "Please check if your proxy or local LLM gateway (e.g., LiteLLM at 127.0.0.1:4011) is running."
        )
    if isinstance(err, AuthenticationError):
        return "Authentication failed (401). Please verify your LITELLM_MASTER_KEY in .env."
    if isinstance(err, RateLimitError):
        return "Rate limit exceeded (429). Please wait a moment before sending another message."
    if isinstance(err, BadRequestError):
        return f"Bad request (400): {err.message}"
    if isinstance(err, APIStatusError):
        return f"API error (HTTP {err.status_code}): {err.message}"
    if isinstance(err, AnthropicError):
        return f"Anthropic SDK error: {err}"
    return f"Unexpected error: {err}"


def run_chat_loop():
    session = ChatSession(model=model)
    print(f"=== Chat Session Started ({session.session_id}) ===")
    print(f"Model: {model} | Timeout: {DEFAULT_TIMEOUT}s")
    print("Type 'exit', 'quit', or 'q' to end the conversation.\n")

    while True:
        try:
            user_input = input("User: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting session...")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "q"}:
            print("Ending conversation...")
            break

        session.add_message(role="user", content=user_input)

        print("Assistant: ", end="", flush=True)
        assistant_reply_chunks = []
        is_success = False

        try:
            with client.messages.stream(
                model=model,
                max_tokens=1000,
                messages=session.get_api_messages(),
                timeout=DEFAULT_TIMEOUT,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    assistant_reply_chunks.append(text)
            print("\n")
            is_success = True
        except Exception as e:
            # Roll back user message so context remains valid for next attempt
            session.pop_last_message()
            error_msg = handle_api_error(e)
            print(f"\n[Error]: {error_msg}\n")

        if is_success:
            full_reply = "".join(assistant_reply_chunks)
            session.add_message(role="assistant", content=full_reply)
            session.save()

    if session.messages:
        saved_paths = session.save()
        print("\nChat history saved:")
        print(f"  - JSON:     {saved_paths['json']}")
        print(f"  - Markdown: {saved_paths['markdown']}")
    else:
        print("No messages were exchanged.")


if __name__ == "__main__":
    run_chat_loop()
