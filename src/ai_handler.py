import os
import time
from typing import Optional, Dict, Tuple
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
        self.deepseek_client = None
        self.deepseek_base_url = "https://api.deepseek.com"

        # Separate defaults for different use cases
        self.default_chat_provider = "claude"  # For character conversations
        self.default_evaluation_provider = "deepseek_reasoner"  # For evaluation tasks

        # Initialize Anthropic client
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                print("✓ Claude Sonnet 4 client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize Claude client: {e}")
        else:
            print("⚠ No ANTHROPIC_API_KEY found in .env")

        # Initialize OpenAI client
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                print("✓ GPT-4.1 client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize GPT client: {e}")
        else:
            print("⚠ No OPENAI_API_KEY found in .env")

        # Initialize DeepSeek client
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            try:
                self.deepseek_client = openai.OpenAI(
                    api_key=deepseek_key, base_url=self.deepseek_base_url
                )
                # Test connection
                self._test_deepseek_connection()
                print("✓ DeepSeek Reasoner client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize DeepSeek client: {e}")
                self.deepseek_client = None
        else:
            print("⚠ No DEEPSEEK_API_KEY found in .env")

        # Determine default providers
        if not self._determine_defaults():
            raise ValueError(
                "No AI providers available. Please set ANTHROPIC_API_KEY, OPENAI_API_KEY, or DEEPSEEK_API_KEY in .env file"
            )

    def _test_deepseek_connection(self):
        """Test DeepSeek API connection"""
        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=90,
            )
            if not response.choices:
                raise Exception("No response from DeepSeek API")
        except Exception as e:
            raise Exception(f"DeepSeek API test failed: {e}")

    def _determine_defaults(self) -> bool:
        """Determine default providers based on availability"""
        chat_providers = self.get_chat_providers()
        eval_providers = self.get_evaluation_providers()

        if not chat_providers or not eval_providers:
            return False

        # Set chat default
        if "claude" in chat_providers:
            self.default_chat_provider = "claude"
        elif "gpt" in chat_providers:
            self.default_chat_provider = "gpt"

        # Set evaluation default (prefer deepseek_reasoner)
        if "deepseek_reasoner" in eval_providers:
            self.default_evaluation_provider = "deepseek_reasoner"
        elif "claude_thinking" in eval_providers:
            self.default_evaluation_provider = "claude_thinking"
        elif "o3" in eval_providers:
            self.default_evaluation_provider = "o3"

        return True

    def get_chat_providers(self) -> list:
        """Get available providers for character conversations"""
        providers = []
        if self.anthropic_client:
            providers.append("claude")
        if self.openai_client:
            providers.append("gpt")
        return providers

    def get_evaluation_providers(self) -> list:
        """Get available providers for evaluation tasks"""
        providers = []
        if self.deepseek_client:
            providers.append("deepseek_reasoner")
        if self.anthropic_client:
            providers.append("claude_thinking")
        if self.openai_client:
            providers.append("o3")
        return providers

    def get_available_providers(self) -> list:
        """Get all available providers (for backward compatibility)"""
        all_providers = []
        all_providers.extend(self.get_chat_providers())
        eval_providers = self.get_evaluation_providers()
        for provider in eval_providers:
            if provider not in all_providers:
                all_providers.append(provider)
        return all_providers

    # CHARACTER CONVERSATION METHODS (Claude Sonnet 4 without thinking, GPT-4.1)
    def get_response_sync(
        self, system_prompt: str, user_message: str, provider: Optional[str] = None
    ) -> str:
        """Get response for character conversations (Claude without thinking or GPT-4.1)"""
        if provider is None:
            provider = self.default_chat_provider

        if provider == "claude" and self.anthropic_client:
            return self._get_claude_chat_response_sync(system_prompt, user_message)
        elif provider == "gpt" and self.openai_client:
            return self._get_gpt_response_sync(system_prompt, user_message)
        else:
            available = self.get_chat_providers()
            raise ValueError(
                f"Provider '{provider}' not available for chat. Available: {available}"
            )

    def _get_claude_chat_response_sync(
        self, system_prompt: str, user_message: str
    ) -> str:
        """Claude Sonnet 4 for character conversations (no thinking mode)"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=360,
                temperature=0.7,
            )
            return response.content[0].text
        except Exception as e:
            return f"Error getting Claude chat response: {e}"

    def _get_gpt_response_sync(self, system_prompt: str, user_message: str) -> str:
        """GPT-4.1 for character conversations or evaluations"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=360,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting GPT response: {e}"

    # EVALUATION METHODS (DeepSeek Reasoner, Claude with thinking, GPT-4.1)
    def get_evaluation_response_sync(
        self, system_prompt: str, user_message: str, provider: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """Get response for evaluation tasks (DeepSeek Reasoner, Claude thinking, GPT-4.1)"""
        if provider is None:
            provider = self.default_evaluation_provider

        start_time = time.time()

        try:
            if provider == "deepseek_reasoner" and self.deepseek_client:
                response, metadata = self._get_deepseek_reasoner_response_sync(
                    system_prompt, user_message
                )
            elif provider == "claude_thinking" and self.anthropic_client:
                response, metadata = self._get_claude_thinking_response_sync(
                    system_prompt, user_message
                )
            elif provider == "o3" and self.openai_client:
                response, metadata = self._get_o3_evaluation_response_sync(
                    system_prompt, user_message
                )
            else:
                available = self.get_evaluation_providers()
                raise ValueError(
                    f"Provider '{provider}' not available for evaluation. Available: {available}"
                )

            # Add response time to metadata
            metadata["response_time"] = time.time() - start_time
            return response, metadata

        except Exception as e:
            error_metadata = {
                "error": str(e),
                "response_time": time.time() - start_time,
                "token_usage": {"total_tokens": 0},
                "has_reasoning": False,
                "has_thinking": False,
            }
            return f"Error getting evaluation response: {e}", error_metadata

    def _get_deepseek_reasoner_response_sync(
        self, system_prompt: str, user_message: str
    ) -> Tuple[str, Dict]:
        """DeepSeek Reasoner for evaluation tasks"""
        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=64000,
                temperature=0.3,
            )

            # DeepSeek Reasoner provides both reasoning_content and content
            choice = response.choices[0]
            reasoning = getattr(choice.message, "reasoning_content", None)
            content = choice.message.content

            # Build metadata
            metadata = {
                "token_usage": {
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(
                        response.usage, "completion_tokens", 0
                    ),
                },
                "has_reasoning": reasoning is not None,
                "has_thinking": False,
                "provider": "deepseek_reasoner",
            }

            return content, metadata
        except Exception as e:
            error_metadata = {
                "error": str(e),
                "token_usage": {"total_tokens": 0},
                "has_reasoning": False,
                "has_thinking": False,
                "provider": "deepseek_reasoner",
            }
            return f"Error getting DeepSeek Reasoner response: {e}", error_metadata

    def _get_claude_thinking_response_sync(
        self, system_prompt: str, user_message: str
    ) -> Tuple[str, Dict]:
        """Claude Sonnet 4 with thinking mode for evaluation tasks"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=27000,  # Increased to be greater than budget_tokens
                thinking={"type": "enabled", "budget_tokens": 18000},
            )

            # Extract text content from response blocks
            text_content = ""
            has_thinking = False
            for block in response.content:
                if block.type == "text":
                    text_content = block.text
                elif block.type == "thinking":
                    has_thinking = True

            # Clean up markdown-wrapped JSON if present
            if text_content.strip().startswith("```json"):
                # Remove ```json at the start and ``` at the end
                lines = text_content.strip().split("\n")
                if lines[0].strip() == "```json" and lines[-1].strip() == "```":
                    text_content = "\n".join(lines[1:-1])

            # Build metadata
            metadata = {
                "token_usage": {
                    "total_tokens": getattr(response.usage, "output_tokens", 0)
                    + getattr(response.usage, "input_tokens", 0),
                    "prompt_tokens": getattr(response.usage, "input_tokens", 0),
                    "completion_tokens": getattr(response.usage, "output_tokens", 0),
                },
                "has_reasoning": False,
                "has_thinking": has_thinking,
                "provider": "claude_thinking",
            }

            return text_content or "No text response received", metadata
        except Exception as e:
            error_metadata = {
                "error": str(e),
                "token_usage": {"total_tokens": 0},
                "has_reasoning": False,
                "has_thinking": False,
                "provider": "claude_thinking",
            }
            return f"Error getting Claude thinking response: {e}", error_metadata

    def _get_o3_evaluation_response_sync(
        self, system_prompt: str, user_message: str
    ) -> Tuple[str, Dict]:
        """O3 for evaluation tasks using the correct chat completions API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="o3",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                reasoning_effort="medium",  # O3 specific parameter
                max_completion_tokens=4000,
            )

            # Build metadata
            metadata = {
                "token_usage": {
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(
                        response.usage, "completion_tokens", 0
                    ),
                },
                "has_reasoning": True,  # O3 has built-in reasoning
                "has_thinking": False,
                "provider": "o3",
            }

            return response.choices[0].message.content, metadata

        except Exception as e:
            # No fallback - just return error
            error_metadata = {
                "error": str(e),
                "token_usage": {"total_tokens": 0},
                "has_reasoning": False,
                "has_thinking": False,
                "provider": "o3_failed",
            }
            return f"Error getting O3 evaluation response: {e}", error_metadata

    # BACKWARD COMPATIBILITY METHODS (for existing Phase 1 code)
    async def get_response(
        self, system_prompt: str, user_message: str, provider: Optional[str] = None
    ) -> str:
        """Async version - delegates to sync for simplicity"""
        return self.get_response_sync(system_prompt, user_message, provider)

    def get_evaluation_optimized_response(
        self, system_prompt: str, user_message: str, provider: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """Legacy method - now delegates to evaluation response with metadata"""
        return self.get_evaluation_response_sync(system_prompt, user_message, provider)

    # UTILITY METHODS
    def test_all_providers(self) -> Dict[str, bool]:
        """Test all available providers with JSON format requirement"""
        results = {}

        # Test chat providers with JSON format
        test_prompt = (
            "You are a helpful assistant. Always respond in valid JSON format only."
        )
        test_message = 'Respond with: {"status": "working", "message": "Hello, I am working correctly.", "provider": "your_model_name"}'

        for provider in self.get_chat_providers():
            try:
                response = self.get_response_sync(test_prompt, test_message, provider)

                # Try to parse JSON to validate format
                try:
                    json_response = json.loads(response.strip())
                    results[f"{provider}_chat"] = (
                        json_response.get("status") == "working"
                    )
                    print(f"✓ {provider} (chat): {json.dumps(json_response, indent=2)}")
                except json.JSONDecodeError:
                    results[f"{provider}_chat"] = False
                    print(f"✗ {provider} (chat): Invalid JSON - {response[:50]}...")

            except Exception as e:
                results[f"{provider}_chat"] = False
                print(f"✗ {provider} (chat): {e}")

        # Test evaluation providers with JSON format
        eval_prompt = (
            "You are an expert evaluator. Always respond in valid JSON format only."
        )
        eval_message = 'Rate "Hello, how are you today?" and respond with: {"rating": 8, "reasoning": "brief explanation", "strengths": ["clear", "polite"], "provider": "your_model_name"}'

        for provider in self.get_evaluation_providers():
            try:
                # Now properly unpack the tuple (content, metadata)
                response, metadata = self.get_evaluation_response_sync(
                    eval_prompt, eval_message, provider
                )

                # Try to parse JSON to validate format
                try:
                    json_response = json.loads(response.strip())
                    results[f"{provider}_eval"] = isinstance(
                        json_response.get("rating"), (int, float)
                    )
                    print(f"✓ {provider} (eval): {json.dumps(json_response, indent=2)}")
                    print(
                        f"  📊 Metadata: {metadata.get('response_time', 0):.2f}s, {metadata.get('token_usage', {}).get('total_tokens', 0)} tokens, reasoning: {metadata.get('has_reasoning', False)}, thinking: {metadata.get('has_thinking', False)}"
                    )
                except json.JSONDecodeError:
                    results[f"{provider}_eval"] = False
                    print(f"✗ {provider} (eval): Invalid JSON - {response[:50]}...")
                    print(
                        f"  📊 Metadata: {metadata.get('response_time', 0):.2f}s, Error: {metadata.get('error', 'JSON parsing failed')}"
                    )

            except Exception as e:
                results[f"{provider}_eval"] = False
                print(f"✗ {provider} (eval): {e}")

        return results

    def get_provider_info(self) -> Dict:
        """Get information about provider configuration"""
        return {
            "chat_providers": self.get_chat_providers(),
            "evaluation_providers": self.get_evaluation_providers(),
            "default_chat": self.default_chat_provider,
            "default_evaluation": self.default_evaluation_provider,
            "model_versions": {
                "claude": "claude-sonnet-4-20250514",
                "claude_thinking": "claude-sonnet-4-20250514 (with thinking)",
                "deepseek_reasoner": "deepseek-reasoner",
                "o3": "o3 (with reasoning)",
                "gpt": "gpt-4.1",
            },
        }

    def get_user_response_for_conversation(
        self, system_prompt: str, user_prompt: str
    ) -> str:
        """Generate user response for conversation automation using GPT-4.1 (always)"""

        if not self.openai_client:
            raise ValueError("GPT-4.1 not available for user response generation")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=180,
                temperature=0.9,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating user response: {e}"

    def validate_conversation_response_quality(
        self, response: str, context: str = ""
    ) -> bool:
        """Validate quality of generated conversation responses"""

        if not response or len(response.strip()) < 5:
            return False

        # Check for error messages
        if response.lower().startswith("error") or "error" in response.lower():
            return False

        # Check for reasonable length (not too short or too long)
        if len(response) < 10 or len(response) > 1000:
            return False

        # Check for natural conversation markers
        unnatural_patterns = [
            "as an ai",
            "i'm an ai",
            "i cannot",
            "i don't have the ability",
            "i'm not able to",
            "i cannot provide",
            "i'm sorry, but i cannot",
        ]

        response_lower = response.lower()
        for pattern in unnatural_patterns:
            if pattern in response_lower:
                return False

        return True

    def get_optimal_provider_for_conversation(
        self, character_category: str = "universal"
    ) -> str:
        """Get optimal provider for character conversations based on character type"""

        chat_providers = self.get_chat_providers()

        # Prefer Claude for character conversations (better at creative roleplay)
        if "claude" in chat_providers:
            return "claude"
        elif "gpt" in chat_providers:
            return "gpt"
        else:
            return self.default_chat_provider if chat_providers else None
