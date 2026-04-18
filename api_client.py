import os
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv

load_dotenv()

class EuronClient:
    def __init__(self):
        self.api_key1 = os.getenv("EURI_API_KEY1")
        self.api_key2 = os.getenv("EURI_API_KEY2")
        self.base_url = "https://api.euron.one/api/v1/euri"
        self.model = "gemini-2.5-flash"

    def call_with_fallback(self, messages: list, system_prompt: str = None) -> str:
        """Call Euron API with automatic fallback to second key if rate limited."""

        # Try first API key
        try:
            client = OpenAI(api_key=self.api_key1, base_url=self.base_url)
            response = self._create_completion(client, messages, system_prompt)
            return response
        except RateLimitError:
            print("First API key rate limited, switching to second key...")
            pass

        # Fallback to second API key
        try:
            client = OpenAI(api_key=self.api_key2, base_url=self.base_url)
            response = self._create_completion(client, messages, system_prompt)
            return response
        except RateLimitError:
            raise Exception("Both API keys are rate limited. Please try again later.")
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")

    def _create_completion(self, client: OpenAI, messages: list, system_prompt: str) -> str:
        """Helper to create completion with optional system prompt."""
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

# Initialize client
euron_client = EuronClient()
