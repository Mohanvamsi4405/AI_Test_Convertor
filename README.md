# AI Text to Human-Readable Pipeline

A powerful web-based tool that converts AI-generated text into natural, human-readable prose while preserving compliance. Choose from 20+ AI models across multiple providers. Built with FastAPI backend and modern HTML/CSS/JS frontend.

## Features

✨ **4 Conversion Modes:**
- **Humanize**: Convert AI text to conversational, natural-sounding prose
- **Architect**: Get guidance designing documentation systems and AI pipelines
- **Compliance**: Check documentation for regulatory and legal requirements
- **Designer**: Create clear information architecture and content structure

🤖 **20+ AI Models from Multiple Providers:**
- **OpenAI**: GPT-4.1 Nano/Mini, GPT-OSS 20B/120B
- **Google**: Gemini 2.0/2.5 Flash, Gemini 2.5 Pro
- **Meta**: Llama 4 Scout, Llama 3.3 70B, Llama 3.1 8B
- **Groq**: Groq Compound & Mini
- **Alibaba**: Qwen 3 32B
- **Sarvam**: Sarvam M

⚙️ **Advanced Controls:**
- Select any model from the dropdown
- Adjust creativity level (0 = precise, 1 = creative)
- View pricing and provider info for each model
- Default to Gemini 2.5 Flash for best performance/cost

🔄 **Smart API Management:**
- Automatic fallback between two Euron API keys
- Handles rate limiting gracefully
- Real-time status updates

💾 **Local History:**
- Automatic conversion history (last 20 items)
- Browser-based storage (localStorage)
- Track which model was used for each conversion
- Quick access to recent conversions

🎯 **Professional Interface:**
- Modern, responsive UI
- Model selection with categories by provider
- Creativity/temperature slider
- Keyboard shortcuts (Ctrl+Enter to convert)
- Copy to clipboard functionality

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create or update `.env` file (already has your keys):
```
EURI_API_KEY1=euri-47166e57a9250848e4c301d530fc4f533f44371737e26b219ef8303e46613e72
EURI_API_KEY2=euri-87efdfafe7560ba699ad389e09e1998a5a0565f3a39286678a55863b2675855a
```

### 3. Run the Server
```bash
python backend.py
```

The server will start at `http://localhost:8000`

## How to Use

1. **Open the website** - Navigate to `http://localhost:8000` in your browser
2. **Select AI Model** - Pick from 20+ models across OpenAI, Google, Meta, Groq, etc.
3. **Adjust Creativity** - Use the slider (0 = precise, 1 = creative)
4. **Select Conversion Mode** - Click one of the four buttons (Humanize, Architect, Compliance, Designer)
5. **Paste your text** - Add AI-generated or formal text in the input box
6. **Convert** - Click "✨ Convert" or press `Ctrl+Enter`
7. **Copy result** - Use the 📋 button to copy converted text
8. **View history** - Click on previous conversions in the history section to see which model was used

## API Endpoints

### Convert Text
```bash
POST /api/convert
Content-Type: application/json

{
    "text": "Your text here",
    "mode": "humanize",  # humanize, architect, compliance, designer
    "model": "gemini-2.5-flash",  # Any model ID from /api/models
    "temperature": 0.7  # 0-1, default 0.7
}
```

Response:
```json
{
    "original": "Your text here",
    "converted": "Converted text here",
    "mode": "humanize",
    "model": "gemini-2.5-flash"
}
```

### Get Available Models
```bash
GET /api/models
```

Returns all models grouped by provider with pricing info.

### Get Specific Model Info
```bash
GET /api/models/gemini-2.5-flash
```

### Get Available Modes
```bash
GET /api/modes
```

### Health Check
```bash
GET /health
```

## Project Structure
```
.
├── backend.py              # FastAPI application
├── api_client.py          # Euron API client with fallback logic
├── conversion_prompts.py   # System prompts for each mode
├── requirements.txt        # Python dependencies
├── .env                   # API keys
└── public/
    ├── index.html         # Main webpage
    ├── style.css          # Styling
    └── script.js          # Frontend logic
```

## Conversion Modes Explained

### 1. **Humanize**
Transforms formal, AI-generated text into natural human speech while maintaining accuracy and compliance. Perfect for:
- Converting model outputs to documentation
- Making technical writing more engaging
- Simplifying complex explanations

### 2. **Architect**
Provides expert guidance on designing documentation systems and AI integration. Includes:
- System architecture recommendations
- Technology stack guidance
- Implementation phases
- Team structure recommendations
- Quality metrics

### 3. **Compliance**
Audits documentation for regulatory and legal requirements:
- GDPR, HIPAA, SOC2 compliance
- Legal language and liability issues
- Data privacy verification
- Accessibility checks
- Provides risk assessment and remediation

### 4. **Designer**
Creates information architecture and content structure:
- Audience persona definition
- Content hierarchy design
- Progressive disclosure strategies
- Example and template design
- Navigation and findability optimization

## Advanced Configuration

### Add New Models
Edit `models_config.py` and add to `AVAILABLE_MODELS`:

```python
AVAILABLE_MODELS = {
    "your-model-id": {
        "provider": "provider_name",
        "name": "Display Name",
        "pricing": "$X/$Y per 1M tokens",
        "type": "text-generation",
        "category": "Your Provider"
    },
    ...
}
```

### Change Default Model
Edit `models_config.py`:
```python
DEFAULT_MODEL = "your-preferred-model"
```

### Change API Base URL
Edit `unified_api_client.py`:
```python
self.base_urls = {
    "euri": "https://your-custom-endpoint.com/api/v1"
}
```

### Add Custom System Prompts
Edit `conversion_prompts.py` and add new prompts, then update `backend.py`:

```python
PROMPTS = {
    "humanize": HUMANIZER_PROMPT,
    "your_new_mode": YOUR_NEW_PROMPT,
}
```

## Troubleshooting

**Error: "Both API keys are rate limited"**
- Wait a few minutes before retrying
- Check your API key quotas in Euron dashboard

**Error: "Port 8000 already in use"**
- Change port in `backend.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`

**API calls failing**
- Verify `.env` file has correct API keys
- Check internet connection
- Verify Euron API status

## Performance Tips

1. **Longer texts** may take more time - be patient
2. **Keep conversions focused** - smaller chunks convert faster
3. **Browser history** is stored locally - clearing cache removes history
4. **Rate limiting** - space out requests if hitting limits

## Security Notes

- API keys are stored in `.env` and never exposed to frontend
- All API calls go through the FastAPI backend
- No user data is logged or stored on servers
- Local history uses browser localStorage only

## License

Use freely for your ML, documentation, and compliance work.
