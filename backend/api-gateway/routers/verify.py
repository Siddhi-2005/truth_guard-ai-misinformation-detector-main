"""
Verification Router - LLM Auditor Integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class VerifyRequest(BaseModel):
    claim_text: str

class VerificationResult(BaseModel):
    is_true: bool
    summary: str
    detailed_explanation: str
    sources: list[str]
    confidence: float

# LLM Auditor service URL (will be Cloud Run URL in production)
LLM_AUDITOR_URL = os.getenv("LLM_AUDITOR_URL", "http://localhost:8001")

@router.post("/verify", response_model=VerificationResult)
async def verify_claim(request: VerifyRequest):
    """
    Verify a claim using the LLM Auditor agent.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{LLM_AUDITOR_URL}/verify",
                json={"claim": request.claim_text}
            )
            response.raise_for_status()
            data = response.json()
            
            return VerificationResult(
                is_true=data.get("is_true", False),
                summary=data.get("summary", ""),
                detailed_explanation=data.get("explanation", ""),
                sources=data.get("sources", []),
                confidence=data.get("confidence", 0.0)
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"LLM Auditor service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
