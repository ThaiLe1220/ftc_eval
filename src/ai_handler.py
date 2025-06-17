import os
from typing import Optional
import anthropic
import openai
from dotenv import load_dotenv

load_dotenv()


class AIHandler:
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self.default_provider = "claude"

        # Initialize Anthropic client
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                print("✓ Claude client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize Claude client: {e}")
        else:
            print("⚠ No ANTHROPIC_API_KEY found in .env")

        # Initialize OpenAI client
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                print("✓ GPT client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize GPT client: {e}")
        else:
            print("⚠ No OPENAI_API_KEY found in .env")

        # Determine default provider
        if self.anthropic_client:
            self.default_provider = "claude"
        elif self.openai_client:
            self.default_provider = "gpt"
        else:
            raise ValueError(
                "No AI providers available. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file"
            )

    def get_available_providers(self) -> list:
        """Get list of available AI providers"""
        providers = []
        if self.anthropic_client:
            providers.append("claude")
        if self.openai_client:
            providers.append("gpt")
        return providers

    async def get_response(
        self, system_prompt: str, user_message: str, provider: Optional[str] = None
    ) -> str:
        """Get AI response from specified provider"""
        if provider is None:
            provider = self.default_provider

        if provider == "claude" and self.anthropic_client:
            return await self._get_claude_response(system_prompt, user_message)
        elif provider == "gpt" and self.openai_client:
            return await self._get_gpt_response(system_prompt, user_message)
        else:
            raise ValueError(f"Provider '{provider}' not available")

    async def _get_claude_response(self, system_prompt: str, user_message: str) -> str:
        """Get response from Claude"""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=400,
                temperature=0.7,
            )
            return response.content[0].text
        except Exception as e:
            return f"Error getting Claude response: {e}"

    async def _get_gpt_response(self, system_prompt: str, user_message: str) -> str:
        """Get response from GPT"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=400,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting GPT response: {e}"

    def get_response_sync(
        self, system_prompt: str, user_message: str, provider: Optional[str] = None
    ) -> str:
        """Synchronous version of get_response"""
        if provider is None:
            provider = self.default_provider

        if provider == "claude" and self.anthropic_client:
            return self._get_claude_response_sync(system_prompt, user_message)
        elif provider == "gpt" and self.openai_client:
            return self._get_gpt_response_sync(system_prompt, user_message)
        else:
            raise ValueError(f"Provider '{provider}' not available")

    def _get_claude_response_sync(self, system_prompt: str, user_message: str) -> str:
        """Synchronous Claude response"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=400,
                temperature=0.7,
            )
            return response.content[0].text
        except Exception as e:
            return f"Error getting Claude response: {e}"

    def _get_gpt_response_sync(self, system_prompt: str, user_message: str) -> str:
        """Synchronous GPT response"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=400,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting GPT response: {e}"
