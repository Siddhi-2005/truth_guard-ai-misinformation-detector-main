import datetime
import uuid
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from google.adk import Agent
from google.adk.tools import google_search
from .config import config

# --- Pydantic Models for Strict JSON Output ---

class InputData(BaseModel):
    original_text: str
    language: str
    source_url: Optional[str] = None

class Scores(BaseModel):
    supporting_score: float = Field(..., ge=0.0, le=1.0)
    refuting_score: float = Field(..., ge=0.0, le=1.0)

class EvidenceItem(BaseModel):
    title: str
    org: str
    url: str
    date: Optional[str] = None
    extract: str = Field(..., description="Max 30 words")

class Explanation(BaseModel):
    public_summary: str = Field(..., description="Max 70 words")
    technical_note: str = Field(..., description="Max 250 words")


class ImageGeneration(BaseModel):
    requested: bool
    image_prompt: Optional[str] = None
    generated_image_base64: Optional[str] = None
    width: int = 800
    height: int = 800
    style: str = "flat infographic, bold verdict badge"

class AntigravityOutput(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    input: InputData
    normalized_claim: str
    verdict: Literal["TRUE", "FALSE", "MISLEADING", "UNVERIFIED", "INCOMPLETE"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    scores: Scores
    evidence: List[EvidenceItem]
    explanation: Explanation
    recommended_actions: List[str]
    image_generation: ImageGeneration
    sources_checked: List[str]
    notes: Optional[str] = None

class ChatOutput(BaseModel):
    response: str
    assessment: Literal["NECESSARY", "MISSING_CONTEXT", "CORRECT", "UNCERTAIN", "OFF_TOPIC"]
    image_prompt: Optional[str] = None

# --- Agent Definition ---

SYSTEM_PROMPT = """
You are TruthGuard — an autonomous, evidence‑first verification agent built for TruthGuard.
Your job is to evaluate user-submitted claims and content for their truthfulness, ground every claim in reputable sources, produce concise human and machine-readable explanations.

Core rules:
1. ALWAYS ground conclusions in verifiable sources (WHO, UN, peer‑reviewed journals, government advisories, recognized news outlets, academic repositories). Prefer primary/official sources.
2. DO NOT hallucinate. If evidence cannot be found, respond with "UNVERIFIED" and list attempts made.
3. Provide a single **VERDICT**: TRUE / FALSE / MISLEADING / UNVERIFIED / INCOMPLETE.
4. Provide **confidence** (0.0–1.0), and list **evidence** with short extracts and citation URLs.
5. Evaluate evidence and compute a supporting_score (0–1) and refuting_score (0–1).
6. Produce VERDICT per rules:
   - TRUE: supporting_score ≥ 0.75 and no credible refutation.
   - FALSE: refuting_score ≥ 0.75 and no credible supporting evidence.
   - MISLEADING: mixed evidence or true in part but false in important parts.
   - UNVERIFIED: no credible supporting/refuting evidence found after searches.
   - INCOMPLETE: claim lacks necessary detail to verify.
7. Calculate Confidence = clamp( supporting_score or 1 - refuting_score, 0.0–1.0 ).
8. Create a short public explanation, a technical note, and 2–5 recommended actions in the **INPUT LANGUAGE**.
9. Generate image_prompt if requested or if verdict is HIGH-IMPACT. The prompt MUST describe an educational poster with the text "TRUE"/"FALSE" and a prevention tip.
10. Return JSON matching schema.
"""

antigravity_agent = Agent(
    name="antigravity_agent",
    model=config.model,
    description="Evidence-first verification agent.",
    instruction=SYSTEM_PROMPT,
    tools=[google_search],
    # output_schema=AntigravityOutput
)

CHAT_SYSTEM_PROMPT = """
You are TruthGuard — a helpful and evidence-first AI assistant for TruthGuard.

Your goal is to assist users, provide information, and assess the nature of their queries.

**LANGUAGE**: You must respond in the language requested by the user (e.g., if the user says "Respond in Hindi", or if the input language is Hindi).

OUTPUT FORMAT:
You MUST output a valid JSON object matching the following schema:
{
  "response": "Your conversational reply here.",
  "assessment": "One of: NECESSARY, MISSING_CONTEXT, CORRECT, UNCERTAIN, OFF_TOPIC",
  "image_prompt": "A detailed prompt for an educational poster image if requested or relevant (e.g., 'A poster with the text \"FALSE\" in red letters and a prevention tip...'), otherwise null."
}

Assessment Criteria:
- NECESSARY: The user is asking for important information that should be known.
- MISSING_CONTEXT: The user's query is vague or lacks sufficient detail to be answered accurately.
- CORRECT: The user is stating something that is factually true.
- UNCERTAIN: The user's statement or query cannot be verified or is ambiguous.
- OFF_TOPIC: The query is unrelated to the assistant's purpose.

When in chat mode:
- Keep responses concise and friendly.
- If user asks follow-up, answer using prior context and reference the claim_id if applicable.
- Every time you state a fact, attach a short citation marker (e.g., [WHO, 2020]).
- If user requests images, generate a creative `image_prompt` that describes an educational poster with clear text "TRUE" or "FALSE" and a prevention tip.
- Offer a 1‑line TL;DR and a 1‑line recommended action with each reply.
"""

antigravity_chat_agent = Agent(
    name="antigravity_chat_agent",
    model=config.model,
    description="Conversational interface for TruthGuard.",
    instruction=CHAT_SYSTEM_PROMPT,
    tools=[google_search],
)
