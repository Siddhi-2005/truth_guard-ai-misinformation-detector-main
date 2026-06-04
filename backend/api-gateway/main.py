"""
TruthGuard AI - API Gateway
Unified REST API for Python ADK agents
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="TruthGuard AI API Gateway",
    description="Unified API for misinformation detection agents",
    version="1.0.0"
)

# CORS configuration for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class VerifyRequest(BaseModel):
    claim_text: str

class VerificationResult(BaseModel):
    is_true: bool
    summary: str
    detailed_explanation: str
    sources: list[str]
    confidence: float

class ResearchRequest(BaseModel):
    query: str
    depth: str = "standard"  # standard, deep

class ResearchResult(BaseModel):
    summary: str
    findings: list[dict]
    sources: list[str]

class SafetyCheckRequest(BaseModel):
    content: str

class SafetyResult(BaseModel):
    is_safe: bool
    risk_score: float
    flags: list[str]
    explanation: str

@app.get("/")
async def root():
    return {
        "service": "TruthGuard AI API Gateway",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import routers
from routers import verify, research, safety, truthguard

app.include_router(verify.router, prefix="/api/v1", tags=["verification"])
app.include_router(research.router, prefix="/api/v1", tags=["research"])
app.include_router(safety.router, prefix="/api/v1", tags=["safety"])
app.include_router(truthguard.router, prefix="/api/v1", tags=["truthguard"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
