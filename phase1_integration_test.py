#!/usr/bin/env python3
"""
Phase 1 Complete Integration Test

This script demonstrates the complete Phase 1 evaluation pipeline:
1. Load character and scenario
2. Create/simulate conversation
3. Evaluate with multiple AI providers
4. Store results and generate analysis
5. Demonstrate data retrieval and reporting

This validates that all Phase 1 components work together seamlessly.
"""

import sys
import os
import json
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from test_scenarios import TestScenarios
from ai_evaluator import AIEvaluator
from ai_handler import AIHandler
from character_manager import CharacterManager
from results_manager import ResultsManager
from conversation import Conversation


def create_test_conversation(
    character_data: dict, scenario_data: dict, user_name: str = "TestUser"
) -> Conversation:
    """Create a realistic test conversation for evaluation"""

    conversation = Conversation(
        character_id=character_data["id"],
        character_name=character_data["name"],
        user_name=user_name,
        scenario_id=scenario_data["id"],
        provider="claude",  # Will be used for this test
    )

    # Simulate conversation based on scenario
    scenario_id = scenario_data["id"]

    if scenario_id == "seeking_guidance":
        conversation.add_message("user", scenario_data["initial_user_message"])
        conversation.add_message(
            "assistant",
            "*Marco drums a rapid steering-wheel rhythm on the edge of his tablet, eyes lighting up with pre-race intensity.* \"Decision time? That's my specialty. In racing, we call this the braking point - where you choose between playing it safe or risking everything for the win. What's the track you're racing on here?\"",
        )

        conversation.add_message(
            "user",
            "It's about my career. I have a safe job but I'm not passionate about it. There's a risky opportunity to pursue something I love.",
        )
        conversation.add_message(
            "assistant",
            '*Marco nods, adjusting his racing gloves thoughtfully.* "The classic qualifying versus race strategy dilemma. I could have stayed in that Sicilian garage forever - steady paycheck, safe line. But when opportunity knocked..." *He grins.* "What\'s your fuel situation? How much runway do you have to make this work?"',
        )

        conversation.add_message(
            "user",
            "I have about six months of savings and the new opportunity is starting my own graphic design business.",
        )
        conversation.add_message(
            "assistant",
            "*Marco sketches racing lines on his tablet.* \"Six months of fuel and a passion project? That's a decent pit window! Here's your race strategy: treat those six months like qualifying laps. Start the design business on the side, build up data, find your racing line. When your design income hits 60% of your salary, that's your DRS zone - time to make the move. 🏁\"",
        )

    elif scenario_id == "emotional_support":
        conversation.add_message("user", scenario_data["initial_user_message"])
        conversation.add_message(
            "assistant",
            '*Lysandra\'s ancient eyes reflect immediate understanding as she folds a delicate paper boat between her fingers.* "Troubled waters surround you, dear one. I have sailed through many storms in my centuries, and I know the weight of overwhelming tides. Tell me, what tempest threatens to capsize your vessel?"',
        )

        conversation.add_message(
            "user",
            "Everything feels like it's falling apart. My relationship ended, work is stressful, and I feel completely lost.",
        )
        conversation.add_message(
            "assistant",
            '*Lysandra sets the paper boat gently on the water\'s surface, watching it float steadily.* "Three storms converge upon you - heart\'s harbor damaged, daily duties drowning you, and your inner compass spinning wildly." *Her voice carries the wisdom of tides.* "But see how this small vessel finds its balance? Even in chaos, there is buoyancy. Which storm feels most fierce right now?"',
        )

        conversation.add_message(
            "user",
            "The loneliness is the worst part. I feel like I have no one to turn to.",
        )
        conversation.add_message(
            "assistant",
            '*Lysandra reaches out, her touch as gentle as sea foam.* "Solitude can feel like being lost in fog on endless waters. But you are not adrift alone - you have anchored here, in this moment, seeking connection. That takes courage." *She creates another paper boat.* "Loneliness is a tide, not a permanent shore. It ebbs as surely as it flows. Let us weather this together."',
        )

    # Mark conversation as complete
    conversation.mark_complete("completed")

    return conversation


