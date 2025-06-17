#!/usr/bin/env python3
"""
Character Chatbot CLI - Simplified version for AI evaluation

Usage: python main.py

Make sure to:
1. Create .env file with ANTHROPIC_API_KEY and/or OPENAI_API_KEY
2. Place character JSON files in 'characters/' directory
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cli import ChatCLI


def main():
    """Main entry point"""
    # Check for .env file
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with your API keys:")
        print("ANTHROPIC_API_KEY=your_claude_key_here")
        print("OPENAI_API_KEY=your_openai_key_here")
        print()

    # Check for characters directory
    if not os.path.exists("characters"):
        print("⚠️  Warning: 'characters' directory not found!")
        print("Please create a 'characters' directory and add character JSON files.")
        print()
        return

    # Run the CLI
    cli = ChatCLI()
    cli.run()


if __name__ == "__main__":
    main()
