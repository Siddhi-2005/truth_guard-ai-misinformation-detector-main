"""
Safety Router - Safety Plugins Integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class SafetyCheckRequest(BaseModel):
    content: str

class SafetyResult(BaseModel):
    is_safe: bool
    risk_score: float
    flags: list[str]
    explanation: str

# Safety Plugins service URL
SAFETY_PLUGINS_URL = os.getenv("SAFETY_PLUGINS_URL", "http://localhost:8003")

@router.post("/safety-check", response_model=SafetyResult)
async def check_safety(request: SafetyCheckRequest):
    """
    Check content safety using the Safety Plugins agent.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SAFETY_PLUGINS_URL}/check",
                json={"content": request.content}
            )
            response.raise_for_status()
            data = response.json()
            
            return SafetyResult(
                is_safe=data.get("is_safe", True),
                risk_score=data.get("risk_score", 0.0),
                flags=data.get("flags", []),
                explanation=data.get("explanation", "")
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Safety service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety check failed: {str(e)}")
