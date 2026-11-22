import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class ChatSession:
    def __init__(self, model: str, storage_dir: str = "chat_histories"):
        self.model = model
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.start_time = datetime.now()
        self.session_id = f"chat_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        self.messages: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def pop_last_message(self) -> Dict[str, Any] | None:
        if self.messages:
            return self.messages.pop()
        return None

    def get_api_messages(self) -> List[Dict[str, str]]:
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]

    def save(self) -> Dict[str, Path]:
        json_path = self._save_json()
        md_path = self._save_markdown()
        return {"json": json_path, "markdown": md_path}

    def _save_json(self) -> Path:
        file_path = self.storage_dir / f"{self.session_id}.json"
        data = {
            "session_id": self.session_id,
            "model": self.model,
            "created_at": self.start_time.isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": self.messages,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path

    def _save_markdown(self) -> Path:
        file_path = self.storage_dir / f"{self.session_id}.md"
        lines = [
            f"# Chat Session: {self.session_id}",
            "",
            f"- **Model**: {self.model}",
            f"- **Started At**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Updated At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]

        for msg in self.messages:
            role_title = "User" if msg["role"] == "user" else "Assistant"
            formatted_time = msg.get("timestamp", "")
            if formatted_time:
                try:
                    formatted_time = datetime.fromisoformat(formatted_time).strftime("%H:%M:%S")
                except ValueError:
                    pass
            lines.append(f"### {role_title} `({formatted_time})`")
            lines.append("")
            lines.append(msg["content"])
            lines.append("")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return file_path
