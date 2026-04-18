from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from pathlib import Path

from unified_api_client import api_client
from api_usage_tracker import tracker
from models_config import get_all_models, DEFAULT_MODEL, get_models_by_category
from conversion_prompts import (
    HUMANIZER_PROMPT,
    ARCHITECT_PROMPT,
    COMPLIANCE_PROMPT,
    DOCUMENTATION_PROMPT
)

app = FastAPI(title="AI Text to Human-Readable Pipeline")

# Serve static files
static_dir = Path(__file__).parent / "public"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ConversionRequest(BaseModel):
    text: str
    mode: str = "humanize"  # humanize, architect, compliance, designer
    model: str = DEFAULT_MODEL
    temperature: float = 0.7

class ConversionResponse(BaseModel):
    original: str
    converted: str
    mode: str
    model: str
    tokens_used: int = 0
    api_key_used: str = ""

PROMPTS = {
    "humanize": HUMANIZER_PROMPT,
    "architect": ARCHITECT_PROMPT,
    "compliance": COMPLIANCE_PROMPT,
    "designer": DOCUMENTATION_PROMPT
}

@app.get("/")
async def root():
    """Serve the main website."""
    return FileResponse(static_dir / "index.html")

@app.post("/api/convert", response_model=ConversionResponse)
async def convert_text(request: ConversionRequest):
    """Convert AI text to human-readable format with specified mode and model."""

    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if request.mode not in PROMPTS:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Choose from: {list(PROMPTS.keys())}")

    if not api_client.validate_model(request.model):
        raise HTTPException(status_code=400, detail=f"Invalid model: {request.model}")

    try:
        system_prompt = PROMPTS[request.mode]
        messages = [{"role": "user", "content": request.text}]

        result, key_used, tokens_used = api_client.call_with_fallback(
            messages,
            model=request.model,
            system_prompt=system_prompt,
            temperature=request.temperature
        )

        return ConversionResponse(
            original=request.text,
            converted=result,
            mode=request.mode,
            model=request.model,
            tokens_used=tokens_used,
            api_key_used=key_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/usage")
async def get_usage():
    """Get API usage stats for both keys."""
    return {
        "usage": tracker.get_usage_stats(),
        "preferences": tracker.get_preferences()
    }

class PreferencesRequest(BaseModel):
    primary_key: str = None
    limit_key1: int = None
    limit_key2: int = None
    fallback_enabled: bool = None

@app.post("/api/preferences")
async def update_preferences(request: PreferencesRequest):
    """Update API preferences."""
    print(f"[PREFS] Received: {request}")
    tracker.set_preferences(
        request.primary_key,
        request.limit_key1,
        request.limit_key2,
        request.fallback_enabled
    )
    prefs = tracker.get_preferences()
    print(f"[PREFS] Updated to: {prefs}")
    return {
        "status": "updated",
        "preferences": prefs
    }

@app.post("/api/reset-usage")
async def reset_usage():
    """Reset daily usage stats."""
    tracker.reset_daily_stats()
    return {
        "status": "reset",
        "usage": tracker.get_usage_stats()
    }

@app.get("/api/modes")
async def get_modes():
    """Get available conversion modes."""
    return {
        "modes": {
            "humanize": "Convert AI text to natural, human-readable prose",
            "architect": "Get architectural guidance for documentation systems",
            "compliance": "Check documentation for compliance issues",
            "designer": "Design information architecture and documentation structure"
        }
    }

@app.get("/api/models")
async def get_models():
    """Get all available AI models grouped by provider."""
    return {
        "models": get_all_models(),
        "grouped": get_models_by_category(),
        "default": DEFAULT_MODEL
    }

@app.get("/api/models/{model_id}")
async def get_model_info(model_id: str):
    """Get information about a specific model."""
    info = api_client.get_model_info(model_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
    return {"model": model_id, **info}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
