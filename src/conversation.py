from typing import List, Tuple, Dict, Optional
from datetime import datetime
import json


class Conversation:
    def __init__(
        self,
        character_id: str,
        character_name: str,
        user_name: str,
        max_history: int = 10,
        scenario_id: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        self.character_id = character_id
        self.character_name = character_name
        self.user_name = user_name
        self.max_history = max_history
        self.scenario_id = scenario_id
        self.provider = provider
        self.messages: List[Tuple[str, str, datetime]] = (
            []
        )  # (role, content, timestamp)

        # Evaluation metadata
        self.conversation_id: Optional[str] = None
        self.evaluation_metadata = {
            "start_time": datetime.now(),
            "end_time": None,
            "total_duration": None,
            "completion_status": "in_progress",
        }

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        timestamp = datetime.now()
        self.messages.append((role, content, timestamp))

        # Keep only the last max_history messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]

        # Update evaluation metadata
        self.evaluation_metadata["last_activity"] = timestamp
        if role == "user":
            self.evaluation_metadata["last_user_message"] = timestamp

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
        self.evaluation_metadata["completion_status"] = "cleared"

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

    # New evaluation-related methods

    def set_conversation_id(self, conversation_id: str) -> None:
        """Set the conversation ID for evaluation tracking"""
        self.conversation_id = conversation_id

    def set_scenario(self, scenario_id: str) -> None:
        """Set the scenario being tested"""
        self.scenario_id = scenario_id

    def set_provider(self, provider: str) -> None:
        """Set the AI provider being used"""
        self.provider = provider

    def mark_complete(self, completion_status: str = "completed") -> None:
        """Mark conversation as complete for evaluation"""
        self.evaluation_metadata["end_time"] = datetime.now()
        self.evaluation_metadata["completion_status"] = completion_status

        # Calculate duration
        start_time = self.evaluation_metadata["start_time"]
        end_time = self.evaluation_metadata["end_time"]
        self.evaluation_metadata["total_duration"] = (
            end_time - start_time
        ).total_seconds()

    def get_evaluation_format(self) -> List[Dict]:
        """Format conversation for evaluation system"""
        evaluation_messages = []

        for role, content, timestamp in self.messages:
            evaluation_messages.append(
                {"role": role, "content": content, "timestamp": timestamp.isoformat()}
            )

        return evaluation_messages

    def get_conversation_metadata(self) -> Dict:
        """Get metadata for evaluation system"""
        user_message_count = sum(1 for role, _, _ in self.messages if role == "user")
        assistant_message_count = sum(
            1 for role, _, _ in self.messages if role == "assistant"
        )
        total_length = sum(len(content) for _, content, _ in self.messages)

        # Calculate average message length
        avg_message_length = total_length / len(self.messages) if self.messages else 0

        # Calculate conversation flow metrics
        conversation_turns = len(self.messages) // 2  # Approximate conversation turns

        metadata = {
            "conversation_id": self.conversation_id,
            "character_id": self.character_id,
            "character_name": self.character_name,
            "user_name": self.user_name,
            "scenario_id": self.scenario_id,
            "provider": self.provider,
            "message_statistics": {
                "total_messages": len(self.messages),
                "user_messages": user_message_count,
                "assistant_messages": assistant_message_count,
                "conversation_turns": conversation_turns,
                "total_length": total_length,
                "average_message_length": avg_message_length,
            },
            "timing": self.evaluation_metadata.copy(),
        }

        return metadata

    def validate_for_evaluation(self) -> Tuple[bool, List[str]]:
        """Validate conversation is ready for evaluation"""
        issues = []

        # Check minimum message count
        if len(self.messages) < 4:  # At least 2 exchanges
            issues.append("Conversation too short (minimum 4 messages required)")

        # Check for proper alternation
        if len(self.messages) > 1:
            previous_role = None
            for role, _, _ in self.messages:
                if role == previous_role:
                    issues.append(
                        "Messages not properly alternating between user and assistant"
                    )
                    break
                previous_role = role

        # Check for empty messages
        empty_messages = [
            i for i, (_, content, _) in enumerate(self.messages) if not content.strip()
        ]
        if empty_messages:
            issues.append(f"Empty messages found at positions: {empty_messages}")

        # Check required metadata
        if not self.character_id:
            issues.append("Missing character_id")

        if not self.scenario_id:
            issues.append("Missing scenario_id")

        if not self.provider:
            issues.append("Missing provider")

        return len(issues) == 0, issues

    def export_for_evaluation(self) -> Dict:
        """Export complete conversation data for evaluation system"""
        is_valid, validation_issues = self.validate_for_evaluation()

        export_data = {
            "conversation_data": {
                "messages": self.get_evaluation_format(),
                "metadata": self.get_conversation_metadata(),
                "validation": {"is_valid": is_valid, "issues": validation_issues},
            },
            "export_timestamp": datetime.now().isoformat(),
            "format_version": "1.0",
        }

        return export_data

    def save_to_file(self, filepath: str) -> None:
        """Save conversation to JSON file"""
        export_data = self.export_for_evaluation()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> "Conversation":
        """Load conversation from JSON file"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        conv_data = data["conversation_data"]
        metadata = conv_data["metadata"]

        # Create conversation instance
        conversation = cls(
            character_id=metadata["character_id"],
            character_name=metadata["character_name"],
            user_name=metadata["user_name"],
            scenario_id=metadata.get("scenario_id"),
            provider=metadata.get("provider"),
        )

        # Set conversation ID
        if metadata.get("conversation_id"):
            conversation.set_conversation_id(metadata["conversation_id"])

        # Load messages
        for msg_data in conv_data["messages"]:
            timestamp = datetime.fromisoformat(msg_data["timestamp"])
            conversation.messages.append(
                (msg_data["role"], msg_data["content"], timestamp)
            )

        # Load evaluation metadata
        if "timing" in metadata:
            conversation.evaluation_metadata.update(metadata["timing"])

        return conversation

    def get_quality_metrics(self) -> Dict:
        """Calculate conversation quality metrics"""
        if not self.messages:
            return {"error": "No messages to analyze"}

        # Message length analysis
        message_lengths = [len(content) for _, content, _ in self.messages]

        # Response time analysis (if we have timestamps)
        response_times = []
        for i in range(1, len(self.messages)):
            prev_time = self.messages[i - 1][2]
            curr_time = self.messages[i][2]
            response_times.append((curr_time - prev_time).total_seconds())

        # Character vs user balance
        user_content = sum(
            len(content) for role, content, _ in self.messages if role == "user"
        )
        assistant_content = sum(
            len(content) for role, content, _ in self.messages if role == "assistant"
        )

        metrics = {
            "message_count": len(self.messages),
            "conversation_turns": len(self.messages) // 2,
            "message_lengths": {
                "average": sum(message_lengths) / len(message_lengths),
                "min": min(message_lengths),
                "max": max(message_lengths),
            },
            "content_balance": {
                "user_content_length": user_content,
                "assistant_content_length": assistant_content,
                "balance_ratio": (
                    assistant_content / user_content if user_content > 0 else 0
                ),
            },
            "timing": {
                "average_response_time": (
                    sum(response_times) / len(response_times) if response_times else 0
                ),
                "total_duration": self.evaluation_metadata.get("total_duration", 0),
            },
        }

        return metrics


# Testing function
def test_enhanced_conversation():
    """Test the enhanced conversation functionality"""
    print("Testing Enhanced Conversation...")

    # Create conversation
    conv = Conversation(
        "marco",
        "Marco Santoro",
        "TestUser",
        scenario_id="seeking_guidance",
        provider="claude",
    )
    conv.set_conversation_id("test_conv_001")

    # Add test messages
    conv.add_message("user", "Hello, I need some guidance")
    conv.add_message(
        "assistant",
        "Hello! I'd be happy to help guide you through whatever challenge you're facing.",
    )
    conv.add_message("user", "I'm trying to decide between two career paths")
    conv.add_message(
        "assistant",
        "That's a significant decision. Let me help you break this down like we would analyze a racing strategy...",
    )

    # Mark as complete
    conv.mark_complete("completed")

    # Test validation
    is_valid, issues = conv.validate_for_evaluation()
    print(f"Validation: {'✓ Valid' if is_valid else '✗ Invalid'}")
    if issues:
        print(f"Issues: {issues}")

    # Test metadata
    metadata = conv.get_conversation_metadata()
    print(f"Messages: {metadata['message_statistics']['total_messages']}")
    print(f"Total length: {metadata['message_statistics']['total_length']} characters")

    # Test quality metrics
    quality = conv.get_quality_metrics()
    print(f"Average message length: {quality['message_lengths']['average']:.1f}")
    print(f"Content balance ratio: {quality['content_balance']['balance_ratio']:.2f}")

    print("✓ Enhanced Conversation test completed")


if __name__ == "__main__":
    test_enhanced_conversation()
