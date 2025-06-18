import os
import sys
from typing import Optional
from colorama import init, Fore, Style, Back
from character_manager import CharacterManager
from ai_handler import AIHandler
from conversation import Conversation

init(autoreset=True)  # Initialize colorama


class ChatCLI:
    def __init__(self):
        self.character_manager = CharacterManager()
        self.ai_handler = AIHandler()
        self.current_conversation: Optional[Conversation] = None
        self.current_character_id: Optional[str] = None
        self.user_name = ""
        self.user_gender = ""
        self.current_provider = self.ai_handler.default_chat_provider

        print(
            f"{Fore.GREEN}🤖 Character Chatbot CLI - Updated Model Configuration{Style.RESET_ALL}"
        )

        # Display new model configuration
        provider_info = self.ai_handler.get_provider_info()
        print(f"📱 Character Chat Models: {', '.join(provider_info['chat_providers'])}")
        print(
            f"🧠 Evaluation Models: {', '.join(provider_info['evaluation_providers'])}"
        )
        print(f"🎯 Default Chat Provider: {provider_info['default_chat']}")
        print(f"📊 Default Evaluation Provider: {provider_info['default_evaluation']}")
        print()
        print(f"{Fore.CYAN}Model Details:{Style.RESET_ALL}")
        for model_name, version in provider_info["model_versions"].items():
            if model_name in ["claude", "gpt"]:  # Chat models
                print(f"  💬 {model_name}: {version}")
            else:  # Evaluation models
                print(f"  🧠 {model_name}: {version}")
        print()

    def setup_user(self) -> None:
        """Get user information"""
        print(f"{Fore.CYAN}👤 User Setup{Style.RESET_ALL}")
        self.user_name = input("Enter your name: ").strip()
        while not self.user_name:
            self.user_name = input("Name cannot be empty. Enter your name: ").strip()

        print("Select your gender:")
        print("1. Male")
        print("2. Female")
        print("3. Other")

        while True:
            choice = input("Enter choice (1-3): ").strip()
            if choice == "1":
                self.user_gender = "male"
                break
            elif choice == "2":
                self.user_gender = "female"
                break
            elif choice == "3":
                self.user_gender = "other"
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

        print(f"\n✓ Welcome, {self.user_name}!\n")

    def show_character_menu(self) -> None:
        """Display character selection menu"""
        characters = self.character_manager.list_characters()

        if not characters:
            print(
                f"{Fore.RED}No characters found! Make sure character JSON files are in the 'characters' directory.{Style.RESET_ALL}"
            )
            return

        print(f"{Fore.CYAN}🎭 Available Characters:{Style.RESET_ALL}")
        print()

        for i, (char_id, name, description, category) in enumerate(characters, 1):
            category_color = Fore.MAGENTA if category == "Fantasy" else Fore.GREEN
            print(
                f"{Fore.YELLOW}{i:2d}.{Style.RESET_ALL} {Fore.WHITE}{name}{Style.RESET_ALL}"
            )
            print(f"     {category_color}[{category}]{Style.RESET_ALL} {description}")
            print()

    def select_character(self) -> bool:
        """Let user select a character"""
        characters = self.character_manager.list_characters()

        if not characters:
            return False

        self.show_character_menu()

        while True:
            try:
                choice = (
                    input(f"Select character (1-{len(characters)}) or 'q' to quit: ")
                    .strip()
                    .lower()
                )

                if choice == "q":
                    return False

                char_index = int(choice) - 1
                if 0 <= char_index < len(characters):
                    char_id, char_name, _, _ = characters[char_index]
                    self.current_character_id = char_id

                    # Create new conversation
                    self.current_conversation = Conversation(
                        char_id, char_name, self.user_name
                    )

                    print(f"\n{Fore.GREEN}✓ Selected: {char_name}{Style.RESET_ALL}")

                    # Show character greeting
                    greeting = self.character_manager.get_character_greeting(
                        char_id, self.user_name
                    )
                    self.display_ai_response(greeting)
                    self.current_conversation.add_message("assistant", greeting)

                    return True
                else:
                    print("Invalid choice. Please try again.")

            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")

    def display_ai_response(self, response: str) -> None:
        """Display AI response with formatting"""
        print(
            f"\n{Back.BLUE}{Fore.WHITE} {self.current_conversation.character_name} {Style.RESET_ALL}"
        )

        # Simple formatting for narrative vs dialogue
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                print()
                continue

            if line.startswith("*") and line.endswith("*"):
                # Narrative text in italic style
                print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
            elif line.startswith('"') and line.endswith('"'):
                # Dialogue in bright white
                print(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
            else:
                # Mixed or other text
                print(f"{Fore.LIGHTBLUE_EX}{line}{Style.RESET_ALL}")
        print()

    def chat_loop(self) -> None:
        """Main chat interaction loop"""
        print(
            f"\n{Fore.YELLOW}💬 Chat started! Commands: /switch, /provider, /info, /models, /clear, /quit{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}Note: Using {self.current_provider} for character conversations{Style.RESET_ALL}\n"
        )

        while True:
            try:
                user_input = input(
                    f"{Fore.GREEN}{self.user_name}:{Style.RESET_ALL} "
                ).strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() == "/quit":
                    print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                    break
                elif user_input.lower() == "/switch":
                    if not self.select_character():
                        break
                    continue
                elif user_input.lower() == "/provider":
                    self.switch_provider()
                    continue
                elif user_input.lower() == "/info":
                    self.show_info()
                    continue
                elif user_input.lower() == "/models":
                    self.show_model_info()
                    continue
                elif user_input.lower() == "/clear":
                    self.current_conversation.clear_history()
                    print(
                        f"{Fore.YELLOW}Conversation history cleared.{Style.RESET_ALL}"
                    )
                    continue
                elif user_input.lower().startswith("/"):
                    print(
                        f"{Fore.RED}Unknown command. Available: /switch, /provider, /info, /models, /clear, /quit{Style.RESET_ALL}"
                    )
                    continue

                # Add user message to conversation
                self.current_conversation.add_message("user", user_input)

                # Generate AI response using chat-specific method
                print(f"{Fore.YELLOW}Thinking...{Style.RESET_ALL}")

                system_prompt = self.character_manager.generate_system_prompt(
                    self.current_character_id,
                    self.user_name,
                    self.user_gender,
                    self.current_conversation.get_formatted_history(),
                )

                # Use get_response_sync for character conversations (no thinking mode)
                ai_response = self.ai_handler.get_response_sync(
                    system_prompt, user_input, self.current_provider
                )

                # Display and save response
                self.display_ai_response(ai_response)
                self.current_conversation.add_message("assistant", ai_response)

            except KeyboardInterrupt:
                print(
                    f"\n{Fore.YELLOW}Chat interrupted. Use /quit to exit properly.{Style.RESET_ALL}"
                )
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def switch_provider(self) -> None:
        """Switch AI provider (chat providers only)"""
        chat_providers = self.ai_handler.get_chat_providers()

        if len(chat_providers) <= 1:
            print(
                f"{Fore.YELLOW}Only one chat provider available: {self.current_provider}{Style.RESET_ALL}"
            )
            return

        print(f"\nAvailable chat providers:")
        for i, provider in enumerate(chat_providers, 1):
            current = " (current)" if provider == self.current_provider else ""
            print(f"{i}. {provider}{current}")

        try:
            choice = int(input("Select provider: ").strip()) - 1
            if 0 <= choice < len(chat_providers):
                self.current_provider = chat_providers[choice]
                print(
                    f"{Fore.GREEN}✓ Switched to {self.current_provider} for character conversations{Style.RESET_ALL}"
                )
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")

    def show_info(self) -> None:
        """Show current session information"""
        if not self.current_conversation:
            print(f"{Fore.RED}No active conversation.{Style.RESET_ALL}")
            return

        character = self.character_manager.get_character(self.current_character_id)

        print(f"\n{Fore.CYAN}📊 Session Info:{Style.RESET_ALL}")
        print(f"User: {self.user_name} ({self.user_gender})")
        print(
            f"Character: {character['name']} ({character.get('category', 'Unknown')})"
        )
        print(f"Chat Provider: {self.current_provider}")
        print(f"Messages: {self.current_conversation.get_message_count()}")
        print(f"Description: {character['description']}")
        print()

    def show_model_info(self) -> None:
        """Show detailed model configuration"""
        provider_info = self.ai_handler.get_provider_info()

        print(f"\n{Fore.CYAN}🤖 Model Configuration:{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}Character Chat Models:{Style.RESET_ALL}")
        for provider in provider_info["chat_providers"]:
            current = " (current)" if provider == self.current_provider else ""
            model_version = provider_info["model_versions"].get(provider, "Unknown")
            print(f"  • {provider}: {model_version}{current}")

        print(f"\n{Fore.BLUE}Evaluation Models:{Style.RESET_ALL}")
        for provider in provider_info["evaluation_providers"]:
            default = (
                " (default)" if provider == provider_info["default_evaluation"] else ""
            )
            model_version = provider_info["model_versions"].get(provider, "Unknown")
            print(f"  • {provider}: {model_version}{default}")

        print(f"\n{Fore.YELLOW}Note:{Style.RESET_ALL}")
        print(f"  • Character conversations use natural, spontaneous responses")
        print(
            f"  • Evaluation tasks use reasoning-enhanced models (DeepSeek, Claude thinking, O3)"
        )
        print(f"  • Switch providers with /provider command")
        print()

    def run(self) -> None:
        """Main application entry point"""
        try:
            self.setup_user()

            if not self.select_character():
                print(f"{Fore.YELLOW}No character selected. Exiting.{Style.RESET_ALL}")
                return

            self.chat_loop()

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Application interrupted. Goodbye!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
            sys.exit(1)