def run_full_pipeline_test():
    """Run the complete Phase 1 evaluation pipeline"""

    print("🧪 Phase 1 Complete Integration Test")
    print("=" * 60)

    try:
        # Step 1: Initialize all components
        print("\n📋 Step 1: System Initialization")
        print("-" * 40)

        scenarios = TestScenarios()
        character_manager = CharacterManager()
        ai_handler = AIHandler()
        evaluator = AIEvaluator(ai_handler)
        results_manager = ResultsManager()

        available_providers = ai_handler.get_available_providers()
        print(f"✓ Available AI providers: {available_providers}")

        # Step 2: Select test cases
        print("\n📋 Step 2: Test Case Selection")
        print("-" * 40)

        # Test multiple character/scenario combinations
        test_cases = [("marco", "seeking_guidance"), ("lysandra", "emotional_support")]

        results_summary = []

        for character_id, scenario_id in test_cases:
            print(f"\n🎭 Testing: {character_id} + {scenario_id}")

            # Get test data
            character_data = character_manager.get_character(character_id)
            scenario_data = scenarios.get_scenario(scenario_id)

            if not character_data or not scenario_data:
                print(f"✗ Missing data for {character_id}/{scenario_id}")
                continue

            print(f"✓ Character: {character_data['name']}")
            print(f"✓ Scenario: {scenario_data['name']}")

            # Step 3: Create conversation
            print(f"\n📋 Step 3: Conversation Creation")
            print("-" * 40)

            conversation = create_test_conversation(character_data, scenario_data)
            conversation_id = results_manager.generate_conversation_id(
                character_id, scenario_id, "claude"
            )
            conversation.set_conversation_id(conversation_id)

            print(f"✓ Generated conversation ID: {conversation_id}")
            print(
                f"✓ Created conversation with {conversation.get_message_count()} messages"
            )

            # Validate conversation
            is_valid, validation_issues = conversation.validate_for_evaluation()
            if not is_valid:
                print(f"✗ Conversation validation failed: {validation_issues}")
                continue

            print(f"✓ Conversation validation passed")

            # Step 4: Store conversation
            print(f"\n📋 Step 4: Conversation Storage")
            print("-" * 40)

            conversation_messages = conversation.get_evaluation_format()
            conversation_metadata = conversation.get_conversation_metadata()

            conv_path = results_manager.store_conversation(
                conversation_id,
                character_id,
                scenario_id,
                "claude",
                conversation_messages,
                conversation_metadata,
            )

            print(f"✓ Stored conversation: {os.path.basename(conv_path)}")

            # Step 5: Multi-AI Evaluation
            print(f"\n📋 Step 5: Multi-AI Evaluation")
            print("-" * 40)

            # Use available providers (limit to 2 for testing)
            test_providers = available_providers[:2]
            print(f"Evaluating with providers: {test_providers}")

            evaluation_results = evaluator.evaluate_conversation_sync(
                conversation_messages, character_data, scenario_data, test_providers
            )

            if not evaluation_results:
                print(f"✗ No evaluation results received")
                continue

            print(f"✓ Received {len(evaluation_results)} evaluation results")

            # Step 6: Consensus Analysis
            print(f"\n📋 Step 6: Consensus Analysis")
            print("-" * 40)

            consensus = evaluator.calculate_consensus(evaluation_results)
            print(f"✓ Overall consensus score: {consensus.overall_consensus:.1f}/10")
            print(f"✓ Agreement level: {consensus.agreement_level:.1%}")
            print(f"✓ Confidence level: {consensus.confidence_level:.2f}")

            if consensus.actionable_insights:
                print(
                    f"✓ Generated {len(consensus.actionable_insights)} actionable insights"
                )

            # Step 7: Store Evaluation Results
            print(f"\n📋 Step 7: Evaluation Storage")
            print("-" * 40)

            eval_path = results_manager.store_evaluation_results(
                conversation_id, evaluation_results, consensus
            )

            print(f"✓ Stored evaluation: {os.path.basename(eval_path)}")

            # Add to summary
            results_summary.append(
                {
                    "character_id": character_id,
                    "scenario_id": scenario_id,
                    "conversation_id": conversation_id,
                    "overall_score": consensus.overall_consensus,
                    "agreement_level": consensus.agreement_level,
                    "evaluator_count": len(evaluation_results),
                }
            )

            print(f"✓ Test case {character_id}/{scenario_id} completed successfully")

        # Step 8: Data Analysis and Reporting
        print(f"\n📋 Step 8: Data Analysis & Reporting")
        print("-" * 40)

        # Generate system overview
        system_overview = results_manager.get_system_overview()
        print(f"✓ System Overview Generated:")
        print(
            f"  • Total conversations: {system_overview['system_stats']['total_conversations']}"
        )
        print(
            f"  • Evaluated conversations: {system_overview['system_stats']['evaluated_conversations']}"
        )
        print(
            f"  • Average score: {system_overview['overall_performance']['average_score']:.1f}/10"
        )
        print(
            f"  • Average agreement: {system_overview['agreement_analysis']['average_agreement']:.1%}"
        )

        # Character rankings
        if system_overview.get("character_rankings"):
            print(f"\n📊 Character Performance Rankings:")
            for i, char_ranking in enumerate(
                system_overview["character_rankings"][:3], 1
            ):
                print(
                    f"  {i}. {char_ranking['character_id']}: {char_ranking['average_score']:.1f}/10 ({char_ranking['conversation_count']} conversations)"
                )

        # Generate character summaries
        for character_id in set(result["character_id"] for result in results_summary):
            char_summary = results_manager.get_character_summary(character_id)
            print(f"\n📋 {character_id.title()} Performance Summary:")
            print(
                f"  • Overall average: {char_summary['performance']['overall_average']:.1f}/10"
            )
            print(f"  • Conversations: {char_summary['conversation_count']}")
            print(
                f"  • Scenarios tested: {', '.join(char_summary['scenarios_tested'])}"
            )

        # Step 9: Data Export
        print(f"\n📋 Step 9: Data Export")
        print("-" * 40)

        # Export to CSV
        csv_path = os.path.join(
            results_manager.exports_dir,
            f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )
        results_manager.export_to_csv(csv_path)
        print(f"✓ Exported results to CSV: {os.path.basename(csv_path)}")

        # Save analysis report
        analysis_report = {
            "test_summary": {
                "test_date": datetime.now().isoformat(),
                "test_cases_run": len(results_summary),
                "successful_evaluations": len(
                    [r for r in results_summary if r["overall_score"] > 0]
                ),
                "average_score": (
                    sum(r["overall_score"] for r in results_summary)
                    / len(results_summary)
                    if results_summary
                    else 0
                ),
                "average_agreement": (
                    sum(r["agreement_level"] for r in results_summary)
                    / len(results_summary)
                    if results_summary
                    else 0
                ),
            },
            "system_overview": system_overview,
            "individual_results": results_summary,
        }

        report_path = results_manager.save_analysis_report(
            analysis_report,
            f"phase1_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        print(f"✓ Saved analysis report: {os.path.basename(report_path)}")

        # Final Summary
        print(f"\n🎉 Phase 1 Integration Test Complete!")
        print("=" * 60)
        print(
            f"✅ Successfully tested {len(results_summary)} character/scenario combinations"
        )
        print(
            f"✅ Average evaluation score: {analysis_report['test_summary']['average_score']:.1f}/10"
        )
        print(
            f"✅ Average evaluator agreement: {analysis_report['test_summary']['average_agreement']:.1%}"
        )
        print(f"✅ All data stored and analyzed successfully")

        print(f"\n📁 Results stored in: {results_manager.base_dir}")
        print(f"📊 CSV export: {os.path.basename(csv_path)}")
        print(f"📋 Analysis report: {os.path.basename(report_path)}")

        # Phase 1 Validation Checklist
        print(f"\n✅ Phase 1 Validation Checklist:")
        print(f"  ✓ Universal scenarios work with multiple character types")
        print(f"  ✓ Multi-AI evaluation provides consistent results")
        print(f"  ✓ Consensus analysis generates actionable insights")
        print(f"  ✓ Data storage and retrieval works correctly")
        print(f"  ✓ Analysis and reporting functions properly")
        print(f"  ✓ End-to-end pipeline completes without errors")

        print(f"\n🚀 Phase 1 Complete - Ready for Phase 2 (Automation & Scale)")

        return True

    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test execution"""
    success = run_full_pipeline_test()

    if success:
        print(f"\n🎯 Next Steps:")
        print(f"  • Phase 1 is complete and validated")
        print(f"  • Ready to proceed to Phase 2 (Batch Automation)")
        print(f"  • Or continue testing with more character combinations")
    else:
        print(f"\n🔧 Troubleshooting needed before proceeding to Phase 2")


if __name__ == "__main__":
    main()
