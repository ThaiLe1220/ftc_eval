"""
Conversation Generator - Fixed with Character Greeting + Enhanced User Bot Context

FIXED:
1. Conversations now start with character's signature greeting
2. User bot gets full character context for realistic responses
3. User responds to greeting + introduces scenario naturally
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
    """Generates realistic conversations with proper character greeting and context"""

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
        chatbot_provider: str = "gpt",
        user_name: str = "TestUser",
    ) -> Conversation:
        """Generate complete conversation starting with character greeting"""

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

        # FIXED: Start with character's signature greeting
        character_greeting = self.character_manager.get_character_greeting(
            character_id, user_name
        )
        conversation.add_message("assistant", character_greeting)

        # FIXED: Generate user response to greeting + scenario introduction
        user_response = self._generate_greeting_response_with_scenario(
            character_data, scenario_data, character_greeting, user_name
        )
        conversation.add_message("user", user_response)

        # Generate character's response to user's scenario introduction
        system_prompt = self.character_manager.generate_system_prompt(
            character_id, user_name, "other", conversation.get_formatted_history()
        )

        character_response = self.ai_handler.get_response_sync(
            system_prompt, user_response, chatbot_provider
        )
        conversation.add_message("assistant", character_response)

        # Generate remaining conversation exchanges
        target_exchanges = scenario_data.get("target_exchanges", 10)

        # We've already done 2 exchanges (greeting + scenario intro), continue from there
        exchanges_completed = 2
        max_exchanges = target_exchanges // 2

        for exchange_num in range(3, max_exchanges + 1):
            if exchanges_completed >= max_exchanges:
                break

            # Generate user response with full character context
            user_response = self._generate_user_response(
                conversation, character_data, scenario_data, exchange_num
            )

            if not user_response:
                break

            conversation.add_message("user", user_response)

            # Generate character response
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
            f"✓ Generated conversation: {exchanges_completed} exchanges, {conversation.get_message_count()} messages (started with character greeting)"
        )
        return conversation

    def _generate_greeting_response_with_scenario(
        self,
        character_data: Dict,
        scenario_data: Dict,
        character_greeting: str,
        user_name: str,
    ) -> str:
        """Generate user response that acknowledges greeting and introduces scenario"""

        character_name = character_data.get("name", "Character")
        character_description = character_data.get("description", "")
        scenario_initial_message = scenario_data["initial_user_message"]
        scenario_name = scenario_data.get("name", "")
        scenario_description = scenario_data.get("description", "")

        # Enhanced user prompt with character awareness
        user_prompt = f"""You just met {character_name} who greeted you with: "{character_greeting}"

CHARACTER CONTEXT:
- Name: {character_name}
- Description: {character_description}
- Background: {character_data.get('greeting_context', '')}
- Personality: {character_data.get('personality', '')}

SCENARIO CONTEXT:
- Scenario: {scenario_name}
- Your situation: {scenario_description}
- What you need to communicate: {scenario_initial_message}

Generate a natural user response that:
1. Acknowledges their greeting appropriately 
2. Responds to their personality/style naturally
3. Introduces the scenario situation smoothly
4. Feels like a real person who just met this character
5. Is 2-4 sentences long

Examples:
- If they're energetic: Match some energy before bringing up your issue
- If they're formal: Be polite and respectful 
- If they're mystical: Show curiosity about their world

Respond only with the user message, no quotes or formatting."""

        try:
            # Use GPT-4.1 for user responses with enhanced context
            user_response = self.ai_handler.get_response_sync(
                "You are helping generate realistic user responses that show awareness of who they're talking to. Be natural, contextual, and engaging.",
                user_prompt,
                "gpt",
            )

            # Clean up response
            user_response = user_response.strip()
            if user_response.startswith('"') and user_response.endswith('"'):
                user_response = user_response[1:-1]

            return user_response if user_response else scenario_initial_message

        except Exception as e:
            print(f"Error generating greeting response: {e}")
            # Fallback to scenario message
            return scenario_initial_message

    def _generate_user_response(
        self,
        conversation: Conversation,
        character_data: Dict,
        scenario_data: Dict,
        exchange_num: int,
    ) -> Optional[str]:
        """Generate contextual user response with full character awareness"""

        character_name = character_data.get("name", "Character")
        character_description = character_data.get("description", "")
        character_personality = character_data.get("personality", "")
        character_background = character_data.get("greeting_context", "")

        scenario_name = scenario_data.get("name", "Unknown")
        scenario_description = scenario_data.get("description", "")
        conversation_flow = scenario_data.get("conversation_flow", [])
        follow_up_prompts = scenario_data.get("follow_up_prompts", [])

        # Get conversation history
        recent_messages = conversation.get_last_messages(4)
        history_text = ""
        for role, content in recent_messages:
            if role == "user":
                history_text += f"You: {content}\n"
            else:
                history_text += f"{character_name}: {content}\n"

        # Build guidance for user response
        flow_guidance = ""
        if exchange_num - 1 < len(conversation_flow):
            flow_guidance = conversation_flow[exchange_num - 1]
        elif follow_up_prompts:
            flow_guidance = random.choice(follow_up_prompts)

        # Enhanced user response prompt with character context
        user_prompt = f"""You are having a conversation with {character_name} in the "{scenario_name}" scenario.

CHARACTER YOU'RE TALKING TO:
- Name: {character_name}
- Description: {character_description}
- Personality: {character_personality}
- Background: {character_background}

SCENARIO CONTEXT:
- Scenario: {scenario_name}
- Description: {scenario_description}

RECENT CONVERSATION:
{history_text}

GUIDANCE FOR THIS RESPONSE: {flow_guidance}

Generate a natural user response that:
1. Shows awareness of who you're talking to ({character_name})
2. Responds appropriately to their personality and style
3. Advances the scenario naturally
4. Feels like a real person's response (not robotic)
5. Is 1-3 sentences long
6. References their profession/world naturally when relevant

Examples:
- If talking to a racing driver: Can reference speed, racing, cars naturally
- If talking to a teacher: Can show respect for their expertise with children
- If talking to a mystical character: Can show curiosity about their magical world

Respond only with the user message, no quotes or formatting."""

        try:
            # Always use GPT-4.1 for user responses with enhanced character context
            user_response = self.ai_handler.get_response_sync(
                "You are helping generate realistic user responses that show natural awareness of the character's identity, profession, and personality. Be contextual and authentic.",
                user_prompt,
                "gpt",
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
    """Test conversation generation with new greeting-first approach"""
    # Import here to avoid circular imports
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

    from ai_handler import AIHandler

    print("Testing Enhanced Conversation Generator...")

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

        # Show conversation flow
        messages = test_conversation.get_last_messages(6)
        print("\n📝 Conversation Preview:")
        for i, (role, content) in enumerate(messages):
            speaker = "Character" if role == "assistant" else "User"
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"{i+1}. {speaker}: {preview}")

        # Verify it starts with character greeting
        first_message = messages[0] if messages else None
        if first_message and first_message[0] == "assistant":
            print("\n✅ Conversation correctly starts with character greeting")
        else:
            print("\n❌ Conversation does not start with character greeting")
    else:
        print("✗ Test conversation generation failed")


if __name__ == "__main__":
    test_conversation_generator()
