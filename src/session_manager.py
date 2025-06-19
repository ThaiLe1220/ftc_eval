"""
Session Manager - Organized session-based file management

Replaces timestamp-suffix chaos with logical session directories.
Provides clean file organization and session tracking for CLI workflow.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


class SessionManager:
    """Manages evaluation sessions with organized directory structure"""

    def __init__(self, base_dir: str = "evaluation_results"):
        self.base_dir = base_dir
        self.sessions_index_file = os.path.join(base_dir, "sessions_index.json")

        # Ensure base directory exists
        os.makedirs(base_dir, exist_ok=True)

        # Load or create sessions index
        self.sessions_index = self._load_sessions_index()

    def _load_sessions_index(self) -> Dict:
        """Load existing sessions index or create new one"""
        if os.path.exists(self.sessions_index_file):
            try:
                with open(self.sessions_index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Create new index if file is corrupted
                return {"sessions": {}, "created": datetime.now().isoformat()}
        else:
            # Create new index
            return {"sessions": {}, "created": datetime.now().isoformat()}

    def _save_sessions_index(self):
        """Save sessions index to file"""
        with open(self.sessions_index_file, "w", encoding="utf-8") as f:
            json.dump(self.sessions_index, f, indent=2, ensure_ascii=False)

    def create_session(
        self,
        session_id: Optional[str] = None,
        description: str = "",
        parameters: Optional[Dict] = None,
    ) -> str:
        """Create new evaluation session with organized directory structure"""

        if session_id is None:
            # Generate timestamp-based session ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"session_{timestamp}"

        # Ensure session ID is unique
        original_session_id = session_id
        counter = 1
        while session_id in self.sessions_index["sessions"]:
            session_id = f"{original_session_id}_{counter}"
            counter += 1

        # Create session directory structure
        session_dir = os.path.join(self.base_dir, session_id)
        self._create_session_directories(session_dir)

        # Create session metadata
        session_metadata = {
            "session_id": session_id,
            "created": datetime.now().isoformat(),
            "description": description,
            "parameters": parameters or {},
            "status": "active",
            "directory": session_dir,
            "evaluation_count": 0,
            "last_activity": datetime.now().isoformat(),
        }

        # Add to sessions index
        self.sessions_index["sessions"][session_id] = session_metadata
        self._save_sessions_index()

        return session_id

    def _create_session_directories(self, session_dir: str):
        """Create organized directory structure for session"""
        directories = [
            session_dir,
            os.path.join(session_dir, "conversations"),
            os.path.join(session_dir, "evaluations"),
            os.path.join(session_dir, "analysis"),
            os.path.join(session_dir, "detailed_logs"),
            os.path.join(session_dir, "exports"),
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_session_paths(self, session_id: str) -> Dict[str, str]:
        """Get all directory paths for a session"""
        if session_id not in self.sessions_index["sessions"]:
            raise ValueError(f"Session '{session_id}' not found")

        session_dir = self.sessions_index["sessions"][session_id]["directory"]

        return {
            "base": session_dir,
            "conversations": os.path.join(session_dir, "conversations"),
            "evaluations": os.path.join(session_dir, "evaluations"),
            "analysis": os.path.join(session_dir, "analysis"),
            "detailed_logs": os.path.join(session_dir, "detailed_logs"),
            "exports": os.path.join(session_dir, "exports"),
        }

    def update_session_activity(
        self, session_id: str, activity_info: Optional[Dict] = None
    ):
        """Update session's last activity timestamp and optional info"""
        if session_id in self.sessions_index["sessions"]:
            self.sessions_index["sessions"][session_id][
                "last_activity"
            ] = datetime.now().isoformat()

            if activity_info:
                # Update evaluation count if provided
                if "evaluation_count" in activity_info:
                    self.sessions_index["sessions"][session_id]["evaluation_count"] = (
                        activity_info["evaluation_count"]
                    )

                # Add any additional activity info
                if "additional_info" not in self.sessions_index["sessions"][session_id]:
                    self.sessions_index["sessions"][session_id]["additional_info"] = {}

                for key, value in activity_info.items():
                    if key != "evaluation_count":
                        self.sessions_index["sessions"][session_id]["additional_info"][
                            key
                        ] = value

            self._save_sessions_index()

    def complete_session(self, session_id: str, summary: Optional[Dict] = None):
        """Mark session as completed with optional summary"""
        if session_id in self.sessions_index["sessions"]:
            self.sessions_index["sessions"][session_id]["status"] = "completed"
            self.sessions_index["sessions"][session_id][
                "completed"
            ] = datetime.now().isoformat()

            if summary:
                self.sessions_index["sessions"][session_id]["summary"] = summary

            self._save_sessions_index()

    def list_sessions(
        self, status_filter: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict]:
        """List sessions with optional filtering"""
        sessions = list(self.sessions_index["sessions"].values())

        # Filter by status if specified
        if status_filter:
            sessions = [s for s in sessions if s.get("status") == status_filter]

        # Sort by creation date (newest first)
        sessions.sort(key=lambda x: x["created"], reverse=True)

        # Limit results if specified
        if limit:
            sessions = sessions[:limit]

        return sessions

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get detailed information about a specific session"""
        return self.sessions_index["sessions"].get(session_id)

    def delete_session(self, session_id: str, remove_files: bool = False) -> bool:
        """Delete session from index and optionally remove files"""
        if session_id not in self.sessions_index["sessions"]:
            return False

        session_info = self.sessions_index["sessions"][session_id]

        # Remove files if requested
        if remove_files:
            import shutil

            session_dir = session_info["directory"]
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)

        # Remove from index
        del self.sessions_index["sessions"][session_id]
        self._save_sessions_index()

        return True

    def cleanup_old_sessions(
        self, days_old: int = 30, keep_completed: bool = True
    ) -> int:
        """Clean up old sessions (older than specified days)"""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days_old)
        sessions_to_remove = []

        for session_id, session_info in self.sessions_index["sessions"].items():
            session_date = datetime.fromisoformat(session_info["created"])

            # Skip if within cutoff date
            if session_date > cutoff_date:
                continue

            # Skip completed sessions if keep_completed is True
            if keep_completed and session_info.get("status") == "completed":
                continue

            sessions_to_remove.append(session_id)

        # Remove old sessions
        removed_count = 0
        for session_id in sessions_to_remove:
            if self.delete_session(session_id, remove_files=True):
                removed_count += 1

        return removed_count

    def generate_clean_filename(
        self, character_id: str, scenario_id: str, file_type: str
    ) -> str:
        """Generate clean filename without timestamp suffixes"""
        return f"{character_id}_{scenario_id}.{file_type}"

    def get_session_stats(self) -> Dict:
        """Get statistics about all sessions"""
        total_sessions = len(self.sessions_index["sessions"])
        active_sessions = len(
            [
                s
                for s in self.sessions_index["sessions"].values()
                if s.get("status") == "active"
            ]
        )
        completed_sessions = len(
            [
                s
                for s in self.sessions_index["sessions"].values()
                if s.get("status") == "completed"
            ]
        )

        total_evaluations = sum(
            s.get("evaluation_count", 0)
            for s in self.sessions_index["sessions"].values()
        )

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "total_evaluations": total_evaluations,
            "sessions_index_path": self.sessions_index_file,
        }

    def export_session_summary(self, output_path: str) -> str:
        """Export summary of all sessions to JSON file"""
        summary_data = {
            "export_date": datetime.now().isoformat(),
            "stats": self.get_session_stats(),
            "sessions": self.list_sessions(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        return output_path


# Integration helper for EnhancedResultsManager
class SessionAwareResultsManager:
    """Wrapper to integrate SessionManager with EnhancedResultsManager"""

    def __init__(self, base_dir: str = "evaluation_results"):
        self.session_manager = SessionManager(base_dir)
        self.current_session_id = None

    def start_evaluation_session(
        self,
        session_id: Optional[str] = None,
        description: str = "",
        parameters: Optional[Dict] = None,
    ) -> str:
        """Start new evaluation session"""
        self.current_session_id = self.session_manager.create_session(
            session_id, description, parameters
        )
        return self.current_session_id

    def get_current_session_paths(self) -> Dict[str, str]:
        """Get paths for current session"""
        if not self.current_session_id:
            raise ValueError("No active session")
        return self.session_manager.get_session_paths(self.current_session_id)

    def update_evaluation_progress(self, completed_evaluations: int):
        """Update current session with evaluation progress"""
        if self.current_session_id:
            self.session_manager.update_session_activity(
                self.current_session_id, {"evaluation_count": completed_evaluations}
            )

    def complete_current_session(self, summary: Optional[Dict] = None):
        """Complete current session"""
        if self.current_session_id:
            self.session_manager.complete_session(self.current_session_id, summary)
            self.current_session_id = None


# Testing function
def test_session_manager():
    """Test session manager functionality"""
    print("Testing Session Manager...")

    # Create test session manager
    manager = SessionManager("test_sessions")

    # Create session
    session_id = manager.create_session(
        description="Test session",
        parameters={"characters": ["marco"], "scenarios": ["seeking_guidance"]},
    )
    print(f"✓ Created session: {session_id}")

    # Get session paths
    paths = manager.get_session_paths(session_id)
    print(f"✓ Session paths: {list(paths.keys())}")

    # Update activity
    manager.update_session_activity(session_id, {"evaluation_count": 1})
    print("✓ Updated session activity")

    # List sessions
    sessions = manager.list_sessions()
    print(f"✓ Found {len(sessions)} sessions")

    # Get stats
    stats = manager.get_session_stats()
    print(f"✓ Session stats: {stats['total_sessions']} total")

    print("✅ Session Manager test completed")


if __name__ == "__main__":
    test_session_manager()
