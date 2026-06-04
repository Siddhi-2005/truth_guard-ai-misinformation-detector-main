"""
Research Router - Deep Search Integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class ResearchRequest(BaseModel):
    query: str
    depth: str = "standard"

class ResearchResult(BaseModel):
    summary: str
    findings: list[dict]
    sources: list[str]

# Deep Search service URL
DEEP_SEARCH_URL = os.getenv("DEEP_SEARCH_URL", "http://localhost:8002")

@router.post("/research", response_model=ResearchResult)
async def deep_research(request: ResearchRequest):
    """
    Perform deep research using the Deep Search agent.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{DEEP_SEARCH_URL}/research",
                json={"query": request.query, "depth": request.depth}
            )
            response.raise_for_status()
            data = response.json()
            
            return ResearchResult(
                summary=data.get("summary", ""),
                findings=data.get("findings", []),
                sources=data.get("sources", [])
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Deep Search service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")
