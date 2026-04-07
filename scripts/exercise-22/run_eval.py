#!/usr/bin/env python3
"""
Interactive runner for the LLM-as-a-Judge evaluation system.

Usage: python run_eval.py

This script provides an interactive CLI for:
1. Quick test (single battle with default models)
2. Full tournament (all battles, choose models)
3. Default comparison (Claude Haiku vs Sonnet)
"""

import asyncio
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_judge_eval import (
    run_model_comparison,
    AVAILABLE_MODELS,
    AgenticBattleSystem,
)


async def run_quick_test():
    """Run a quick test with default models (single battle only)"""
    print("Running Quick Test (Single Battle)")
    print("-" * 40)
    print("Testing: Claude Haiku vs Claude Sonnet")

    try:
        model1_config = AVAILABLE_MODELS["claude_haiku"]
        model2_config = AVAILABLE_MODELS["claude_haiku"]
        battle_system = AgenticBattleSystem(model1_config, model2_config)

        test_cases = battle_system.get_test_cases()
        if test_cases:
            battle_result = await battle_system.run_battle(test_cases[0])
            print(f"\nQuick test completed!")
            print(f"Winner: {battle_result.winner}")
            return True
        else:
            print("No test cases found")
            return False
    except Exception as e:
        print(f"Quick test failed: {e}")
        return False


async def run_full_tournament():
    """Run the full tournament with model selection"""
    print("Running Full Tournament")
    print("-" * 50)

    print("\nAvailable models:")
    model_keys = list(AVAILABLE_MODELS.keys())
    for i, key in enumerate(model_keys, 1):
        config = AVAILABLE_MODELS[key]
        print(f"  {i}. {key}: {config.name}")

    print("\nSelect models to compare:")

    # Get model 1
    while True:
        try:
            choice1 = input(f"Model 1 (1-{len(model_keys)}): ").strip()
            idx1 = int(choice1) - 1
            if 0 <= idx1 < len(model_keys):
                model1_key = model_keys[idx1]
                break
            print("Invalid choice, try again.")
        except ValueError:
            print("Please enter a number.")

    # Get model 2
    while True:
        try:
            choice2 = input(f"Model 2 (1-{len(model_keys)}): ").strip()
            idx2 = int(choice2) - 1
            if 0 <= idx2 < len(model_keys):
                model2_key = model_keys[idx2]
                if model2_key != model1_key:
                    break
                print("Cannot compare model to itself.")
            else:
                print("Invalid choice, try again.")
        except ValueError:
            print("Please enter a number.")

    stats = await run_model_comparison(model1_key, model2_key)
    return stats


def main():
    """Main function with interactive menu"""
    print("\n" + "=" * 50)
    print("LLM-as-a-Judge Security Evaluation")
    print("=" * 50)
    print("\nChoose evaluation mode:")
    print("1. Quick test (single battle, default models)")
    print("2. Full tournament (all battles, choose models)")
    print("3. Default comparison (Nova Micro vs Claude Haiku)")
    print("4. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                print("\nStarting quick test...")
                success = asyncio.run(run_quick_test())
                if success:
                    print("\nQuick test completed successfully!")
                break

            elif choice == "2":
                print("\nStarting full tournament...")
                asyncio.run(run_full_tournament())
                print("\nFull tournament completed successfully!")
                break

            elif choice == "3":
                print("\nRunning default comparison...")
                asyncio.run(run_model_comparison("nova_micro", "claude_haiku"))
                print("\nDefault comparison completed successfully!")
                break

            elif choice == "4":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\nError occurred: {e}")
            break


if __name__ == "__main__":
    main()
