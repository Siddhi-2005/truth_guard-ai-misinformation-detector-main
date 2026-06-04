# TruthGuard AI - Backend Setup Guide

## Phase 1: Local Setup (Completed ✓)

### What We've Done:
1. ✅ Created `backend/` directory structure
2. ✅ Copied LLM Auditor agent
3. ✅ Copied Deep Search agent
4. ✅ Copied Safety Plugins agent
5. ✅ Created FastAPI API Gateway

### Directory Structure:
```
backend/
├── llm-auditor/           # Verification Agent
├── deep-search/           # Research Agent  
├── safety-plugins/        # Content Filter
└── api-gateway/           # FastAPI Gateway
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    └── routers/
        ├── verify.py
        ├── research.py
        └── safety.py
```

## Next Steps:

### 1. Configure Environment Variables

Each agent needs a `.env` file. Copy the `.env.example` to `.env` in each directory:

**LLM Auditor** (`backend/llm-auditor/.env`):
```bash
cp backend/llm-auditor/.env.example backend/llm-auditor/.env
```
Then edit and add:
```bash
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_SEARCH_API_KEY=your-google-search-api-key
```

**Deep Search** (`backend/deep-search/.env`):
```bash
# Similar configuration
GOOGLE_API_KEY=your-gemini-api-key
```

**Safety Plugins** (`backend/safety-plugins/.env`):
```bash
GOOGLE_API_KEY=your-gemini-api-key
```

**API Gateway** (`backend/api-gateway/.env`):
```bash
cp backend/api-gateway/.env.example backend/api-gateway/.env
```

### 2. Install Dependencies

**For each agent** (run from agent directory):
```bash
cd backend/llm-auditor
poetry install

cd ../deep-search
poetry install  # or: uv sync

cd ../safety-plugins
poetry install
```

**For API Gateway**:
```bash
cd backend/api-gateway
pip install -r requirements.txt
```

### 3. Test Agents Locally

**Test LLM Auditor**:
```bash
cd backend/llm-auditor
adk web
```
Open browser to test the agent.

**Test Deep Search**:
```bash
cd backend/deep-search
adk web
```

**Test Safety Plugins**:
```bash
cd backend/safety-plugins
adk web
```

### 4. Run API Gateway

```bash
cd backend/api-gateway
python main.py
```

Gateway will be available at `http://localhost:8000`

### 5. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Verify claim
curl -X POST http://localhost:8000/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"claim_text": "The Earth is flat"}'
```

## Troubleshooting

### Issue: Poetry not found
```bash
pip install poetry
```

### Issue: ADK not found
```bash
pip install google-adk
```

### Issue: Missing API keys
Get your Gemini API key from: https://aistudio.google.com/apikey

## What's Next?

Once local testing works:
1. **Phase 2**: Deploy to Cloud Run
2. **Phase 3**: Integrate with Flutter app
3. **Phase 4**: Testing & optimization

## Current Status: ✅ Phase 1 Complete

You now have:
- 3 Python ADK agents ready to configure
- 1 FastAPI gateway ready to run
- All necessary files and structure

**Next Action**: Configure `.env` files with your API keys and test locally.
