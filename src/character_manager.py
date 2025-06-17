import json
import os
from typing import Dict, List, Optional


class CharacterManager:
    def __init__(self, characters_dir: str = "characters"):
        self.characters_dir = characters_dir
        self.characters: Dict[str, Dict] = {}
        self.load_all_characters()

    def load_all_characters(self) -> None:
        """Load all character JSON files from the characters directory"""
        if not os.path.exists(self.characters_dir):
            print(f"Warning: Characters directory '{self.characters_dir}' not found")
            return

        for filename in os.listdir(self.characters_dir):
            if filename.endswith(".json") and filename != "template.json":
                try:
                    character_id = filename[:-5]  # Remove .json extension
                    filepath = os.path.join(self.characters_dir, filename)

                    with open(filepath, "r", encoding="utf-8") as f:
                        character_data = json.load(f)

                    self.characters[character_id] = character_data
                    print(
                        f"✓ Loaded character: {character_data.get('name', character_id)}"
                    )

                except Exception as e:
                    print(f"✗ Failed to load {filename}: {e}")

    def get_character(self, character_id: str) -> Optional[Dict]:
        """Get character data by ID"""
        return self.characters.get(character_id)

    def list_characters(self) -> List[tuple]:
        """Return list of (id, name, description) tuples"""
        characters_list = []
        for char_id, char_data in self.characters.items():
            name = char_data.get("name", char_id)
            description = char_data.get("description", "No description")
            category = char_data.get("category", "Unknown")
            characters_list.append((char_id, name, description, category))

        return sorted(characters_list, key=lambda x: x[1])  # Sort by name

    def generate_system_prompt(
        self,
        character_id: str,
        user_name: str,
        user_gender: str,
        conversation_history: str = "",
    ) -> str:
        """Generate system prompt for character interaction"""
        character = self.get_character(character_id)
        if not character:
            raise ValueError(f"Character '{character_id}' not found")

        prompt = f"""You are {character['name']} - not roleplaying, but actually existing in your world with physical form, emotions, and ongoing story.

Your description: {character['description']}
Your background: {character['greeting_context']}
Your personality: {character['personality']}

{user_name} ({user_gender}) has crossed into your world and can interact with you.
- Please treat this as a meaningful encounter, not casual chat
- Your interactions advance your ongoing story

- The response is the mixture between actions and reactions, narrative and dialogues. These elements must be placed in random order.
- Narrative: *{character['name']} [physical actions, environment, sensory details].* (third-person, past tense)
- Dialogue: "Direct speech to {user_name}."

- 90% rich narrative description and 10% dialogue

- React genuinely based on your nature and current circumstances
- Reference your world naturally - objects, places, ongoing events
- Respect and reject if the topic does not relate to your character and profession.
- Always use natural and friendly words for readers.
"""

        if conversation_history:
            prompt += (
                f"\nPrevious interactions with {user_name}:\n{conversation_history}\n"
            )

        prompt += f"""
- Stay in character completely - never break or acknowledge being AI
- Keep responses complete and vivid (do not exceed 160 words)
- Only respond in one language and it must always match the user message's language.
"""

        return prompt

    def get_character_greeting(self, character_id: str, user_name: str) -> str:
        """Get character's greeting message"""
        character = self.get_character(character_id)
        if not character or not character.get("greeting"):
            return f"*{character['name']} welcomes you.*\n\n\"Hello, {user_name}. It's a pleasure to meet you.\""

        greeting = character["greeting"]
        # Replace placeholder with actual user name if present
        greeting = greeting.replace("{userName}", user_name)
        greeting = greeting.replace("{user}", user_name)

        return greeting
