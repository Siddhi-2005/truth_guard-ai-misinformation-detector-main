from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import List, Optional, Literal

router = APIRouter()

# Define models matching the agent output (simplified or full)
# For proxying, we can just return the dict or define the full model.
# I'll define the full model to be safe and for documentation.

class InputData(BaseModel):
    original_text: str
    language: str
    source_url: Optional[str] = None

class Scores(BaseModel):
    supporting_score: float
    refuting_score: float

class EvidenceItem(BaseModel):
    title: str
    org: str
    url: str
    date: Optional[str] = None
    extract: str

class Explanation(BaseModel):
    public_summary: str
    technical_note: str

class ImageGeneration(BaseModel):
    requested: bool
    image_prompt: Optional[str] = None
    width: int
    height: int
    style: str

class AntigravityOutput(BaseModel):
    claim_id: str
    timestamp_utc: str
    input: InputData
    normalized_claim: str
    verdict: Literal["TRUE", "FALSE", "MISLEADING", "UNVERIFIED", "INCOMPLETE"]
    confidence: float
    scores: Scores
    evidence: List[EvidenceItem]
    explanation: Explanation
    recommended_actions: List[str]
    image_generation: ImageGeneration
    sources_checked: List[str]
    notes: Optional[str] = None

class VerifyRequest(BaseModel):
    claim: str
    image_requested: bool = False

ANTIGRAVITY_URL = os.getenv("ANTIGRAVITY_URL", "http://localhost:8002")

@router.post("/antigravity/verify", response_model=AntigravityOutput)
async def verify_claim(request: VerifyRequest):
    """
    Verify a claim using the Antigravity agent.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{ANTIGRAVITY_URL}/verify",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Antigravity service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
