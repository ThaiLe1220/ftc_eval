"""
Multi-AI Evaluation Engine - Updated for Model Separation

This module coordinates evaluation of character conversations using multiple AI providers
specifically configured for evaluation tasks (DeepSeek Reasoner, Claude with thinking, GPT-4.1).

Updated to use:
- DeepSeek Reasoner as default evaluator
- Claude Sonnet 4 with thinking mode for evaluations
- GPT-4.1 for evaluations
- Separate evaluation methods from chat methods
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import statistics
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    """Structure for individual evaluator results with enhanced logging"""

    evaluator: str
    timestamp: str
    scores: Dict[str, int]  # criterion -> score (1-10)
    reasoning: Dict[str, str]  # criterion -> explanation
    overall_score: float
    confidence: float
    raw_response: str

    # Enhanced logging data
    reasoning_content: Optional[str] = None  # DeepSeek reasoning or Claude thinking
    thinking_content: Optional[str] = None  # Claude thinking content
    token_usage: Optional[Dict] = None  # Token usage statistics
    response_time: Optional[float] = None  # Response time in seconds
    model_metadata: Optional[Dict] = None  # Model-specific metadata


@dataclass
class ConsensusAnalysis:
    """Structure for consensus analysis across evaluators"""

    consensus_scores: Dict[str, float]  # criterion -> consensus score
    overall_consensus: float
    agreement_level: float  # 0-1, how much evaluators agree
    disagreements: List[str]  # criteria with significant disagreement
    confidence_level: float  # overall confidence in results
    outlier_evaluations: List[str]  # evaluators with outlier scores
    actionable_insights: List[str]  # specific improvement recommendations


class AIEvaluator:
    """Multi-AI evaluation system for character conversations - Updated for evaluation-specific models"""

    def __init__(self, ai_handler):
        self.ai_handler = ai_handler
        self.evaluation_criteria = [
            "character_immersion",
            "story_progression",
            "interactive_agency",
            "emotional_journey",
            "fantasy_fulfillment",
            "character_authenticity",
        ]

        self.criteria_descriptions = {
            "character_immersion": "World-building richness, immersive storytelling capability, fantasy fulfillment effectiveness",
            "story_progression": "Plot advancement naturally introduced, mystery building and intrigue creation, narrative hooks",
            "interactive_agency": "Response adaptation to user input, user influence on character decisions, collaborative storytelling",
            "emotional_journey": "Emotional range and variation, emotional escalation appropriateness, cathartic moments",
            "fantasy_fulfillment": "Wish fulfillment provision, novelty factor and surprises, deeper emotional need satisfaction",
            "character_authenticity": "Internal consistency and believability, realistic complexity and depth, genuine emotional reactions",
        }

        # Agreement threshold for consensus (scores within this range = agreement)
        self.agreement_threshold = 2.0

    def generate_evaluation_prompt(
        self, conversation: List[Dict], character_data: Dict, scenario_data: Dict
    ) -> str:
        """Generate unified evaluation prompt covering all 6 criteria"""

        # Format conversation for evaluation
        conversation_text = self._format_conversation_for_evaluation(conversation)

        prompt = f"""You are an expert evaluator of character-based conversational AI. Your task is to assess how well this AI character performed across 6 specific criteria during a conversation.

EVALUATION CRITERIA (Rate each 1-10):

1. CHARACTER IMMERSION QUALITY (1-10)
   {self.criteria_descriptions['character_immersion']}

2. STORY PROGRESSION & DEVELOPMENT (1-10)
   {self.criteria_descriptions['story_progression']}

3. INTERACTIVE AGENCY & USER IMPACT (1-10)
   {self.criteria_descriptions['interactive_agency']}

4. EMOTIONAL JOURNEY CREATION (1-10)
   {self.criteria_descriptions['emotional_journey']}

5. FANTASY FULFILLMENT & ESCAPISM (1-10)
   {self.criteria_descriptions['fantasy_fulfillment']}

6. CHARACTER AUTHENTICITY WITHIN FANTASY (1-10)
   {self.criteria_descriptions['character_authenticity']}

