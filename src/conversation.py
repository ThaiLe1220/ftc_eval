from typing import List, Tuple
from datetime import datetime


class Conversation:
    def __init__(
        self,
        character_id: str,
        character_name: str,
        user_name: str,
        max_history: int = 10,
    ):
        self.character_id = character_id
        self.character_name = character_name
        self.user_name = user_name
        self.max_history = max_history
        self.messages: List[Tuple[str, str, datetime]] = (
            []
        )  # (role, content, timestamp)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        timestamp = datetime.now()
        self.messages.append((role, content, timestamp))

        # Keep only the last max_history messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]

    def get_formatted_history(self) -> str:
        """Get conversation history formatted for AI context"""
        if not self.messages:
            return ""

        history_lines = []
        for role, content, _ in self.messages[:-1]:  # Exclude the current message
            if role == "user":
                history_lines.append(f"{self.user_name}: {content}")
            else:
                history_lines.append(f"{self.character_name}: {content}")

        return "\n\n".join(history_lines)

    def get_last_messages(self, count: int = 5) -> List[Tuple[str, str]]:
        """Get the last N messages as (role, content) tuples"""
        return [(role, content) for role, content, _ in self.messages[-count:]]

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.messages = []

    def get_message_count(self) -> int:
        """Get total number of messages"""
        return len(self.messages)

    def get_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.messages:
            return "No messages yet"

        user_messages = sum(1 for role, _, _ in self.messages if role == "user")
        ai_messages = sum(1 for role, _, _ in self.messages if role == "assistant")

        return f"Conversation with {self.character_name}: {user_messages} user messages, {ai_messages} AI responses"
