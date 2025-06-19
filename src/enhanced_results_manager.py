"""
Enhanced Results Manager - Session-Only Version

Always uses session-based storage, removes legacy storage methods.
Includes enhanced error logging for DeepSeek responses.
Removes redundant reasoning_analysis directory.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict, is_dataclass
import statistics
import csv

from session_manager import SessionManager


class EnhancedResultsManager:
    """Enhanced manager - Session-only storage with better error logging"""

    def __init__(self, base_dir: str = "evaluation_results"):
        # Initialize session manager (primary storage)
        self.session_manager = SessionManager(base_dir)
        self.current_session_id = None

        # Base directory for logging
        self.base_dir = base_dir
        self.logs_dir = os.path.join(base_dir, "logs")

        # Ensure logging directory exists
        os.makedirs(self.logs_dir, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for evaluation operations"""
        self.log_file = os.path.join(self.logs_dir, "evaluation_log.txt")
        self.error_log_file = os.path.join(self.logs_dir, "error_log.txt")

        # Create log files if they don't exist
        for log_file in [self.log_file, self.error_log_file]:
            if not os.path.exists(log_file):
                with open(log_file, "w") as f:
                    f.write(
                        f"Enhanced Evaluation System Log - Created {datetime.now().isoformat()}\n"
                    )
                    f.write("=" * 60 + "\n\n")

    def _serialize_datetime_objects(self, data: Any) -> Any:
        """Recursively convert datetime objects and dataclasses to serializable format"""
        if isinstance(data, datetime):
            return data.isoformat()
        elif is_dataclass(data):
            return self._serialize_datetime_objects(asdict(data))
        elif isinstance(data, dict):
            return {
                key: self._serialize_datetime_objects(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._serialize_datetime_objects(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(self._serialize_datetime_objects(item) for item in data)
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

    def log_error(self, error_type: str, details: str, context: Optional[Dict] = None):
        """Log detailed error information for debugging"""
        timestamp = datetime.now().isoformat()

        error_entry = f"[{timestamp}] ERROR: {error_type}\n"
        error_entry += f"Details: {details}\n"

        if context:
            error_entry += "Context:\n"
            for key, value in context.items():
                # Truncate very long values for readability
                if isinstance(value, str) and len(value) > 1000:
                    value = value[:1000] + "... [TRUNCATED]"
                error_entry += f"  {key}: {value}\n"

        error_entry += "-" * 60 + "\n\n"

        with open(self.error_log_file, "a") as f:
            f.write(error_entry)

    def start_session(
        self,
        session_id: Optional[str] = None,
        description: str = "",
        parameters: Optional[Dict] = None,
    ) -> str:
        """Start new evaluation session (always required)"""
        self.current_session_id = self.session_manager.create_session(
            session_id, description, parameters
        )

        self.log_operation(
            "START_SESSION",
            f"Started session: {self.current_session_id} - {description}",
        )

        return self.current_session_id

    def ensure_session(self) -> str:
        """Ensure there's an active session, create one if needed"""
        if not self.current_session_id:
            self.current_session_id = self.start_session(
                description="Auto-created session", parameters={"auto_created": True}
            )
        return self.current_session_id

    def store_conversation(
        self,
        conversation_id: str,
        character_id: str,
        scenario_id: str,
        provider: str,
        messages: List[Dict],
        metadata: Optional[Dict] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Store conversation with session support (session always required)"""

        # Use provided session or ensure we have one
        if session_id:
            target_session = session_id
        else:
            target_session = self.ensure_session()

        # Get session paths
        paths = self.session_manager.get_session_paths(target_session)

        conversation_data = {
            "conversation_id": conversation_id,
            "character_id": character_id,
            "scenario_id": scenario_id,
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "metadata": metadata or {},
            "session_id": target_session,
            "stats": {
                "message_count": len(messages),
                "total_length": sum(len(msg.get("content", "")) for msg in messages),
                "user_messages": len([m for m in messages if m.get("role") == "user"]),
                "assistant_messages": len(
                    [m for m in messages if m.get("role") == "assistant"]
                ),
            },
        }

        # Serialize datetime objects and dataclasses
        serializable_data = self._serialize_datetime_objects(conversation_data)

        # Generate clean filename
        filename = self.session_manager.generate_clean_filename(
            character_id, scenario_id, "json"
        )

        filepath = os.path.join(paths["conversations"], filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        # Update session activity
        self.session_manager.update_session_activity(target_session)

        self.log_operation(
            "STORE_CONVERSATION",
            f"ID: {conversation_id}, Character: {character_id}, Scenario: {scenario_id}, Session: {target_session}, File: {filename}",
        )

        return filepath

    def store_evaluation_results(
        self,
        conversation_id: str,
        evaluation_results: Dict,
        consensus_analysis,
        session_id: Optional[str] = None,
    ) -> str:
        """Store evaluation results with enhanced error logging"""

        # Use provided session or ensure we have one
        if session_id:
            target_session = session_id
        else:
            target_session = self.ensure_session()

        # Get session paths
        paths = self.session_manager.get_session_paths(target_session)

        # Convert evaluation results to dict format
        evaluations_dict = {}
        detailed_logs = {}

        for provider, result in evaluation_results.items():
            # Basic evaluation data
            evaluations_dict[provider] = {
                "evaluator": result.evaluator,
                "timestamp": result.timestamp,
                "scores": result.scores,
                "reasoning": result.reasoning,
                "overall_score": result.overall_score,
                "confidence": result.confidence,
                "response_time": getattr(result, "response_time", None),
            }

            # Enhanced logging data - store full response for debugging
            detailed_logs[provider] = {
                "full_raw_response": result.raw_response,  # Complete response for debugging
                "reasoning_content": getattr(result, "reasoning_content", None),
                "thinking_content": getattr(result, "thinking_content", None),
                "token_usage": getattr(result, "token_usage", None),
                "model_metadata": getattr(result, "model_metadata", None),
                "response_time": getattr(result, "response_time", None),
                "evaluation_context": {
                    "conversation_id": conversation_id,
                    "session_id": target_session,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        # Convert consensus analysis to dict
        consensus_dict = (
            asdict(consensus_analysis)
            if is_dataclass(consensus_analysis)
            else consensus_analysis
        )

        # Main evaluation data
        evaluation_data = {
            "evaluation_id": f"{conversation_id}_eval",
            "conversation_id": conversation_id,
            "session_id": target_session,
            "timestamp": datetime.now().isoformat(),
            "evaluations": evaluations_dict,
            "consensus": consensus_dict,
            "meta": {
                "evaluator_count": len(evaluation_results),
                "criteria_evaluated": (
                    list(consensus_analysis.consensus_scores.keys())
                    if hasattr(consensus_analysis, "consensus_scores")
                    else []
                ),
                "total_tokens_used": sum(
                    (
                        getattr(result, "token_usage", {}).get("total_tokens", 0)
                        if getattr(result, "token_usage", None)
                        else 0
                    )
                    for result in evaluation_results.values()
                ),
                "total_response_time": sum(
                    getattr(result, "response_time", 0) or 0
                    for result in evaluation_results.values()
                ),
            },
        }

        # Serialize datetime objects and dataclasses
        serializable_data = self._serialize_datetime_objects(evaluation_data)
        detailed_logs_serializable = self._serialize_datetime_objects(detailed_logs)

        # Generate clean filenames from conversation_id
        parts = conversation_id.replace(f"{target_session}_", "").split("_")
        if len(parts) >= 2:
            character_id = parts[0]
            scenario_id = parts[1]
        else:
            character_id = "unknown"
            scenario_id = "unknown"

        eval_filename = self.session_manager.generate_clean_filename(
            character_id, scenario_id, "json"
        )
        detailed_filename = f"{character_id}_{scenario_id}_detailed.json"

        # Store main evaluation results
        eval_filepath = os.path.join(paths["evaluations"], eval_filename)
        with open(eval_filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        # Store detailed logs with full responses
        detailed_filepath = os.path.join(paths["detailed_logs"], detailed_filename)
        with open(detailed_filepath, "w", encoding="utf-8") as f:
            json.dump(detailed_logs_serializable, f, indent=2, ensure_ascii=False)

        # Update session activity
        self.session_manager.update_session_activity(target_session)

        self.log_operation(
            "STORE_EVALUATION",
            f"Conversation: {conversation_id}, Session: {target_session}, Evaluators: {len(evaluation_results)}, Files: {eval_filename}, {detailed_filename}",
        )

        return eval_filepath

    def log_evaluation_error(
        self,
        provider: str,
        raw_response: str,
        error_message: str,
        conversation_id: str,
        parsing_context: Optional[Dict] = None,
    ):
        """Log detailed evaluation parsing errors with full context"""

        error_context = {
            "provider": provider,
            "conversation_id": conversation_id,
            "session_id": self.current_session_id,
            "error_message": error_message,
            "raw_response_length": len(raw_response),
            "raw_response_preview": (
                raw_response[:500] + "..." if len(raw_response) > 500 else raw_response
            ),
            "full_raw_response": raw_response,  # Complete response for debugging
        }

        if parsing_context:
            error_context.update(parsing_context)

        self.log_error(
            "EVALUATION_PARSING_ERROR",
            f"Failed to parse {provider} evaluation response for {conversation_id}",
            error_context,
        )

        # Also save error to session for easy access
        if self.current_session_id:
            try:
                paths = self.session_manager.get_session_paths(self.current_session_id)
                error_filename = f"error_{provider}_{conversation_id}_{datetime.now().strftime('%H%M%S')}.json"
                error_filepath = os.path.join(paths["detailed_logs"], error_filename)

                with open(error_filepath, "w", encoding="utf-8") as f:
                    json.dump(
                        self._serialize_datetime_objects(error_context),
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )

            except Exception as e:
                # Don't fail the main operation if error logging fails
                print(f"⚠️ Could not save error log to session: {e}")

    def save_analysis_report(
        self, report_data: Dict, filename: str, session_id: Optional[str] = None
    ) -> str:
        """Save analysis report to session"""

        # Use provided session or ensure we have one
        if session_id:
            target_session = session_id
        else:
            target_session = self.ensure_session()

        paths = self.session_manager.get_session_paths(target_session)
        filepath = os.path.join(paths["analysis"], filename)

        # Serialize datetime objects and dataclasses
        try:
            serializable_data = self._serialize_datetime_objects(report_data)
        except Exception as e:
            # Log error and use fallback
            self.log_error(
                "ANALYSIS_SERIALIZATION_ERROR", str(e), {"filename": filename}
            )
            serializable_data = self._clean_report_data_for_json(report_data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        # Update session activity
        self.session_manager.update_session_activity(target_session)

        self.log_operation(
            "SAVE_ANALYSIS",
            f"Saved analysis report: {filename}, Session: {target_session}",
        )

        return filepath

    def _clean_report_data_for_json(self, report_data: Dict) -> Dict:
        """Fallback method to clean report data for JSON serialization"""
        cleaned_data = {}

        for key, value in report_data.items():
            try:
                json.dumps(value, default=str)
                cleaned_data[key] = value
            except (TypeError, ValueError):
                if isinstance(value, list):
                    cleaned_list = []
                    for item in value:
                        if is_dataclass(item):
                            cleaned_list.append(asdict(item))
                        elif hasattr(item, "__dict__"):
                            cleaned_list.append(vars(item))
                        else:
                            cleaned_list.append(str(item))
                    cleaned_data[key] = cleaned_list
                elif is_dataclass(value):
                    cleaned_data[key] = asdict(value)
                elif hasattr(value, "__dict__"):
                    cleaned_data[key] = vars(value)
                else:
                    cleaned_data[key] = str(value)

        return cleaned_data

    def complete_session(
        self, session_id: Optional[str] = None, summary: Optional[Dict] = None
    ):
        """Complete evaluation session"""

        if session_id is None:
            session_id = self.current_session_id

        if session_id:
            self.session_manager.complete_session(session_id, summary)

            if session_id == self.current_session_id:
                self.current_session_id = None

            self.log_operation("COMPLETE_SESSION", f"Completed session: {session_id}")

    def get_current_session_info(self) -> Optional[Dict]:
        """Get information about current session"""
        if self.current_session_id:
            return self.session_manager.get_session_info(self.current_session_id)
        return None

    def get_session_paths(self, session_id: Optional[str] = None) -> Dict[str, str]:
        """Get session directory paths"""
        if session_id is None:
            session_id = self.current_session_id

        if not session_id:
            raise ValueError("No active session")

        return self.session_manager.get_session_paths(session_id)

    # Utility methods for data access
    def load_conversation(
        self, character_id: str, scenario_id: str, session_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Load conversation data by character/scenario from session"""
        if session_id is None:
            session_id = self.current_session_id

        if not session_id:
            return None

        paths = self.session_manager.get_session_paths(session_id)
        filename = self.session_manager.generate_clean_filename(
            character_id, scenario_id, "json"
        )
        filepath = os.path.join(paths["conversations"], filename)

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def load_evaluation(
        self, character_id: str, scenario_id: str, session_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Load evaluation results by character/scenario from session"""
        if session_id is None:
            session_id = self.current_session_id

        if not session_id:
            return None

        paths = self.session_manager.get_session_paths(session_id)
        filename = self.session_manager.generate_clean_filename(
            character_id, scenario_id, "json"
        )
        filepath = os.path.join(paths["evaluations"], filename)

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def export_session_to_csv(
        self, session_id: Optional[str] = None, output_filename: Optional[str] = None
    ) -> str:
        """Export session results to CSV"""
        if session_id is None:
            session_id = self.current_session_id

        if not session_id:
            raise ValueError("No session specified")

        paths = self.session_manager.get_session_paths(session_id)

        # Generate output filename if not provided
        if output_filename is None:
            output_filename = f"{session_id}_results.csv"

        output_path = os.path.join(paths["exports"], output_filename)

        # Collect evaluation data from session
        evaluations_dir = paths["evaluations"]
        csv_data = []

        if os.path.exists(evaluations_dir):
            for filename in os.listdir(evaluations_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(evaluations_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        eval_data = json.load(f)

                    # Extract data for CSV
                    consensus = eval_data.get("consensus", {})
                    meta = eval_data.get("meta", {})

                    # Parse character/scenario from filename
                    base_name = filename[:-5]  # Remove .json
                    parts = base_name.split("_")
                    character_id = parts[0] if len(parts) > 0 else "unknown"
                    scenario_id = "_".join(parts[1:]) if len(parts) > 1 else "unknown"

                    row = {
                        "session_id": session_id,
                        "character_id": character_id,
                        "scenario_id": scenario_id,
                        "timestamp": eval_data.get("timestamp", ""),
                        "overall_consensus": consensus.get("overall_consensus", 0),
                        "agreement_level": consensus.get("agreement_level", 0),
                        "confidence_level": consensus.get("confidence_level", 0),
                        "total_tokens": meta.get("total_tokens_used", 0),
                        "total_response_time": meta.get("total_response_time", 0),
                        "evaluator_count": meta.get("evaluator_count", 0),
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
            "EXPORT_CSV", f"Exported session {session_id} to {output_filename}"
        )

        return output_path
