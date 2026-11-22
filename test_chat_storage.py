import json
import shutil
import tempfile
from pathlib import Path

from chat_storage import ChatSession


def test_chat_session_storage():
    temp_dir = tempfile.mkdtemp()
    try:
        session = ChatSession(model="claude-opus-4-6", storage_dir=temp_dir)
        session.add_message("user", "Hello, who are you?")
        session.add_message("assistant", "I am Claude, an AI assistant.")

        # Test API format
        api_messages = session.get_api_messages()
        assert len(api_messages) == 2
        assert api_messages[0] == {"role": "user", "content": "Hello, who are you?"}
        assert api_messages[1] == {"role": "assistant", "content": "I am Claude, an AI assistant."}

        # Test file saving
        saved = session.save()
        json_file = Path(saved["json"])
        md_file = Path(saved["markdown"])

        assert json_file.exists()
        assert md_file.exists()

        # Verify JSON content
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["session_id"] == session.session_id
            assert data["model"] == "claude-opus-4-6"
            assert len(data["messages"]) == 2
            assert data["messages"][0]["role"] == "user"
            assert data["messages"][0]["content"] == "Hello, who are you?"
            assert "timestamp" in data["messages"][0]

        # Verify Markdown content
        md_content = md_file.read_text(encoding="utf-8")
        assert f"# Chat Session: {session.session_id}" in md_content
        assert "- **Model**: claude-opus-4-6" in md_content
        assert "### User" in md_content
        assert "Hello, who are you?" in md_content
        assert "### Assistant" in md_content
        assert "I am Claude, an AI assistant." in md_content

        print("All chat storage tests passed!")
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_chat_session_storage()
