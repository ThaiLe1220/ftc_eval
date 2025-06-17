"""
Results Manager - Data Storage and Basic Analysis

This module handles storage, retrieval, and preliminary analysis of evaluation results.
It provides the data infrastructure for the character evaluation system.

Core functionality:
- Store conversation data and evaluation results
- Generate unique IDs and organize data files
- Perform basic analysis and consensus calculations
- Export data in multiple formats
- Track evaluation system reliability
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
import statistics
import csv

from ai_evaluator import EvaluationResult, ConsensusAnalysis


class ResultsManager:
    """Manage storage and analysis of evaluation results"""

    def __init__(self, base_dir: str = "evaluation_results"):
        self.base_dir = base_dir
        self.conversations_dir = os.path.join(base_dir, "conversations")
        self.evaluations_dir = os.path.join(base_dir, "evaluations")
        self.analysis_dir = os.path.join(base_dir, "analysis")
        self.logs_dir = os.path.join(base_dir, "logs")
        self.exports_dir = os.path.join(base_dir, "exports")

        self._ensure_directories()
        self._setup_logging()

    def _ensure_directories(self):
        """Create directory structure if it doesn't exist"""
        directories = [
            self.base_dir,
            self.conversations_dir,
            self.evaluations_dir,
            self.analysis_dir,
            self.logs_dir,
            self.exports_dir,
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        print(f"✓ Results directories initialized in {self.base_dir}")

    def _setup_logging(self):
        """Setup logging for evaluation operations"""
        self.log_file = os.path.join(self.logs_dir, "evaluation_log.txt")

        # Create log file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(
                    f"Evaluation System Log - Created {datetime.now().isoformat()}\n"
                )
                f.write("=" * 60 + "\n\n")

    def _serialize_datetime_objects(self, data: Any) -> Any:
        """Recursively convert datetime objects to ISO format strings"""
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {
                key: self._serialize_datetime_objects(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._serialize_datetime_objects(item) for item in data]
        else:
            return data

    def log_operation(self, operation: str, details: str = ""):
        """Log an operation to the log file"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {operation}"
        if details:
            log_entry += f" - {details}"
        log_entry += "\n"

        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def generate_conversation_id(
        self, character_id: str, scenario_id: str, provider: str
    ) -> str:
        """Generate unique conversation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"{character_id}_{scenario_id}_{provider}_{timestamp}_{short_uuid}"

    def store_conversation(
        self,
        conversation_id: str,
        character_id: str,
        scenario_id: str,
        provider: str,
        messages: List[Dict],
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Store conversation data

        Returns the file path where conversation was stored
        """

        conversation_data = {
            "conversation_id": conversation_id,
            "character_id": character_id,
            "scenario_id": scenario_id,
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "metadata": metadata or {},
            "stats": {
                "message_count": len(messages),
                "total_length": sum(len(msg.get("content", "")) for msg in messages),
                "user_messages": len([m for m in messages if m.get("role") == "user"]),
                "assistant_messages": len(
                    [m for m in messages if m.get("role") == "assistant"]
                ),
            },
        }

        # Serialize datetime objects
        serializable_data = self._serialize_datetime_objects(conversation_data)

        # Store conversation
        filename = f"{conversation_id}.json"
        filepath = os.path.join(self.conversations_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        self.log_operation(
            "STORE_CONVERSATION",
            f"ID: {conversation_id}, Character: {character_id}, Scenario: {scenario_id}",
        )

        return filepath

    def store_evaluation_results(
        self,
        conversation_id: str,
        evaluation_results: Dict[str, EvaluationResult],
        consensus_analysis: ConsensusAnalysis,
    ) -> str:
        """
        Store evaluation results and consensus analysis

        Returns the file path where evaluation was stored
        """

        # Convert evaluation results to dict format
        evaluations_dict = {}
        for provider, result in evaluation_results.items():
            evaluations_dict[provider] = {
                "evaluator": result.evaluator,
                "timestamp": result.timestamp,
                "scores": result.scores,
                "reasoning": result.reasoning,
                "overall_score": result.overall_score,
                "confidence": result.confidence,
                "raw_response_length": len(result.raw_response),
            }

        # Convert consensus analysis to dict
        consensus_dict = {
            "consensus_scores": consensus_analysis.consensus_scores,
            "overall_consensus": consensus_analysis.overall_consensus,
            "agreement_level": consensus_analysis.agreement_level,
            "disagreements": consensus_analysis.disagreements,
            "confidence_level": consensus_analysis.confidence_level,
            "outlier_evaluations": consensus_analysis.outlier_evaluations,
            "actionable_insights": consensus_analysis.actionable_insights,
        }

        evaluation_data = {
            "evaluation_id": f"{conversation_id}_eval",
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "evaluations": evaluations_dict,
            "consensus": consensus_dict,
            "meta": {
                "evaluator_count": len(evaluation_results),
                "criteria_evaluated": list(consensus_analysis.consensus_scores.keys()),
            },
        }

        # Serialize datetime objects
        serializable_data = self._serialize_datetime_objects(evaluation_data)

        # Store evaluation results
        filename = f"{conversation_id}_eval.json"
        filepath = os.path.join(self.evaluations_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        self.log_operation(
            "STORE_EVALUATION",
            f"Conversation: {conversation_id}, Evaluators: {len(evaluation_results)}, Consensus: {consensus_analysis.overall_consensus:.1f}",
        )

        return filepath

    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Load conversation data by ID"""
        filename = f"{conversation_id}.json"
        filepath = os.path.join(self.conversations_dir, filename)

        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_evaluation(self, conversation_id: str) -> Optional[Dict]:
        """Load evaluation results by conversation ID"""
        filename = f"{conversation_id}_eval.json"
        filepath = os.path.join(self.evaluations_dir, filename)

        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_conversations(
        self, character_id: Optional[str] = None, scenario_id: Optional[str] = None
    ) -> List[str]:
        """List conversation IDs, optionally filtered by character or scenario"""
        conversation_files = [
            f for f in os.listdir(self.conversations_dir) if f.endswith(".json")
        ]
        conversation_ids = [
            f[:-5] for f in conversation_files
        ]  # Remove .json extension

        if character_id or scenario_id:
            filtered_ids = []
            for conv_id in conversation_ids:
                conv_data = self.load_conversation(conv_id)
                if conv_data:
                    if character_id and conv_data.get("character_id") != character_id:
                        continue
                    if scenario_id and conv_data.get("scenario_id") != scenario_id:
                        continue
                    filtered_ids.append(conv_id)
            return filtered_ids

        return conversation_ids

    def get_character_summary(self, character_id: str) -> Dict:
        """Generate performance summary for a specific character"""
        conversation_ids = self.list_conversations(character_id=character_id)

        if not conversation_ids:
            return {
                "character_id": character_id,
                "conversation_count": 0,
                "error": "No conversations found",
            }

        evaluations = []
        scenarios = set()
        providers = set()

        for conv_id in conversation_ids:
            eval_data = self.load_evaluation(conv_id)
            if eval_data and "consensus" in eval_data:
                evaluations.append(eval_data["consensus"])

                # Get conversation metadata
                conv_data = self.load_conversation(conv_id)
                if conv_data:
                    scenarios.add(conv_data.get("scenario_id", "unknown"))
                    providers.add(conv_data.get("provider", "unknown"))

        if not evaluations:
            return {
                "character_id": character_id,
                "conversation_count": len(conversation_ids),
                "error": "No evaluations found",
            }

        # Calculate statistics
        overall_scores = [eval_data["overall_consensus"] for eval_data in evaluations]
        agreement_levels = [eval_data["agreement_level"] for eval_data in evaluations]

        # Calculate criteria averages
        criteria_scores = {}
        criteria_names = evaluations[0]["consensus_scores"].keys()

        for criterion in criteria_names:
            scores = [
                eval_data["consensus_scores"][criterion] for eval_data in evaluations
            ]
            criteria_scores[criterion] = {
                "average": statistics.mean(scores),
                "min": min(scores),
                "max": max(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
            }

        # Collect all insights
        all_insights = []
        for eval_data in evaluations:
            all_insights.extend(eval_data.get("actionable_insights", []))

        summary = {
            "character_id": character_id,
            "conversation_count": len(conversation_ids),
            "evaluation_count": len(evaluations),
            "scenarios_tested": list(scenarios),
            "providers_used": list(providers),
            "performance": {
                "overall_average": statistics.mean(overall_scores),
                "overall_min": min(overall_scores),
                "overall_max": max(overall_scores),
                "overall_std_dev": (
                    statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0
                ),
            },
            "criteria_performance": criteria_scores,
            "agreement_stats": {
                "average_agreement": statistics.mean(agreement_levels),
                "min_agreement": min(agreement_levels),
                "max_agreement": max(agreement_levels),
            },
            "common_insights": list(set(all_insights)),
            "timestamp": datetime.now().isoformat(),
        }

        return summary

    def get_system_overview(self) -> Dict:
        """Generate overview of entire evaluation system"""
        all_conversations = self.list_conversations()

        if not all_conversations:
            return {"error": "No conversations found"}

        characters = set()
        scenarios = set()
        providers = set()
        evaluations_with_data = []

        for conv_id in all_conversations:
            conv_data = self.load_conversation(conv_id)
            eval_data = self.load_evaluation(conv_id)

            if conv_data:
                characters.add(conv_data.get("character_id", "unknown"))
                scenarios.add(conv_data.get("scenario_id", "unknown"))
                providers.add(conv_data.get("provider", "unknown"))

            if eval_data and "consensus" in eval_data:
                evaluations_with_data.append(
                    {
                        "conversation_id": conv_id,
                        "character_id": (
                            conv_data.get("character_id") if conv_data else "unknown"
                        ),
                        "scenario_id": (
                            conv_data.get("scenario_id") if conv_data else "unknown"
                        ),
                        "consensus": eval_data["consensus"],
                    }
                )

        if not evaluations_with_data:
            return {
                "total_conversations": len(all_conversations),
                "characters_tested": list(characters),
                "scenarios_tested": list(scenarios),
                "providers_used": list(providers),
                "error": "No evaluation data found",
            }

        # Calculate overall statistics
        overall_scores = [
            eval_data["consensus"]["overall_consensus"]
            for eval_data in evaluations_with_data
        ]
        agreement_levels = [
            eval_data["consensus"]["agreement_level"]
            for eval_data in evaluations_with_data
        ]

        # Character performance ranking
        character_performances = {}
        for eval_data in evaluations_with_data:
            char_id = eval_data["character_id"]
            score = eval_data["consensus"]["overall_consensus"]

            if char_id not in character_performances:
                character_performances[char_id] = []
            character_performances[char_id].append(score)

        # Calculate character averages and rank
        character_rankings = []
        for char_id, scores in character_performances.items():
            avg_score = statistics.mean(scores)
            character_rankings.append(
                {
                    "character_id": char_id,
                    "average_score": avg_score,
                    "conversation_count": len(scores),
                    "score_range": (min(scores), max(scores)),
                }
            )

        character_rankings.sort(key=lambda x: x["average_score"], reverse=True)

        overview = {
            "system_stats": {
                "total_conversations": len(all_conversations),
                "evaluated_conversations": len(evaluations_with_data),
                "characters_tested": len(characters),
                "scenarios_tested": len(scenarios),
                "providers_used": len(providers),
            },
            "overall_performance": {
                "average_score": statistics.mean(overall_scores),
                "min_score": min(overall_scores),
                "max_score": max(overall_scores),
                "score_std_dev": (
                    statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0
                ),
            },
            "agreement_analysis": {
                "average_agreement": statistics.mean(agreement_levels),
                "min_agreement": min(agreement_levels),
                "max_agreement": max(agreement_levels),
            },
            "character_rankings": character_rankings,
            "coverage": {
                "characters": list(characters),
                "scenarios": list(scenarios),
                "providers": list(providers),
            },
            "timestamp": datetime.now().isoformat(),
        }

        return overview

    def export_to_csv(self, output_path: str) -> str:
        """Export all evaluation data to CSV format"""
        all_conversations = self.list_conversations()

        if not all_conversations:
            raise ValueError("No conversations to export")

        csv_data = []

        for conv_id in all_conversations:
            conv_data = self.load_conversation(conv_id)
            eval_data = self.load_evaluation(conv_id)

            if not conv_data or not eval_data:
                continue

            consensus = eval_data.get("consensus", {})

            row = {
                "conversation_id": conv_id,
                "character_id": conv_data.get("character_id", ""),
                "scenario_id": conv_data.get("scenario_id", ""),
                "provider": conv_data.get("provider", ""),
                "timestamp": conv_data.get("timestamp", ""),
                "message_count": conv_data.get("stats", {}).get("message_count", 0),
                "overall_consensus": consensus.get("overall_consensus", 0),
                "agreement_level": consensus.get("agreement_level", 0),
                "confidence_level": consensus.get("confidence_level", 0),
            }

            # Add individual criteria scores
            consensus_scores = consensus.get("consensus_scores", {})
            for criterion, score in consensus_scores.items():
                row[f"score_{criterion}"] = score

            csv_data.append(row)

        # Write CSV
        if csv_data:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)

        self.log_operation(
            "EXPORT_CSV", f"Exported {len(csv_data)} evaluations to {output_path}"
        )

        return output_path

    def save_analysis_report(self, report_data: Dict, filename: str) -> str:
        """Save analysis report to the analysis directory"""
        filepath = os.path.join(self.analysis_dir, filename)

        # Serialize datetime objects
        serializable_data = self._serialize_datetime_objects(report_data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        self.log_operation("SAVE_ANALYSIS", f"Saved analysis report: {filename}")

        return filepath


# Testing and utility functions
def test_results_manager():
    """Test the results manager functionality"""
    print("Testing Results Manager...")

    # Initialize
    manager = ResultsManager("test_evaluation_results")

    # Test conversation storage
    test_conversation = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]

    conv_id = manager.generate_conversation_id("marco", "seeking_guidance", "claude")
    print(f"Generated conversation ID: {conv_id}")

    # Store conversation
    conv_path = manager.store_conversation(
        conv_id,
        "marco",
        "seeking_guidance",
        "claude",
        test_conversation,
        {"test": True},
    )
    print(f"Stored conversation: {conv_path}")

    # Load conversation
    loaded_conv = manager.load_conversation(conv_id)
    print(f"Loaded conversation: {loaded_conv['conversation_id']}")

    print("✓ Results Manager test completed")


if __name__ == "__main__":
    test_results_manager()
