"""
Conversation Generator - Automated conversation creation for character evaluation

This module replaces hardcoded conversations with AI-generated conversations
that follow scenario objectives and maintain natural flow.

Fixed AI assignments:
- User responses: GPT-4.1 (always)
- Character responses: Specified chatbot AI (Claude/GPT-4.1/etc.)
- Evaluation: DeepSeek Reasoner (always)
"""

import random
import sys
import os
from typing import Dict, List, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from conversation import Conversation
from character_manager import CharacterManager
from test_scenarios import TestScenarios


class ConversationGenerator:
    """Generates realistic conversations between user and character for evaluation"""

    def __init__(
        self, ai_handler, character_manager: CharacterManager, scenarios: TestScenarios
    ):
        self.ai_handler = ai_handler
        self.character_manager = character_manager
        self.scenarios = scenarios

    def generate(
        self,
        character_data: Dict,
        scenario_data: Dict,
        chatbot_provider: str = "claude",
        user_name: str = "TestUser",
    ) -> Conversation:
        """Generate complete conversation following scenario objectives"""

        character_id = character_data["id"]
        character_name = character_data["name"]
        scenario_id = scenario_data["id"]

        # Create conversation object
        conversation = Conversation(
            character_id=character_id,
            character_name=character_name,
            user_name=user_name,
            scenario_id=scenario_id,
            provider=chatbot_provider,
        )

        # Start with scenario's initial user message
        initial_message = scenario_data["initial_user_message"]
        conversation.add_message("user", initial_message)

        # Generate character's greeting/first response
        system_prompt = self.character_manager.generate_system_prompt(
            character_id, user_name, "other", ""  # No history for first response
        )

        character_response = self.ai_handler.get_response_sync(
            system_prompt, initial_message, chatbot_provider
        )
        conversation.add_message("assistant", character_response)

        # Generate remaining conversation exchanges
        target_exchanges = scenario_data.get("target_exchanges", 10)
        conversation_flow = scenario_data.get("conversation_flow", [])
        follow_up_prompts = scenario_data.get("follow_up_prompts", [])

        # Generate exchanges (each exchange = user message + character response)
        exchanges_completed = 1  # Already did initial exchange
        max_exchanges = target_exchanges // 2  # Convert to exchange pairs

        for exchange_num in range(2, max_exchanges + 1):
            if exchanges_completed >= max_exchanges:
                break

            # Generate user response using GPT-4.1
            user_response = self._generate_user_response(
                conversation, scenario_data, exchange_num
            )

            if not user_response:
                break

            conversation.add_message("user", user_response)

            # Generate character response using specified provider
            updated_system_prompt = self.character_manager.generate_system_prompt(
                character_id, user_name, "other", conversation.get_formatted_history()
            )

            character_response = self.ai_handler.get_response_sync(
                updated_system_prompt, user_response, chatbot_provider
            )
            conversation.add_message("assistant", character_response)

            exchanges_completed += 1

            # Validate conversation quality
            if not self._validate_conversation_quality(conversation, scenario_data):
                print(f"⚠️ Quality check failed at exchange {exchange_num}")
                break

        # Mark conversation as complete
        conversation.mark_complete("completed")

        print(
            f"✓ Generated conversation: {exchanges_completed} exchanges, {conversation.get_message_count()} messages"
        )
        return conversation

    def _generate_user_response(
        self, conversation: Conversation, scenario_data: Dict, exchange_num: int
    ) -> Optional[str]:
        """Generate contextual user response using GPT-4.1"""

        scenario_name = scenario_data.get("name", "Unknown")
        scenario_description = scenario_data.get("description", "")
        conversation_flow = scenario_data.get("conversation_flow", [])
        follow_up_prompts = scenario_data.get("follow_up_prompts", [])

        # Get conversation history
        recent_messages = conversation.get_last_messages(4)  # Last 2 exchanges
        history_text = ""
        for role, content in recent_messages:
            if role == "user":
                history_text += f"User: {content}\n"
            else:
                history_text += f"Character: {content}\n"

        # Build guidance for user response
        flow_guidance = ""
        if exchange_num - 1 < len(conversation_flow):
            flow_guidance = conversation_flow[exchange_num - 1]
        elif follow_up_prompts:
            flow_guidance = random.choice(follow_up_prompts)

        # Create user response prompt
        user_prompt = f"""You are a user having a conversation with an AI character in the "{scenario_name}" scenario.

Scenario Description: {scenario_description}

Recent conversation:
{history_text}

Your role: Continue this conversation naturally as a user who {scenario_description.lower()}. 

Guidance for this response: {flow_guidance}

Generate a natural user response that:
1. Follows the conversation flow naturally
2. Shows genuine engagement with the character
3. Advances the scenario objectives
4. Feels like a real person's response (not robotic)
5. Is 1-3 sentences long

Respond only with the user message, no quotes or formatting."""

        try:
            # Always use GPT-4.1 for user responses
            user_response = self.ai_handler.get_response_sync(
                "You are helping generate realistic user responses for character evaluation conversations. Be natural and engaging.",
                user_prompt,
                "gpt",  # GPT-4.1 provider
            )

            # Clean up response
            user_response = user_response.strip()
            if user_response.startswith('"') and user_response.endswith('"'):
                user_response = user_response[1:-1]

            return user_response if user_response else None

        except Exception as e:
            print(f"Error generating user response: {e}")
            # Fallback to scenario prompts
            if follow_up_prompts:
                return random.choice(follow_up_prompts)
            return None

    def _validate_conversation_quality(
        self, conversation: Conversation, scenario_data: Dict
    ) -> bool:
        """Basic quality validation for generated conversation"""

        messages = conversation.get_last_messages(2)  # Last exchange
        if len(messages) < 2:
            return True

        user_msg = messages[0][1] if messages[0][0] == "user" else messages[1][1]
        char_msg = messages[1][1] if messages[1][0] == "assistant" else messages[0][1]

        # Basic quality checks
        quality_checks = [
            len(user_msg) > 10,  # User message has substance
            len(char_msg) > 20,  # Character response has substance
            not user_msg.lower().startswith("error"),  # No error messages
            not char_msg.lower().startswith("error"),
            "..." not in user_msg or user_msg.count("...") < 3,  # Not too many ellipses
        ]

        return sum(quality_checks) >= 4  # Pass if 4/5 checks pass

    def generate_test_conversation(
        self, character_id: str, scenario_id: str, chatbot_provider: str = "claude"
    ) -> Optional[Conversation]:
        """Convenience method for generating test conversations"""

        character_data = self.character_manager.get_character(character_id)
        scenario_data = self.scenarios.get_scenario(scenario_id)

        if not character_data or not scenario_data:
            print(
                f"Error: Missing character ({character_id}) or scenario ({scenario_id})"
            )
            return None

        return self.generate(character_data, scenario_data, chatbot_provider)


# Testing function for validation
def test_conversation_generator():
    """Test conversation generation with existing system"""
    # Import here to avoid circular imports
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

    from ai_handler import AIHandler

    print("Testing Conversation Generator...")

    # Initialize components
    ai_handler = AIHandler()
    character_manager = CharacterManager()
    scenarios = TestScenarios()

    generator = ConversationGenerator(ai_handler, character_manager, scenarios)

    # Test with Marco and seeking guidance scenario
    test_conversation = generator.generate_test_conversation(
        "marco", "seeking_guidance", "claude"
    )

    if test_conversation:
        print(
            f"✓ Generated test conversation with {test_conversation.get_message_count()} messages"
        )

        # Show first few messages
        recent_messages = test_conversation.get_last_messages(4)
        for role, content in recent_messages:
            print(f"{role}: {content[:100]}...")
    else:
        print("✗ Test conversation generation failed")


if __name__ == "__main__":
    test_conversation_generator()