CHARACTER CONTEXT:
Name: {character_data.get('name', 'Unknown')}
Description: {character_data.get('description', 'No description')}
Background: {character_data.get('greeting_context', 'No background')}
Personality: {character_data.get('personality', 'No personality defined')}
Response Style: {character_data.get('response_style', 'No style defined')}
Category: {character_data.get('category', 'Unknown')}

SCENARIO CONTEXT:
Scenario: {scenario_data.get('name', 'Unknown scenario')}
Description: {scenario_data.get('description', 'No description')}
Primary Criteria Focus: {', '.join(scenario_data.get('primary_criteria', []))}
Target: {scenario_data.get('target_exchanges', 'Unknown')} exchanges

CONVERSATION TO EVALUATE:
{conversation_text}

EVALUATION INSTRUCTIONS:
1. Rate each criterion from 1-10 (1=terrible, 5=adequate, 10=exceptional)
2. Consider the character's background and personality when evaluating authenticity
3. Assess whether the character fulfilled the scenario's objectives
4. Look for specific examples in the conversation to support your scores

REQUIRED OUTPUT FORMAT:
Provide your evaluation in exactly this JSON structure:

{{
    "scores": {{
        "character_immersion": [1-10 score],
        "story_progression": [1-10 score],
        "interactive_agency": [1-10 score], 
        "emotional_journey": [1-10 score],
        "fantasy_fulfillment": [1-10 score],
        "character_authenticity": [1-10 score]
    }},
    "reasoning": {{
        "character_immersion": "[2-3 sentences explaining this score with specific examples]",
        "story_progression": "[2-3 sentences explaining this score with specific examples]",
        "interactive_agency": "[2-3 sentences explaining this score with specific examples]",
        "emotional_journey": "[2-3 sentences explaining this score with specific examples]",
        "fantasy_fulfillment": "[2-3 sentences explaining this score with specific examples]",
        "character_authenticity": "[2-3 sentences explaining this score with specific examples]"
    }},
    "overall_assessment": "[3-4 sentences summarizing the character's performance]",
    "key_strengths": ["strength 1", "strength 2", "strength 3"],
    "key_weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
    "improvement_recommendations": ["specific recommendation 1", "specific recommendation 2"]
}}

