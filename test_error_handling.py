import httpx2 as httpx
from anthropic import (
    APITimeoutError,
    APIConnectionError,
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    APIStatusError,
)
from RequestAPI import handle_api_error
from chat_storage import ChatSession


def test_handle_api_error_messages():
    # 1. Timeout
    req = httpx.Request("POST", "http://test")
    timeout_err = APITimeoutError(request=req)
    msg = handle_api_error(timeout_err)
    assert "timed out" in msg

    # 2. Connection Error
    conn_err = APIConnectionError(request=req)
    msg = handle_api_error(conn_err)
    assert "Network connection failed" in msg

    # 3. Authentication Error
    resp_401 = httpx.Response(401, request=req)
    auth_err = AuthenticationError("Unauthorized", response=resp_401, body={})
    msg = handle_api_error(auth_err)
    assert "Authentication failed (401)" in msg

    # 4. Rate Limit
    resp_429 = httpx.Response(429, request=req)
    rate_err = RateLimitError("Too Many Requests", response=resp_429, body={})
    msg = handle_api_error(rate_err)
    assert "Rate limit exceeded (429)" in msg

    # 5. Bad Request
    resp_400 = httpx.Response(400, request=req)
    bad_req_err = BadRequestError("Invalid parameter", response=resp_400, body={})
    msg = handle_api_error(bad_req_err)
    assert "Bad request (400)" in msg

    print("All error message formatting tests passed!")


def test_session_rollback_on_error():
    session = ChatSession(model="claude-opus-4-6")
    session.add_message("user", "This prompt will fail")
    assert len(session.messages) == 1

    # Simulate error cleanup
    popped = session.pop_last_message()
    assert popped["content"] == "This prompt will fail"
    assert len(session.messages) == 0

    print("Session rollback test passed!")


if __name__ == "__main__":
    test_handle_api_error_messages()
    test_session_rollback_on_error()
