"""
Evaluation Pipeline - Reusable multithreaded evaluation engine

Extracted from phase1_integration_test.py and enhanced for CLI usage.
Handles multithreaded character evaluation with session management.
"""

import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Callable

from conversation_generator import ConversationGenerator
from ai_evaluator import AIEvaluator, ConsensusAnalysis


class EvaluationPipeline:
    """Reusable multithreaded evaluation pipeline for character testing"""

    def __init__(self, ai_handler, character_manager, scenarios, results_manager):
        self.ai_handler = ai_handler
        self.character_manager = character_manager
        self.scenarios = scenarios
        self.results_manager = results_manager

        # Initialize sub-components
        self.evaluator = AIEvaluator(ai_handler)
        self.conversation_generator = ConversationGenerator(
            ai_handler, character_manager, scenarios
        )

        # Thread coordination
        self.output_lock = threading.Lock()

    def execute_evaluation(
        self,
        characters: List[str],
        scenarios: List[str] = None,
        bots_ai: str = "claude",
        session_id: Optional[str] = None,
        max_workers: int = 4,
        progress_callback: Optional[Callable] = None,
        user_name: str = "TestUser",
    ) -> List[Dict]:
        """Execute comprehensive evaluation across characters and scenarios with session support"""

        # Default to all scenarios if not specified
        if scenarios is None or scenarios == ["all"]:
            scenarios = [s[0] for s in self.scenarios.list_scenarios()]

        # ALWAYS create/ensure session
        if session_id:
            # Use provided session ID
            session_description = (
                f"Evaluation: {len(characters)} characters, {len(scenarios)} scenarios"
            )
            session_parameters = {
                "characters": characters,
                "scenarios": scenarios,
                "bots_ai": bots_ai,
                "max_workers": max_workers,
            }

            actual_session_id = self.results_manager.start_session(
                session_id, session_description, session_parameters
            )
        else:
            # Auto-create session with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_description = (
                f"Auto-evaluation: {len(characters)} chars, {len(scenarios)} scenarios"
            )
            session_parameters = {
                "characters": characters,
                "scenarios": scenarios,
                "bots_ai": bots_ai,
                "max_workers": max_workers,
                "auto_created": True,
            }

            actual_session_id = self.results_manager.start_session(
                f"eval_{timestamp}", session_description, session_parameters
            )

        # Notify about session creation
        if progress_callback:
            progress_callback(
                0,
                len(characters) * len(scenarios),
                {
                    "session_created": actual_session_id,
                    "session_paths": self.results_manager.get_session_paths(),
                },
            )

        # Generate all character/scenario combinations
        test_cases = []
        for character_id in characters:
            for scenario_id in scenarios:
                test_cases.append((character_id, scenario_id))

        # Execute multithreaded evaluation with session
        results = self._execute_multithreaded_evaluation(
            test_cases=test_cases,
            bots_ai=bots_ai,
            session_id=actual_session_id,  # Use actual session ID
            max_workers=max_workers,
            progress_callback=progress_callback,
            user_name=user_name,
        )

        # Complete session with summary
        successful_results = [r for r in results if r.get("status") == "completed"]
        session_summary = {
            "total_evaluations": len(results),
            "successful_evaluations": len(successful_results),
            "failed_evaluations": len(results) - len(successful_results),
            "average_score": (
                sum(r["overall_score"] for r in successful_results)
                / len(successful_results)
                if successful_results
                else 0
            ),
            "characters_tested": characters,
            "scenarios_tested": scenarios,
            "provider_used": bots_ai,
            "execution_summary": {
                "total_time": sum(r.get("execution_time", 0) for r in results),
                "average_time_per_evaluation": (
                    sum(r.get("execution_time", 0) for r in results) / len(results)
                    if results
                    else 0
                ),
            },
        }

        self.results_manager.complete_session(actual_session_id, session_summary)

        # Add session info to results
        for result in results:
            result["session_id"] = actual_session_id

        return results

    def _execute_multithreaded_evaluation(
        self,
        test_cases: List[tuple],
        bots_ai: str,
        session_id: Optional[str],
        max_workers: int,
        progress_callback: Optional[Callable],
        user_name: str,
    ) -> List[Dict]:
        """Execute evaluations using thread pool"""

        results = []

        with ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="CharEval"
        ) as executor:
            # Submit all evaluation tasks
            future_to_case = {
                executor.submit(
                    self._evaluate_character_scenario,
                    character_id,
                    scenario_id,
                    bots_ai,
                    session_id,
                    user_name,
                ): (character_id, scenario_id)
                for character_id, scenario_id in test_cases
            }

            # Collect results as they complete
            completed_count = 0
            for future in as_completed(future_to_case):
                character_id, scenario_id = future_to_case[future]

                try:
                    result = future.result()
                    results.append(result)
                    completed_count += 1

                    # Progress callback
                    if progress_callback:
                        progress_callback(completed_count, len(test_cases), result)

                except Exception as e:
                    error_result = {
                        "character_id": character_id,
                        "scenario_id": scenario_id,
                        "status": "failed",
                        "error": f"Thread exception: {e}",
                        "execution_time": 0,
                    }
                    results.append(error_result)
                    completed_count += 1

                    if progress_callback:
                        progress_callback(
                            completed_count, len(test_cases), error_result
                        )

        return results

    def _evaluate_character_scenario(
        self,
        character_id: str,
        scenario_id: str,
        bots_ai: str,
        session_id: Optional[str],
        user_name: str,
    ) -> Dict:
        """Evaluate a single character/scenario combination - thread-safe"""

        thread_name = f"{character_id}/{scenario_id}"
        start_time = time.time()

        try:
            # Get character and scenario data
            character_data = self.character_manager.get_character(character_id)
            scenario_data = self.scenarios.get_scenario(scenario_id)

            if not character_data or not scenario_data:
                return {
                    "character_id": character_id,
                    "scenario_id": scenario_id,
                    "status": "failed",
                    "error": "Missing character or scenario data",
                    "execution_time": time.time() - start_time,
                }

            # Generate conversation
            conversation = self.conversation_generator.generate(
                character_data=character_data,
                scenario_data=scenario_data,
                chatbot_provider=bots_ai,
                user_name=user_name,
            )

            # Generate conversation ID for session
            conversation_id = f"{session_id}_{character_id}_{scenario_id}_{bots_ai}"
            conversation.set_conversation_id(conversation_id)

            # Validate conversation
            is_valid, validation_issues = conversation.validate_for_evaluation()
            if not is_valid:
                return {
                    "character_id": character_id,
                    "scenario_id": scenario_id,
                    "status": "failed",
                    "error": f"Conversation validation failed: {validation_issues}",
                    "execution_time": time.time() - start_time,
                }

            # Store conversation using session (session always required now)
            conversation_messages = conversation.get_evaluation_format()
            conversation_metadata = conversation.get_conversation_metadata()

            self.results_manager.store_conversation(
                conversation_id,
                character_id,
                scenario_id,
                bots_ai,
                conversation_messages,
                conversation_metadata,
                session_id,
            )

            # Evaluate with DeepSeek Reasoner
            evaluation_results = self.evaluator.evaluate_conversation_sync(
                conversation_messages,
                character_data,
                scenario_data,
                ["deepseek_reasoner"],
            )

            if not evaluation_results:
                return {
                    "character_id": character_id,
                    "scenario_id": scenario_id,
                    "conversation_id": conversation_id,
                    "status": "evaluation_failed",
                    "error": "No evaluation results received",
                    "execution_time": time.time() - start_time,
                }

            # Process evaluation results
            deepseek_result = evaluation_results["deepseek_reasoner"]

            # Create consensus analysis (single evaluator)
            consensus = ConsensusAnalysis(
                consensus_scores=deepseek_result.scores,
                overall_consensus=deepseek_result.overall_score,
                agreement_level=1.0,
                disagreements=[],
                confidence_level=deepseek_result.confidence,
                outlier_evaluations=[],
                actionable_insights=[],
            )

            # Store evaluation results using session (session always required now)
            self.results_manager.store_evaluation_results(
                conversation_id, evaluation_results, consensus, session_id
            )

            execution_time = time.time() - start_time

            return {
                "character_id": character_id,
                "scenario_id": scenario_id,
                "conversation_id": conversation_id,
                "overall_score": consensus.overall_consensus,
                "scores": deepseek_result.scores,
                "agreement_level": consensus.agreement_level,
                "confidence": deepseek_result.confidence,
                "evaluator_count": len(evaluation_results),
                "evaluators_used": list(evaluation_results.keys()),
                "status": "completed",
                "execution_time": execution_time,
                "character_name": character_data["name"],
                "scenario_name": scenario_data["name"],
                "provider": bots_ai,
                # Keep references for detailed analysis
                "consensus": consensus,
                "evaluation_results": evaluation_results,
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "character_id": character_id,
                "scenario_id": scenario_id,
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time,
            }

    def compare_providers(
        self,
        character_id: str,
        scenario_id: str,
        providers: List[str],
        session_id: Optional[str] = None,
        user_name: str = "TestUser",
    ) -> Dict:
        """Compare different providers for the same character/scenario combination"""

        comparison_results = {}

        for provider in providers:
            result = self._evaluate_character_scenario(
                character_id, scenario_id, provider, session_id, user_name
            )
            comparison_results[provider] = result

        # Calculate comparison metrics
        successful_results = {
            k: v
            for k, v in comparison_results.items()
            if v.get("status") == "completed"
        }

        if len(successful_results) >= 2:
            scores = {
                provider: result["overall_score"]
                for provider, result in successful_results.items()
            }

            best_provider = max(scores.keys(), key=lambda k: scores[k])
            score_difference = max(scores.values()) - min(scores.values())

            comparison_analysis = {
                "character_id": character_id,
                "scenario_id": scenario_id,
                "providers_compared": providers,
                "scores": scores,
                "best_provider": best_provider,
                "score_difference": score_difference,
                "significant_difference": score_difference > 0.5,
                "individual_results": comparison_results,
            }
        else:
            comparison_analysis = {
                "character_id": character_id,
                "scenario_id": scenario_id,
                "providers_compared": providers,
                "error": "Insufficient successful evaluations for comparison",
                "individual_results": comparison_results,
            }

        return comparison_analysis

    def default_progress_callback(self, completed: int, total: int, result: Dict):
        """Default progress callback for console output"""

        with self.output_lock:
            if result.get("status") == "completed":
                score = result.get("overall_score", 0)
                time_taken = result.get("execution_time", 0)
                print(
                    f"✅ {result.get('character_id', 'unknown')}/{result.get('scenario_id', 'unknown')}: {score:.1f}/10 ({time_taken:.1f}s) [{completed}/{total}]"
                )

            else:
                error = result.get("error", "Unknown error")
                print(
                    f"❌ {result.get('character_id', 'unknown')}/{result.get('scenario_id', 'unknown')}: {error} [{completed}/{total}]"
                )

    def get_pipeline_stats(self) -> Dict:
        """Get statistics about the evaluation pipeline configuration"""

        return {
            "available_characters": len(self.character_manager.list_characters()),
            "available_scenarios": len(self.scenarios.list_scenarios()),
            "available_chat_providers": self.ai_handler.get_chat_providers(),
            "available_evaluation_providers": self.ai_handler.get_evaluation_providers(),
            "default_chat_provider": self.ai_handler.default_chat_provider,
            "default_evaluation_provider": self.ai_handler.default_evaluation_provider,
        }


# Testing function
def test_evaluation_pipeline():
    """Test the evaluation pipeline with a single character/scenario"""

    print("Testing Evaluation Pipeline...")

    # This would normally be called from the CLI
    # Just showing the interface for now
    print("✓ Evaluation Pipeline module ready for CLI integration")


if __name__ == "__main__":
    test_evaluation_pipeline()
