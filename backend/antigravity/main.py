from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .agent import antigravity_agent, antigravity_chat_agent, AntigravityOutput
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
import json
from typing import Optional

import sys
import os

# Add sibling directories to path to import other agents
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(backend_dir, "deep-search"))
sys.path.append(os.path.join(backend_dir, "llm-auditor"))

from fastapi.middleware.cors import CORSMiddleware

# Import agents
# Note: We use try-except to avoid crashing if dependencies are missing for other agents
agents = {}

# 1. Antigravity (TruthGuard)
agents["TruthGuard"] = antigravity_chat_agent

# 2. Deep Search
try:
    from app.agent import root_agent as deep_search_agent
    agents["Deep Search"] = deep_search_agent
except ImportError as e:
    print(f"Could not import Deep Search agent: {e}")

# 3. LLM Auditor
try:
    from llm_auditor.agent import llm_auditor as llm_auditor_agent
    agents["LLM Auditor"] = llm_auditor_agent
except ImportError as e:
    print(f"Could not import LLM Auditor agent: {e}")


app = FastAPI(title="Antigravity Agent API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Antigravity Agent API is running"}

class VerifyRequest(BaseModel):
    claim: str
    image_requested: bool = False
    language: str = "English"

@app.post("/verify", response_model=AntigravityOutput)
async def verify(request: VerifyRequest):
    try:
        # Construct the input for the agent
        prompt = f"Claim: {request.claim}\nImage Requested: {request.image_requested}\nLanguage: {request.language}"
        
        runner = InMemoryRunner(agent=antigravity_agent)
        session = await runner.session_service.create_session(
            app_name=runner.app_name, user_id="api_user"
        )
        content = UserContent(parts=[Part(text=prompt)])
        
        final_text = ""
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text += part.text
        
        # Parse the JSON output
        # The agent is instructed to output JSON.
        # We might need to clean it if it contains markdown code blocks.
        cleaned_text = final_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
            
        cleaned_text = cleaned_text.strip()
        

        try:
            data = json.loads(cleaned_text)
            output = AntigravityOutput(**data)

            # Image Generation (Nano Banana / Gemini 2.5 Flash Image)
            if output.image_generation and output.image_generation.image_prompt:
                try:
                    from google.genai import Client
                    import base64
                    import os
                    
                    client = Client(api_key=os.environ.get("GOOGLE_API_KEY"))
                    # Using gemini-2.5-flash-image (Nano Banana)
                    response = client.models.generate_images(
                        model='gemini-2.5-flash-image',
                        prompt=output.image_generation.image_prompt,
                        config={'number_of_images': 1}
                    )
                    if response.generated_images:
                        image_bytes = response.generated_images[0].image.image_bytes
                        b64_img = base64.b64encode(image_bytes).decode('utf-8')
                        output.image_generation.generated_image_base64 = b64_img
                        print("Image generated successfully with Nano Banana.")
                except Exception as img_err:
                    print(f"Image generation failed: {img_err}")
                    # Fallback or just ignore, the prompt is still there
            
            return output
        except json.JSONDecodeError:
             # Fallback: try to find JSON object if there's extra text
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}')
            if start != -1 and end != -1:
                json_str = cleaned_text[start:end+1]
                data = json.loads(json_str)
                output = AntigravityOutput(**data)
                
                # Image Generation (Nano Banana / Gemini 2.5 Flash Image) - Copy of logic
                if output.image_generation and output.image_generation.image_prompt:
                    try:
                        from google.genai import Client
                        import base64
                        import os
                        
                        client = Client(api_key=os.environ.get("GOOGLE_API_KEY"))
                        response = client.models.generate_images(
                            model='gemini-2.5-flash-image',
                            prompt=output.image_generation.image_prompt,
                            config={'number_of_images': 1}
                        )
                        if response.generated_images:
                            image_bytes = response.generated_images[0].image.image_bytes
                            b64_img = base64.b64encode(image_bytes).decode('utf-8')
                            output.image_generation.generated_image_base64 = b64_img
                            print("Image generated successfully with Nano Banana.")
                    except Exception as img_err:
                        print(f"Image generation failed: {img_err}")

                return output
            else:
                raise ValueError(f"Could not parse JSON from response: {cleaned_text}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"
    language: str = "English"
    agent_name: str = "TruthGuard"

class ChatResponse(BaseModel):
    response: str
    assessment: str
    image_prompt: Optional[str] = None

@app.post("/chat")
async def chat(request: ChatRequest):
    async def event_generator():
        try:
            selected_agent = agents.get(request.agent_name, antigravity_chat_agent)
            runner = InMemoryRunner(agent=selected_agent)
            session = await runner.session_service.create_session(
                app_name=runner.app_name, user_id="api_user", session_id=request.session_id
            )
            
            # Adjust prompt based on agent
            if request.agent_name == "Deep Search":
                # Deep Search expects a research topic
                prompt_text = f"Research Topic: {request.message}\n(Language: {request.language})"
            elif request.agent_name == "LLM Auditor":
                # LLM Auditor expects a claim or text to audit
                prompt_text = f"Audit this: {request.message}\n(Language: {request.language})"
            else:
                # TruthGuard
                prompt_text = f"{request.message}\n(Respond in {request.language})"

            content = UserContent(parts=[Part(text=prompt_text)])
            
            # Immediate feedback
            yield json.dumps({"type": "log", "message": "Starting analysis..."}) + "\n"

            final_text = ""
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content,
            ):
                # Log tool use or thoughts if available
                # Inspect event for specific agent activities
                log_message = "Processing..."
                event_str = str(event)
                
                # Generic fallback for any tool use
                if "tool_call" in event_str:
                     log_message = "Using Tool..."

                if request.agent_name == "Deep Search":
                    # Deep Search specific logs
                    if "plan_generator" in event_str:
                        log_message = "Generating Research Plan..."
                    elif "section_researcher" in event_str:
                         # Try to extract section info if possible, otherwise generic
                        log_message = "Researching Section..."
                    elif "google_search" in event_str:
                        log_message = "Searching the Web..."
                    elif "report_composer" in event_str:
                        log_message = "Composing Final Report..."
                    elif "enhanced_search_executor" in event_str:
                        log_message = "Executing Enhanced Search..."
                    elif "interactive_planner_agent" in event_str:
                        log_message = "Refining Plan..."
                elif request.agent_name == "LLM Auditor":
                     if "critic_agent" in event_str:
                        log_message = "Critiquing Content..."
                     elif "reviser_agent" in event_str:
                        log_message = "Revising Content..."
                     elif "google_search" in event_str:
                        log_message = "Verifying Claims..."
                else:
                    # TruthGuard
                    if "google_search" in event_str:
                        log_message = "Verifying with Google Search..."
                    elif "model_call" in event_str:
                        log_message = "Analyzing Evidence..."
                    elif "tool_result" in event_str:
                        log_message = "Processing Search Results..."
                
                # Send log event
                # We only send if it's a meaningful state change or periodically?
                # For now, streaming every event as a potential log update is fine, 
                # frontend can debounce or just show the latest.
                yield json.dumps({"type": "log", "message": log_message}) + "\n"

            # Parse the JSON output
            cleaned_text = final_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
                
            cleaned_text = cleaned_text.strip()
            
            response_data = {}
            try:
                response_data = json.loads(cleaned_text)
            except json.JSONDecodeError:
                 # Fallback: try to find JSON object if there's extra text
                start = cleaned_text.find('{')
                end = cleaned_text.rfind('}')
                if start != -1 and end != -1:
                    json_str = cleaned_text[start:end+1]
                    response_data = json.loads(json_str)
                else:
                    # Fallback for plain text response
                    response_data = {
                        "response": final_text,
                        "assessment": "UNCERTAIN",
                        "image_prompt": None
                    }
            
            yield json.dumps({"type": "result", "data": response_data}) + "\n"

        except Exception:
            import traceback
            traceback.print_exc()
            yield json.dumps({"type": "error", "message": "An internal server error occurred"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
