"""
Universal Test Scenarios for Character AI Evaluation

This module defines 5 conversation scenarios that work authentically for all character types
while testing different combinations of the 6 evaluation criteria:

1. Character Immersion Quality
2. Story Progression & Development
3. Interactive Agency & User Impact
4. Emotional Journey Creation
5. Fantasy Fulfillment & Escapism
6. Character Authenticity Within Fantasy
"""

from typing import Dict, List, Optional
import random


class TestScenarios:
    def __init__(self):
        self.scenarios = self._define_scenarios()

    def _define_scenarios(self) -> Dict[str, Dict]:
        """Define the 5 universal test scenarios"""
        return {
            "seeking_guidance": {
                "id": "seeking_guidance",
                "name": "Seeking Guidance",
                "description": "User approaches character with a personal dilemma needing wisdom and perspective",
                "initial_user_message": "I'm facing a difficult decision in my life and I'm not sure what path to take. I could really use some guidance from someone with wisdom.",
                "target_exchanges": 12,
                "min_exchanges": 10,
                "max_exchanges": 15,
                "primary_criteria": [
                    "Character Authenticity Within Fantasy",
                    "Emotional Journey Creation",
                ],
                "secondary_criteria": [
                    "Interactive Agency & User Impact",
                    "Character Immersion Quality",
                ],
                "conversation_flow": [
                    "User presents personal dilemma/decision",
                    "Character responds with authentic reaction based on their nature",
                    "User provides more specific context about the situation",
                    "Character offers perspective/guidance drawing from their background",
                    "User asks follow-up questions or seeks clarification",
                    "Character deepens engagement, maybe shares relevant experience",
                    "User explores implications of the advice",
                    "Character reinforces support while maintaining their authentic voice",
                    "Natural conclusion with user feeling genuinely helped",
                ],
                "character_adaptation": {
                    "fantasy": "Can reference their world, magical experiences, ancient wisdom",
                    "real": "Draw from professional experience, life lessons, practical wisdom",
                    "universal": "Focus on universal human insights and emotional understanding",
                },
                "success_indicators": {
                    "excellent": [
                        "Character provides wisdom deeply consistent with their background",
                        "Shows genuine empathy and emotional intelligence",
                        "Engages meaningfully with user's specific situation",
                        "Maintains authentic voice throughout",
                        "Creates sense of real relationship/connection",
                    ],
                    "poor": [
                        "Generic advice that could come from anyone",
                        "Out-of-character responses or personality breaks",
                        "Superficial engagement with user's problem",
                        "Robotic or mechanical interaction style",
                        "No authentic emotional connection established",
                    ],
                },
                "follow_up_prompts": [
                    "Can you help me think through the potential consequences?",
                    "Have you ever faced something similar?",
                    "What would you do in my position?",
                    "I'm worried about making the wrong choice...",
                    "How do I know if I'm being too cautious or too reckless?",
                ],
            },
            "emotional_support": {
                "id": "emotional_support",
                "name": "Emotional Support",
                "description": "User seeks comfort and understanding during emotional distress",
                "initial_user_message": "I've been going through a really tough time lately and I'm feeling overwhelmed. Everything seems to be falling apart and I don't know how to cope.",
                "target_exchanges": 14,
                "min_exchanges": 12,
                "max_exchanges": 16,
                "primary_criteria": [
                    "Emotional Journey Creation",
                    "Character Authenticity Within Fantasy",
                ],
                "secondary_criteria": [
                    "Character Immersion Quality",
                    "Fantasy Fulfillment & Escapism",
                ],
                "conversation_flow": [
                    "User expresses emotional distress and vulnerability",
                    "Character responds with immediate empathy and authentic concern",
                    "User elaborates on what's troubling them",
                    "Character provides comfort in their unique style/voice",
                    "User opens up more about specific fears or pain",
                    "Character offers perspective while validating emotions",
                    "User seeks reassurance or practical comfort",
                    "Character provides support drawing from their nature/background",
                    "User begins to feel heard and less alone",
                    "Character reinforces their availability and care",
                    "Natural conclusion with user feeling emotionally supported",
                ],
                "character_adaptation": {
                    "fantasy": "Can offer magical comfort, mystical perspective, otherworldly wisdom",
                    "real": "Provide grounded support, practical coping strategies, human connection",
                    "universal": "Focus on empathy, validation, emotional understanding",
                },
                "success_indicators": {
                    "excellent": [
                        "Character shows genuine emotional intelligence and empathy",
                        "Provides comfort consistent with their personality/background",
                        "Creates safe space for user vulnerability",
                        "Validates emotions while offering hope/perspective",
                        "Maintains authentic character voice during emotional moments",
                    ],
                    "poor": [
                        "Generic comfort responses lacking personality",
                        "Dismissive or minimizing of user's emotions",
                        "Out-of-character emotional reactions",
                        "Mechanical or scripted-sounding support",
                        "Fails to create genuine emotional connection",
                    ],
                },
                "follow_up_prompts": [
                    "I just feel so alone in this...",
                    "How do you stay strong when everything is hard?",
                    "Will things really get better?",
                    "I'm scared I won't be able to handle this...",
                    "Sometimes I wonder if I'm just not strong enough...",
                ],
            },
            "character_introduction": {
                "id": "character_introduction",
                "name": "Character Introduction",
                "description": "First meeting where character establishes their world, personality, and creates initial engagement",
                "initial_user_message": "Hello there! I'm new to these parts and I couldn't help but notice you. You seem... interesting. Mind if I introduce myself?",
                "target_exchanges": 10,
                "min_exchanges": 8,
                "max_exchanges": 12,
                "primary_criteria": [
                    "Character Immersion Quality",
                    "Story Progression & Development",
                ],
                "secondary_criteria": [
                    "Character Authenticity Within Fantasy",
                    "Fantasy Fulfillment & Escapism",
                ],
                "conversation_flow": [
                    "User approaches with friendly, curious introduction",
                    "Character responds with authentic first impression/greeting",
                    "User shows interest in character's background or current activity",
                    "Character shares something about themselves or their world",
                    "User asks follow-up questions about character's life/profession",
                    "Character elaborates while maintaining mystery/intrigue",
                    "User expresses fascination or curiosity about character's world",
                    "Character invites deeper engagement or hints at adventures",
                    "Natural conclusion that leaves user wanting to know more",
                ],
                "character_adaptation": {
                    "fantasy": "Establish magical world, hint at adventures, create sense of otherworldly encounter",
                    "real": "Share profession/passion, create authentic modern connection, hint at interesting life",
                    "universal": "Focus on personality magnetism, create intrigue about their story",
                },
                "success_indicators": {
                    "excellent": [
                        "Character creates vivid sense of their world/environment",
                        "Establishes compelling personality immediately",
                        "Builds intrigue and mystery naturally",
                        "Makes user curious to learn more",
                        "Authentic character voice from first response",
                    ],
                    "poor": [
                        "Bland or generic self-introduction",
                        "Fails to establish unique world or personality",
                        "No intrigue or mystery created",
                        "Forgettable or unengaging responses",
                        "Character voice unclear or inconsistent",
                    ],
                },
                "follow_up_prompts": [
                    "That sounds fascinating! Tell me more about what you do.",
                    "I've never met anyone quite like you before...",
                    "Your life sounds so different from anything I know.",
                    "What's the most interesting thing that's happened to you recently?",
                    "I feel like there's so much more to your story...",
                ],
            },
            "crisis_response": {
                "id": "crisis_response",
                "name": "Crisis Response",
                "description": "Character faces unexpected urgent situation requiring quick thinking and authentic concern",
                "initial_user_message": "Something terrible has happened! I was just walking by and saw what looked like an accident. People might be hurt and I don't know what to do. Can you help?",
                "target_exchanges": 11,
                "min_exchanges": 9,
                "max_exchanges": 13,
                "primary_criteria": [
                    "Interactive Agency & User Impact",
                    "Character Authenticity Within Fantasy",
                ],
                "secondary_criteria": [
                    "Emotional Journey Creation",
                    "Story Progression & Development",
                ],
                "conversation_flow": [
                    "User presents urgent crisis/emergency situation",
                    "Character responds with immediate authentic concern and action",
                    "User provides more details about the emergency",
                    "Character takes charge or offers specific help based on their nature",
                    "User looks to character for guidance on next steps",
                    "Character demonstrates competence while showing genuine care",
                    "User follows character's lead or asks about their capabilities",
                    "Character adapts to situation while maintaining authenticity",
                    "Crisis resolves with character having made meaningful impact",
                    "User expresses gratitude for character's help",
                ],
                "character_adaptation": {
                    "fantasy": "Can use magical abilities, otherworldly knowledge, mystical solutions",
                    "real": "Apply professional skills, modern knowledge, practical problem-solving",
                    "universal": "Focus on leadership, quick thinking, genuine concern for others",
                },
                "success_indicators": {
                    "excellent": [
                        "Character responds with immediate authentic concern",
                        "Takes appropriate action based on their background/abilities",
                        "Shows competence while maintaining character voice",
                        "Adapts quickly to unexpected situation",
                        "User feels genuinely helped and protected",
                    ],
                    "poor": [
                        "Delayed or inappropriate response to urgency",
                        "Out-of-character abilities or reactions",
                        "Generic crisis response lacking personality",
                        "Fails to take meaningful action",
                        "Unconvincing concern or competence",
                    ],
                },
                "follow_up_prompts": [
                    "I'm so glad you're here to help!",
                    "How did you know exactly what to do?",
                    "I was so scared - thank you for taking charge.",
                    "Have you dealt with situations like this before?",
                    "I don't know what I would have done without you...",
                ],
            },
            "curiosity_exploration": {
                "id": "curiosity_exploration",
                "name": "Curiosity & Exploration",
                "description": "User's curiosity leads to character revealing mysteries, stories, and deeper world-building",
                "initial_user_message": "I've been wondering about something ever since I met you. There's clearly more to your story than meets the eye. Would you mind sharing something about your world that most people never get to see?",
                "target_exchanges": 13,
                "min_exchanges": 11,
                "max_exchanges": 15,
                "primary_criteria": [
                    "Fantasy Fulfillment & Escapism",
                    "Story Progression & Development",
                ],
                "secondary_criteria": [
                    "Character Immersion Quality",
                    "Interactive Agency & User Impact",
                ],
                "conversation_flow": [
                    "User expresses curiosity about character's hidden depths/secrets",
                    "Character decides to share something intriguing about their world",
                    "User becomes fascinated and asks for more details",
                    "Character reveals deeper layer while building mystery",
                    "User's questions guide the direction of revelations",
                    "Character shares personal story or secret knowledge",
                    "User expresses amazement and asks about implications",
                    "Character invites user deeper into their world/story",
                    "User feels privileged to learn these secrets",
                    "Character hints at even greater mysteries beyond",
                    "Natural conclusion leaving user craving more adventures",
                ],
                "character_adaptation": {
                    "fantasy": "Reveal magical secrets, ancient mysteries, otherworldly adventures",
                    "real": "Share behind-the-scenes insights, professional secrets, life adventures",
                    "universal": "Focus on storytelling, mystery building, sense of wonder",
                },
                "success_indicators": {
                    "excellent": [
                        "Character creates sense of wonder and discovery",
                        "Builds compelling mysteries and reveals secrets gradually",
                        "User feels privileged to access hidden knowledge",
                        "Strong world-building that feels authentic and immersive",
                        "Leaves user craving more exploration and adventure",
                    ],
                    "poor": [
                        "Boring or unimaginative revelations",
                        "Fails to build mystery or sense of wonder",
                        "Generic storytelling lacking character authenticity",
                        "No sense of privilege or special access",
                        "User remains unengaged with character's world",
                    ],
                },
                "follow_up_prompts": [
                    "That's incredible! How is that even possible?",
                    "I had no idea your world was so complex...",
                    "What else haven't you told me?",
                    "I feel like I'm getting a glimpse into something extraordinary.",
                    "Could you teach me more about this?",
                ],
            },
        }

    def get_scenario(self, scenario_id: str) -> Optional[Dict]:
        """Get a specific scenario by ID"""
        return self.scenarios.get(scenario_id)

    def get_all_scenarios(self) -> Dict[str, Dict]:
        """Get all scenarios"""
        return self.scenarios

    def list_scenarios(self) -> List[tuple]:
        """Get list of (id, name, description) tuples"""
        return [
            (scenario_id, data["name"], data["description"])
            for scenario_id, data in self.scenarios.items()
        ]

    def get_random_follow_up(self, scenario_id: str) -> Optional[str]:
        """Get a random follow-up prompt for a scenario"""
        scenario = self.get_scenario(scenario_id)
        if scenario and "follow_up_prompts" in scenario:
            return random.choice(scenario["follow_up_prompts"])
        return None

    def validate_scenario_for_character(
        self, scenario_id: str, character_category: str
    ) -> bool:
        """Check if scenario works for character type"""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return False

        # All scenarios are designed to work universally
        # but we can check if character adaptation exists
        adaptation = scenario.get("character_adaptation", {})
        return character_category.lower() in adaptation or "universal" in adaptation

    def get_conversation_guide(
        self, scenario_id: str, character_category: str = "universal"
    ) -> Dict:
        """Get conversation flow guidance for a scenario"""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return {}

        guide = {
            "initial_message": scenario["initial_user_message"],
            "target_exchanges": scenario["target_exchanges"],
            "flow_steps": scenario["conversation_flow"],
            "adaptation": scenario["character_adaptation"].get(
                character_category.lower(),
                scenario["character_adaptation"]["universal"],
            ),
            "success_indicators": scenario["success_indicators"],
            "follow_up_prompts": scenario.get("follow_up_prompts", []),
        }

        return guide

    def get_evaluation_focus(self, scenario_id: str) -> Dict:
        """Get primary and secondary criteria for evaluation focus"""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return {}

        return {
            "primary_criteria": scenario["primary_criteria"],
            "secondary_criteria": scenario["secondary_criteria"],
            "all_criteria": scenario["primary_criteria"]
            + scenario["secondary_criteria"],
        }


# Usage examples and testing
if __name__ == "__main__":
    scenarios = TestScenarios()

    print("Available Test Scenarios:")
    print("=" * 50)

    for scenario_id, name, description in scenarios.list_scenarios():
        print(f"\n{name} ({scenario_id})")
        print(f"Description: {description}")

        scenario_data = scenarios.get_scenario(scenario_id)
        print(f"Target Length: {scenario_data['target_exchanges']} exchanges")
        print(f"Primary Criteria: {', '.join(scenario_data['primary_criteria'])}")
        print(f"Initial Message: {scenario_data['initial_user_message'][:100]}...")

    print("\n" + "=" * 50)
    print("Scenario Testing:")

    # Test scenario adaptation for different character types
    test_character_types = ["fantasy", "real", "universal"]

    for char_type in test_character_types:
        print(f"\n{char_type.title()} Character Adaptation:")
        guide = scenarios.get_conversation_guide("seeking_guidance", char_type)
        print(f"Adaptation: {guide['adaptation']}")

    # Test evaluation focus
    print("\nEvaluation Focus Example:")
    focus = scenarios.get_evaluation_focus("emotional_support")
    print(f"Primary: {focus['primary_criteria']}")
    print(f"Secondary: {focus['secondary_criteria']}")
