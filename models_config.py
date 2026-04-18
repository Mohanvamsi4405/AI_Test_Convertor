# Available models from multiple providers
AVAILABLE_MODELS = {
    # OpenAI
    "gpt-4.1-nano": {
        "provider": "openai",
        "name": "GPT 4.1 Nano",
        "type": "text-generation",
        "category": "OpenAI"
    },
    "gpt-4.1-mini": {
        "provider": "openai",
        "name": "GPT 4.1 Mini",
        "type": "text-generation",
        "category": "OpenAI"
    },
    "openai/gpt-oss-20b": {
        "provider": "openai",
        "name": "GPT-OSS 20B",
        "type": "text-generation",
        "category": "OpenAI"
    },
    "openai/gpt-oss-120b": {
        "provider": "openai",
        "name": "GPT-OSS 120B",
        "type": "text-generation",
        "category": "OpenAI"
    },

    # Google
    "gemini-2.0-flash": {
        "provider": "google",
        "name": "Gemini 2.0 Flash",
        "type": "text-generation",
        "category": "Google"
    },
    "gemini-2.5-pro": {
        "provider": "google",
        "name": "Gemini 2.5 Pro",
        "type": "text-generation",
        "category": "Google"
    },
    "gemini-2.5-flash": {
        "provider": "google",
        "name": "Gemini 2.5 Flash",
        "type": "text-generation",
        "category": "Google"
    },

    # Meta
    "llama-4-scout-17b-16e-instruct": {
        "provider": "meta",
        "name": "Llama 4 Scout",
        "type": "text-generation",
        "category": "Meta"
    },
    "llama-3.3-70b-versatile": {
        "provider": "meta",
        "name": "Llama 3.3 70B",
        "type": "text-generation",
        "category": "Meta"
    },
    "llama-3.1-8b-instant": {
        "provider": "meta",
        "name": "Llama 3.1 8B Instant",
        "type": "text-generation",
        "category": "Meta"
    },

    # Groq
    "groq/compound": {
        "provider": "groq",
        "name": "Groq Compound",
        "type": "text-generation",
        "category": "Groq"
    },
    "groq/compound-mini": {
        "provider": "groq",
        "name": "Groq Compound Mini",
        "type": "text-generation",
        "category": "Groq"
    },

    # Alibaba
    "qwen/qwen3-32b": {
        "provider": "alibaba",
        "name": "Qwen 3 32B",
        "type": "text-generation",
        "category": "Alibaba"
    },

    # Sarvam
    "sarvam-m": {
        "provider": "sarvam",
        "name": "Sarvam M",
        "type": "text-generation",
        "category": "Sarvam"
    },
}

# Default model
DEFAULT_MODEL = "gemini-2.5-flash"

def get_model_info(model_id: str):
    """Get information about a specific model."""
    return AVAILABLE_MODELS.get(model_id, None)

def get_models_by_category():
    """Group models by provider/category."""
    grouped = {}
    for model_id, info in AVAILABLE_MODELS.items():
        category = info["category"]
        if category not in grouped:
            grouped[category] = []
        grouped[category].append({
            "id": model_id,
            "name": info["name"]
        })
    return grouped

def get_all_models():
    """Get all available models."""
    return [
        {
            "id": model_id,
            "name": info["name"],
            "provider": info["provider"],
            "category": info["category"]
        }
        for model_id, info in AVAILABLE_MODELS.items()
    ]