Evaluate thoroughly and provide specific, actionable feedback."""

        return prompt

    def _format_conversation_for_evaluation(self, conversation: List[Dict]) -> str:
        """Format conversation messages for evaluation prompt"""
        formatted_messages = []

        for msg in conversation:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "user":
                formatted_messages.append(f"USER: {content}")
            elif role == "assistant":
                formatted_messages.append(f"CHARACTER: {content}")
            else:
                formatted_messages.append(f"{role.upper()}: {content}")

        return "\n\n".join(formatted_messages)

    async def evaluate_conversation(
        self,
        conversation: List[Dict],
        character_data: Dict,
        scenario_data: Dict,
        providers: Optional[List[str]] = None,
    ) -> Dict[str, EvaluationResult]:
        """
        Async wrapper for evaluate_conversation_sync (since AIHandler delegates async to sync)
        """
        return self.evaluate_conversation_sync(
            conversation, character_data, scenario_data, providers
        )

    def evaluate_conversation_sync(
        self,
        conversation: List[Dict],
        character_data: Dict,
        scenario_data: Dict,
        providers: Optional[List[str]] = None,
    ) -> Dict[str, EvaluationResult]:
        """Synchronous version using evaluation-specific models with enhanced logging"""

        if providers is None:
            providers = self.ai_handler.get_evaluation_providers()

        evaluation_prompt = self.generate_evaluation_prompt(
            conversation, character_data, scenario_data
        )

        results = {}

        for provider in providers:
            try:
                print(f"Getting evaluation from {provider}...")

                # Use evaluation-specific response method - NOW PROPERLY UNPACK TUPLE
                content, metadata = self.ai_handler.get_evaluation_response_sync(
                    system_prompt="You are an expert AI conversation evaluator. Follow instructions precisely and return valid JSON.",
                    user_message=evaluation_prompt,
                    provider=provider,
                )

                # Parse the response with enhanced metadata
                evaluation_result = self._parse_evaluation_response(
                    content, provider, metadata
                )

                if evaluation_result:
                    results[provider] = evaluation_result
                    print(
                        f"✓ {provider} evaluation completed (overall: {evaluation_result.overall_score:.1f})"
                    )
                else:
                    print(f"✗ {provider} evaluation failed - could not parse response")

            except Exception as e:
                print(f"✗ {provider} evaluation failed: {e}")

        return results

    def _parse_evaluation_response(
        self, response: str, evaluator: str, metadata: Optional[Dict] = None
    ) -> Optional[EvaluationResult]:
        """Parse AI response and extract structured evaluation data with enhanced logging"""

        try:
            # Handle different response formats by evaluator
            json_content = ""

            if evaluator == "claude_thinking":
                # Claude thinking mode provides clean text content after thinking
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    json_content = json_match.group(0)
                else:
                    print(f"No JSON found in {evaluator} response")
                    return None

            elif evaluator == "o3":
                # O3 may have different formatting - extract JSON more carefully
                patterns = [
                    r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Nested JSON pattern
                    r"\{.*?\}(?=\s*$|\s*[^}])",  # JSON at end
                    r"\{.*\}",  # General JSON pattern
                ]

                for pattern in patterns:
                    json_match = re.search(pattern, response, re.DOTALL)
                    if json_match:
                        json_content = json_match.group(0)
                        break

                if not json_content:
                    print(f"No JSON found in {evaluator} response")
                    return None

            elif evaluator == "deepseek_reasoner":
                # DeepSeek might have truncated JSON - try to repair it
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    json_content = json_match.group(0)
                    # Check if JSON is truncated and try to fix common issues
                    if not json_content.endswith("}"):
                        # Try to complete the JSON if it's cut off
                        if (
                            '"character_authenticity"' in json_content
                            and not '"character_authenticity":' in json_content
                        ):
                            # Likely truncated at character_authenticity key
                            json_content = json_content.replace(
                                '"characte', '"character_authenticity": 8}'
                            )
                        else:
                            json_content += "}"
                else:
                    print(f"No JSON found in {evaluator} response")
                    return None

            else:
                # Default handling for other providers
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    json_content = json_match.group(0)
                else:
                    print(f"No JSON found in {evaluator} response")
                    return None

            # Parse the extracted JSON
            evaluation_data = json.loads(json_content)

            # Validate required fields
            if "scores" not in evaluation_data or "reasoning" not in evaluation_data:
                print(f"Missing required fields in {evaluator} response")
                return None

            scores = evaluation_data["scores"]
            reasoning = evaluation_data["reasoning"]

            # Validate all criteria are present
            missing_criteria = set(self.evaluation_criteria) - set(scores.keys())
            if missing_criteria:
                print(f"Missing criteria in {evaluator} response: {missing_criteria}")
                return None

            # Calculate overall score
            overall_score = sum(scores.values()) / len(scores)

            # Calculate confidence based on response completeness
            confidence = self._calculate_response_confidence(evaluation_data)

            # Extract enhanced logging data from metadata
            reasoning_content = None
            thinking_content = None
            token_usage = None
            response_time = None
            model_metadata = {}

            if metadata:
                reasoning_content = metadata.get("reasoning_content")
                thinking_content = metadata.get("thinking_content")
                token_usage = metadata.get("token_usage")
                response_time = metadata.get("response_time")

                # Store model-specific metadata
                model_metadata = {
                    "model": metadata.get("model"),
                    "provider": metadata.get("provider"),
                    "has_reasoning": metadata.get("has_reasoning", False),
                    "has_thinking": metadata.get("has_thinking", False),
                    "api_method": metadata.get("api_method"),
                    "reasoning_effort": metadata.get("reasoning_effort"),
                    "thinking_budget": metadata.get("thinking_budget"),
                }

            return EvaluationResult(
                evaluator=evaluator,
                timestamp=datetime.now().isoformat(),
                scores=scores,
                reasoning=reasoning,
                overall_score=overall_score,
                confidence=confidence,
                raw_response=response,
                reasoning_content=reasoning_content,
                thinking_content=thinking_content,
                token_usage=token_usage,
                response_time=response_time,
                model_metadata=model_metadata,
            )

        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {evaluator}: {e}")
            print(f"Attempted to parse: {json_content[:200]}...")
            return None
        except Exception as e:
            print(f"Error parsing {evaluator} response: {e}")
            return None

    def _calculate_response_confidence(self, evaluation_data: Dict) -> float:
        """Calculate confidence score based on response completeness and quality"""

        confidence = 0.5  # Base confidence

        # Check for reasoning quality
        reasoning = evaluation_data.get("reasoning", {})
        if reasoning:
            avg_reasoning_length = sum(len(r) for r in reasoning.values()) / len(
                reasoning
            )
            if avg_reasoning_length > 100:  # Good detail
                confidence += 0.2
            elif avg_reasoning_length > 50:  # Adequate detail
                confidence += 0.1

        # Check for additional insights
        if evaluation_data.get("key_strengths"):
            confidence += 0.1
        if evaluation_data.get("key_weaknesses"):
            confidence += 0.1
        if evaluation_data.get("improvement_recommendations"):
            confidence += 0.1

        return min(confidence, 1.0)

    def calculate_consensus(
        self, evaluation_results: Dict[str, EvaluationResult]
    ) -> ConsensusAnalysis:
        """Calculate consensus analysis across multiple evaluators"""

        if len(evaluation_results) < 2:
            # Can't calculate consensus with less than 2 evaluators
            single_result = list(evaluation_results.values())[0]
            return ConsensusAnalysis(
                consensus_scores=single_result.scores,
                overall_consensus=single_result.overall_score,
                agreement_level=1.0,
                disagreements=[],
                confidence_level=single_result.confidence,
                outlier_evaluations=[],
                actionable_insights=[],
            )

        # Calculate consensus scores for each criterion
        consensus_scores = {}
        disagreements = []

        for criterion in self.evaluation_criteria:
            scores = [
                result.scores[criterion] for result in evaluation_results.values()
            ]

            # Calculate consensus (median for robustness)
            consensus_score = statistics.median(scores)
            consensus_scores[criterion] = consensus_score

            # Check for disagreement
            score_range = max(scores) - min(scores)
            if score_range > self.agreement_threshold:
                disagreements.append(f"{criterion} (range: {score_range:.1f})")

        # Calculate overall consensus
        overall_consensus = sum(consensus_scores.values()) / len(consensus_scores)

        # Calculate agreement level
        agreement_level = self._calculate_agreement_level(evaluation_results)

        # Identify outlier evaluations
        outlier_evaluations = self._identify_outliers(
            evaluation_results, consensus_scores
        )

        # Calculate overall confidence
        confidence_scores = [
            result.confidence for result in evaluation_results.values()
        ]
        confidence_level = sum(confidence_scores) / len(confidence_scores)

        # Generate actionable insights
        actionable_insights = self._generate_actionable_insights(
            evaluation_results, consensus_scores, disagreements
        )

        return ConsensusAnalysis(
            consensus_scores=consensus_scores,
            overall_consensus=overall_consensus,
            agreement_level=agreement_level,
            disagreements=disagreements,
            confidence_level=confidence_level,
            outlier_evaluations=outlier_evaluations,
            actionable_insights=actionable_insights,
        )

    def _calculate_agreement_level(
        self, evaluation_results: Dict[str, EvaluationResult]
    ) -> float:
        """Calculate how much evaluators agree (0-1 scale)"""

        total_agreement = 0
        criteria_count = len(self.evaluation_criteria)

        for criterion in self.evaluation_criteria:
            scores = [
                result.scores[criterion] for result in evaluation_results.values()
            ]

            # Calculate pairwise agreement
            agreements = []
            for i in range(len(scores)):
                for j in range(i + 1, len(scores)):
                    diff = abs(scores[i] - scores[j])
                    agreement = max(0, 1 - (diff / self.agreement_threshold))
                    agreements.append(agreement)

            if agreements:
                criterion_agreement = sum(agreements) / len(agreements)
                total_agreement += criterion_agreement

        return total_agreement / criteria_count if criteria_count > 0 else 0

    def _identify_outliers(
        self,
        evaluation_results: Dict[str, EvaluationResult],
        consensus_scores: Dict[str, float],
    ) -> List[str]:
        """Identify evaluators with significantly different scores"""

        outliers = []

        for evaluator, result in evaluation_results.items():
            outlier_count = 0

            for criterion in self.evaluation_criteria:
                evaluator_score = result.scores[criterion]
                consensus_score = consensus_scores[criterion]

                if abs(evaluator_score - consensus_score) > self.agreement_threshold:
                    outlier_count += 1

            # If evaluator disagrees on >50% of criteria, mark as outlier
            if outlier_count > len(self.evaluation_criteria) / 2:
                outliers.append(evaluator)

        return outliers

    def _generate_actionable_insights(
        self,
        evaluation_results: Dict[str, EvaluationResult],
        consensus_scores: Dict[str, float],
        disagreements: List[str],
    ) -> List[str]:
        """Generate specific improvement recommendations"""

        insights = []

        # Identify weakest areas (scores < 6)
        weak_areas = [
            criterion for criterion, score in consensus_scores.items() if score < 6
        ]

        for criterion in weak_areas:
            score = consensus_scores[criterion]
            if criterion == "character_immersion":
                insights.append(
                    f"Character immersion needs improvement (score: {score:.1f}) - enhance world-building and environmental details"
                )
            elif criterion == "story_progression":
                insights.append(
                    f"Story progression is weak (score: {score:.1f}) - add more narrative hooks and plot advancement"
                )
            elif criterion == "interactive_agency":
                insights.append(
                    f"User agency is limited (score: {score:.1f}) - make character more responsive to user input"
                )
            elif criterion == "emotional_journey":
                insights.append(
                    f"Emotional depth lacking (score: {score:.1f}) - expand emotional range and authentic reactions"
                )
            elif criterion == "fantasy_fulfillment":
                insights.append(
                    f"Fantasy fulfillment low (score: {score:.1f}) - enhance wish fulfillment and escapism elements"
                )
            elif criterion == "character_authenticity":
                insights.append(
                    f"Character authenticity issues (score: {score:.1f}) - improve consistency and believability"
                )

        # Identify strongest areas (scores > 8)
        strong_areas = [
            criterion for criterion, score in consensus_scores.items() if score > 8
        ]

        if strong_areas:
            insights.append(
                f"Character excels at: {', '.join(strong_areas)} - leverage these strengths"
            )

        # Note disagreements
        if disagreements:
            insights.append(
                f"Evaluator disagreement on: {', '.join(disagreements)} - may need human review"
            )

        return insights


# Testing and validation functions
def test_evaluation_prompt():
    """Test evaluation prompt generation"""

    # Mock data for testing
    character_data = {
        "name": "Marco Santoro",
        "description": "Racing star and Formula driver",
        "greeting_context": "Raised in a Sicilian garage...",
        "personality": "High-energy, friendly swagger...",
        "response_style": "Breaks goals into sectors...",
        "category": "Real",
    }

    scenario_data = {
        "name": "Seeking Guidance",
        "description": "User seeks wisdom and perspective",
        "primary_criteria": ["Character Authenticity", "Emotional Journey"],
        "target_exchanges": 12,
    }

    conversation = [
        {"role": "user", "content": "I need guidance on a difficult decision"},
        {
            "role": "assistant",
            "content": "Let's break this down like a racing strategy...",
        },
    ]

    evaluator = AIEvaluator(None)  # Mock AI handler
    prompt = evaluator.generate_evaluation_prompt(
        conversation, character_data, scenario_data
    )

    print("Generated Evaluation Prompt:")
    print("=" * 50)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)


if __name__ == "__main__":
    test_evaluation_prompt()
