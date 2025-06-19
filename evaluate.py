#!/usr/bin/env python3
"""
Character Evaluation CLI - Phase 2 Implementation

Main developer interface for character evaluation with provider selection,
session management, and clean output formatting.

Usage:
    python evaluate.py --bots_ai claude                    # Default 4 characters
    python evaluate.py --char marco --bots_ai gpt          # Single character
    python evaluate.py --char marco,lysandra --scenarios seeking_guidance,emotional_support
    python evaluate.py --bots_ai gpt --char marco --scenarios emotional_support

"""

import sys
import os
import argparse
import time
from datetime import datetime
from typing import List, Optional, Dict

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from character_manager import CharacterManager
from test_scenarios import TestScenarios
from ai_handler import AIHandler
from enhanced_results_manager import EnhancedResultsManager
from evaluation_pipeline import EvaluationPipeline


def parse_arguments() -> argparse.Namespace:
    """Parse and validate CLI arguments"""
    parser = argparse.ArgumentParser(
        description="Character Evaluation CLI - Automated character testing with provider selection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python evaluate.py --bots_ai claude                    # Default 4 characters with Claude
    python evaluate.py --char marco --bots_ai gpt          # Single character with GPT
    python evaluate.py --char marco,lysandra --scenarios seeking_guidance
    python evaluate.py --char all --bots_ai claude --output json
    python evaluate.py --session my_test_session --char marco --scenarios all
        """,
    )

    # Primary configuration parameters
    parser.add_argument(
        "--char",
        "--characters",
        default="marco,lysandra,dorian,juniper",
        help="Characters to evaluate (comma-separated). Use 'all' for all characters. Default: marco,lysandra,dorian,juniper",
    )

    parser.add_argument(
        "--scenarios",
        default="all",
        help="Scenarios to test (comma-separated). Use 'all' for all scenarios. Default: all",
    )

    parser.add_argument(
        "--bots_ai",
        "--provider",
        choices=["claude", "gpt"],
        default="claude",
        help="AI provider for character responses. Default: claude",
    )

    # Output and session management
    parser.add_argument(
        "--output",
        choices=["console", "json", "csv"],
        default="console",
        help="Output format. Default: console",
    )

    parser.add_argument(
        "--session", help="Custom session ID for organized file management"
    )

    # Advanced options
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of parallel threads for evaluation. Default: 4",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output, show only results",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with detailed progress",
    )

    return parser.parse_args()


def validate_arguments(
    args: argparse.Namespace,
    character_manager: CharacterManager,
    scenarios: TestScenarios,
) -> bool:
    """Validate CLI arguments against available characters and scenarios"""

    # Validate characters
    available_characters = [char[0] for char in character_manager.list_characters()]

    if args.char == "all":
        selected_characters = available_characters
    else:
        selected_characters = [c.strip() for c in args.char.split(",")]

    invalid_characters = [
        c for c in selected_characters if c not in available_characters
    ]
    if invalid_characters:
        print(f"❌ Invalid characters: {', '.join(invalid_characters)}")
        print(f"📋 Available characters: {', '.join(available_characters)}")
        return False

    # Validate scenarios
    available_scenarios = [s[0] for s in scenarios.list_scenarios()]

    if args.scenarios == "all":
        selected_scenarios = available_scenarios
    else:
        selected_scenarios = [s.strip() for s in args.scenarios.split(",")]

    invalid_scenarios = [s for s in selected_scenarios if s not in available_scenarios]
    if invalid_scenarios:
        print(f"❌ Invalid scenarios: {', '.join(invalid_scenarios)}")
        print(f"📋 Available scenarios: {', '.join(available_scenarios)}")
        return False

    # Store validated selections in args
    args.selected_characters = selected_characters
    args.selected_scenarios = selected_scenarios

    return True


def display_configuration(args: argparse.Namespace, ai_handler: AIHandler):
    """Display evaluation configuration"""

    if args.quiet:
        return

    print("🎭 Character Evaluation CLI")
    print("=" * 50)

    print(f"📋 Configuration:")
    print(
        f"  • Characters: {', '.join(args.selected_characters)} ({len(args.selected_characters)} total)"
    )
    print(
        f"  • Scenarios: {', '.join(args.selected_scenarios)} ({len(args.selected_scenarios)} total)"
    )
    print(f"  • Character AI: {args.bots_ai}")
    print(f"  • Evaluation AI: DeepSeek Reasoner (fixed)")
    print(f"  • User AI: GPT-4.1 (fixed)")
    print(f"  • Threads: {args.threads}")
    print(
        f"  • Total evaluations: {len(args.selected_characters) * len(args.selected_scenarios)}"
    )

    if args.session:
        print(f"  • Session: {args.session}")

    print()


def display_results(
    results: List[Dict], args: argparse.Namespace, execution_time: float
):
    """Display evaluation results in requested format"""

    successful_results = [r for r in results if r.get("status") == "completed"]
    failed_results = [r for r in results if r.get("status") != "completed"]

    if args.output == "console":
        display_console_results(
            successful_results, failed_results, execution_time, args.quiet
        )
    elif args.output == "json":
        display_json_results(results, execution_time)
    elif args.output == "csv":
        # Export session to CSV if we have results with session_id
        if results and results[0].get("session_id"):
            try:
                # Import here to avoid circular imports
                from enhanced_results_manager import EnhancedResultsManager

                manager = EnhancedResultsManager()
                session_id = results[0]["session_id"]
                csv_path = manager.export_session_to_csv(session_id)
                print(f"📊 CSV exported to: {csv_path}")
            except Exception as e:
                print(f"❌ CSV export failed: {e}")
                # Fallback to console display
                display_console_results(
                    successful_results, failed_results, execution_time, args.quiet
                )
        else:
            print("❌ No session data available for CSV export")
            display_console_results(
                successful_results, failed_results, execution_time, args.quiet
            )


def display_console_results(
    successful_results: List[Dict],
    failed_results: List[Dict],
    execution_time: float,
    quiet: bool = False,
):
    """Display results in clean console format"""

    if not quiet:
        print("📊 Evaluation Results")
        print("=" * 50)

    if successful_results:
        avg_score = sum(r["overall_score"] for r in successful_results) / len(
            successful_results
        )

        if not quiet:
            print(f"✅ Successful evaluations: {len(successful_results)}")
            print(f"📈 Average score: {avg_score:.1f}/10")
            print(f"⏱️ Execution time: {execution_time:.1f}s")
            print()
            print("🏆 Individual Results:")

        # Sort results by score (descending)
        successful_results.sort(key=lambda x: x["overall_score"], reverse=True)

        for result in successful_results:
            character_name = result.get("character_name", result["character_id"])
            scenario_name = result.get("scenario_name", result["scenario_id"])
            score = result["overall_score"]
            time_taken = result.get("execution_time", 0)

            if quiet:
                print(f"{result['character_id']}: {score:.1f}/10")
            else:
                print(
                    f"  • {character_name} ({result['character_id']}) - {scenario_name}: {score:.1f}/10 ({time_taken:.1f}s)"
                )

    if failed_results:
        print(f"\n❌ Failed evaluations: {len(failed_results)}")
        for result in failed_results:
            error = result.get("error", "Unknown error")
            print(f"  • {result['character_id']}/{result['scenario_id']}: {error}")


def display_json_results(results: List[Dict], execution_time: float):
    """Display results in JSON format"""
    import json

    output = {
        "evaluation_summary": {
            "total_evaluations": len(results),
            "successful": len([r for r in results if r.get("status") == "completed"]),
            "failed": len([r for r in results if r.get("status") != "completed"]),
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
        },
        "results": results,
    }

    print(json.dumps(output, indent=2, default=str))


def main():
    """Main CLI entry point"""

    try:
        # Parse and validate arguments
        args = parse_arguments()

        # Initialize system components
        character_manager = CharacterManager()
        scenarios = TestScenarios()
        ai_handler = AIHandler()
        results_manager = EnhancedResultsManager()

        # Validate arguments
        if not validate_arguments(args, character_manager, scenarios):
            sys.exit(1)

        # Validate AI provider availability
        available_chat_providers = ai_handler.get_chat_providers()
        if args.bots_ai not in available_chat_providers:
            print(f"❌ AI provider '{args.bots_ai}' not available")
            print(f"📋 Available providers: {', '.join(available_chat_providers)}")
            sys.exit(1)

        # Display configuration
        display_configuration(args, ai_handler)

        # Initialize evaluation pipeline
        pipeline = EvaluationPipeline(
            ai_handler=ai_handler,
            character_manager=character_manager,
            scenarios=scenarios,
            results_manager=results_manager,
        )

        # Execute evaluation (pipeline will create session automatically)
        start_time = time.time()

        if not args.quiet:
            print("🚀 Starting evaluation...")

        # Pass session ID to pipeline (it will auto-create if None)
        results = pipeline.execute_evaluation(
            characters=args.selected_characters,
            scenarios=args.selected_scenarios,
            bots_ai=args.bots_ai,
            session_id=args.session,  # Can be None for auto-creation
            max_workers=args.threads,
            progress_callback=(
                None if args.quiet else pipeline.default_progress_callback
            ),
        )

        execution_time = time.time() - start_time

        # Display results
        display_results(results, args, execution_time)

        # Show session information
        successful_count = len([r for r in results if r.get("status") == "completed"])
        session_id = results[0].get("session_id") if results else "unknown"

        if not args.quiet:
            print(f"\n🎉 Evaluation complete!")
            print(f"✅ {successful_count}/{len(results)} evaluations successful")
            print(f"📁 Session: {session_id}")

            # Get session info from results manager
            try:
                session_info = results_manager.get_current_session_info()
                if session_info:
                    session_dir = session_info.get("directory", "Unknown")
                    print(f"📂 Results saved to: {session_dir}")

                    # Show CSV export option
                    print(f'💾 Export to CSV: python -c "')
                    print(
                        f"from src.enhanced_results_manager import EnhancedResultsManager;"
                    )
                    print(f"manager = EnhancedResultsManager();")
                    print(f"manager.export_session_to_csv('{session_id}')\"")
            except:
                pass  # Don't fail if session info unavailable

        # Exit with appropriate code
        if successful_count == len(results):
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        if args.verbose if "args" in locals() else False:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
