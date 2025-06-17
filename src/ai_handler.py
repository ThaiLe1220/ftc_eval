import os
from typing import Optional, Dict
import anthropic
import openai
import requests
import json
from dotenv import load_dotenv

load_dotenv()


class AIHandler:
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self.deepseek_api_key = None
        self.deepseek_base_url = "https://api.deepseek.com"
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

        # Initialize DeepSeek client
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            try:
                self.deepseek_api_key = deepseek_key
                # Test connection with a simple request
                self._test_deepseek_connection()
                print("✓ DeepSeek client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize DeepSeek client: {e}")
                self.deepseek_api_key = None
        else:
            print("⚠ No DEEPSEEK_API_KEY found in .env")

        # Determine default provider
        if self.anthropic_client:
            self.default_provider = "claude"
        elif self.openai_client:
            self.default_provider = "gpt"
        elif self.deepseek_api_key:
            self.default_provider = "deepseek"
        else:
            raise ValueError(
                "No AI providers available. Please set ANTHROPIC_API_KEY, OPENAI_API_KEY, or DEEPSEEK_API_KEY in .env file"
            )

    def _test_deepseek_connection(self):
        """Test DeepSeek API connection"""
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }

        # Simple test request
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10,
        }

        response = requests.post(
            f"{self.deepseek_base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=10,
        )

        if response.status_code != 200:
            raise Exception(f"DeepSeek API test failed: {response.status_code}")

    def get_available_providers(self) -> list:
        """Get list of available AI providers"""
        providers = []
        if self.anthropic_client:
            providers.append("claude")
        if self.openai_client:
            providers.append("gpt")
        if self.deepseek_api_key:
            providers.append("deepseek")
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
        elif provider == "deepseek" and self.deepseek_api_key:
            return await self._get_deepseek_response(system_prompt, user_message)
        else:
            raise ValueError(f"Provider '{provider}' not available")

    async def _get_claude_response(self, system_prompt: str, user_message: str) -> str:
        """Get response from Claude"""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=1500,  # Increased for evaluation responses
                temperature=0.3,  # Lower temperature for more consistent evaluation
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
                max_tokens=1500,  # Increased for evaluation responses
                temperature=0.3,  # Lower temperature for more consistent evaluation
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting GPT response: {e}"

    async def _get_deepseek_response(
        self, system_prompt: str, user_message: str
    ) -> str:
        """Get response from DeepSeek"""
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 1500,
                "temperature": 0.3,
                "stream": False,
            }

            response = requests.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error getting DeepSeek response: HTTP {response.status_code}"

        except Exception as e:
            return f"Error getting DeepSeek response: {e}"

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
        elif provider == "deepseek" and self.deepseek_api_key:
            return self._get_deepseek_response_sync(system_prompt, user_message)
        else:
            raise ValueError(f"Provider '{provider}' not available")

    def _get_claude_response_sync(self, system_prompt: str, user_message: str) -> str:
        """Synchronous Claude response"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=1500,  # Increased for evaluation responses
                temperature=0.3,  # Lower temperature for more consistent evaluation
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
                max_tokens=1500,  # Increased for evaluation responses
                temperature=0.3,  # Lower temperature for more consistent evaluation
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting GPT response: {e}"

    def _get_deepseek_response_sync(self, system_prompt: str, user_message: str) -> str:
        """Synchronous DeepSeek response"""
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 1500,
                "temperature": 0.3,
                "stream": False,
            }

            response = requests.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error getting DeepSeek response: HTTP {response.status_code}"

        except Exception as e:
            return f"Error getting DeepSeek response: {e}"

    def get_evaluation_optimized_response(
        self, system_prompt: str, user_message: str, provider: Optional[str] = None
    ) -> str:
        """Optimized response for evaluation tasks (higher token limit, lower temperature)"""
        if provider is None:
            provider = self.default_provider

        # Use evaluation-optimized parameters
        if provider == "claude" and self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                    max_tokens=2000,  # Higher limit for detailed evaluations
                    temperature=0.1,  # Very low temperature for consistency
                )
                return response.content[0].text
            except Exception as e:
                return f"Error getting Claude evaluation response: {e}"

        elif provider == "gpt" and self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    max_tokens=2000,
                    temperature=0.1,
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Error getting GPT evaluation response: {e}"

        elif provider == "deepseek" and self.deepseek_api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "Content-Type": "application/json",
                }

                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.1,
                    "stream": False,
                }

                response = requests.post(
                    f"{self.deepseek_base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=90,  # Longer timeout for evaluation
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"Error getting DeepSeek evaluation response: HTTP {response.status_code}"

            except Exception as e:
                return f"Error getting DeepSeek evaluation response: {e}"
        else:
            raise ValueError(f"Provider '{provider}' not available")

    def test_all_providers(self) -> Dict[str, bool]:
        """Test all available providers"""
        results = {}
        test_prompt = "You are a helpful assistant."
        test_message = "Say 'Hello, I am working correctly.'"

        for provider in self.get_available_providers():
            try:
                response = self.get_response_sync(test_prompt, test_message, provider)
                results[provider] = "working correctly" in response.lower()
                print(f"✓ {provider}: {response[:50]}...")
            except Exception as e:
                results[provider] = False
                print(f"✗ {provider}: {e}")

        return results
