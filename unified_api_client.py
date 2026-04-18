import os
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
from models_config import AVAILABLE_MODELS, DEFAULT_MODEL
from api_usage_tracker import tracker

load_dotenv()

class UnifiedAPIClient:
    """Unified client supporting multiple AI providers with automatic fallback."""

    def __init__(self):
        self.api_keys = {
            "euri": [
                os.getenv("EURI_API_KEY1"),
                os.getenv("EURI_API_KEY2")
            ]
        }
        self.base_urls = {
            "euri": "https://api.euron.one/api/v1/euri"
        }
        self.tracker = tracker

    def call_with_fallback(
        self,
        messages: list,
        model: str = DEFAULT_MODEL,
        system_prompt: str = None,
        temperature: float = 0.7,
        use_preferred_key: bool = True
    ) -> tuple:
        """Call API with automatic fallback to secondary key if rate limited.

        Returns: (response_text, key_used, tokens_used)
        """

        # Validate model
        if model not in AVAILABLE_MODELS:
            raise ValueError(f"Unknown model: {model}")

        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        # Determine which key to try first based on user preference
        primary_key_index = 0 if self.tracker.get_primary_key() == "key1" else 1
        secondary_key_index = 1 - primary_key_index

        # Try with primary key
        try:
            return self._call_euri_api(messages, model, temperature, key_index=primary_key_index)
        except RateLimitError:
            print(f"Primary API key rate limited for {model}, trying secondary key...")

        # Try with secondary key
        if self.tracker.preferences.get("fallback_enabled", True):
            try:
                return self._call_euri_api(messages, model, temperature, key_index=secondary_key_index)
            except RateLimitError:
                raise Exception(f"Both API keys are rate limited for {model}. Please try again later.")
        else:
            raise Exception(f"Primary API key rate limited and fallback is disabled.")

        raise Exception(f"API Error occurred.")

    def _call_euri_api(self, messages: list, model: str, temperature: float, key_index: int = 0) -> tuple:
        """Make actual API call to Euron and track usage.

        Returns: (response_text, key_used, tokens_used)
        """

        api_keys = self.api_keys.get("euri", [])
        if key_index >= len(api_keys):
            raise ValueError(f"API key index {key_index} out of range")

        api_key = api_keys[key_index]
        if not api_key:
            raise ValueError(f"API key at index {key_index} not configured")

        key_id = f"key{key_index + 1}"

        try:
            client = OpenAI(
                api_key=api_key,
                base_url=self.base_urls["euri"]
            )

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )

            # Track usage - handle if usage is None
            tokens_used = 0
            if hasattr(response, 'usage') and response.usage is not None:
                tokens_used = response.usage.total_tokens
                print(f"[API] {key_id} used {tokens_used} tokens for model {model}")
            else:
                print(f"[API] Warning: No usage data returned from API")
                tokens_used = len(response.choices[0].message.content) // 4  # Rough estimate

            # Log usage
            try:
                self.tracker.log_usage(key_id, tokens_used, model)
                print(f"[TRACKER] Logged {tokens_used} tokens to {key_id}")
            except Exception as track_err:
                print(f"[TRACKER] Error logging usage: {track_err}")

            return response.choices[0].message.content, key_id, tokens_used

        except Exception as e:
            print(f"[API ERROR] {str(e)}")
            raise e

    def validate_model(self, model: str) -> bool:
        """Check if model is available."""
        return model in AVAILABLE_MODELS

    def get_model_info(self, model: str):
        """Get information about a model."""
        return AVAILABLE_MODELS.get(model, None)

# Initialize client
api_client = UnifiedAPIClient()
