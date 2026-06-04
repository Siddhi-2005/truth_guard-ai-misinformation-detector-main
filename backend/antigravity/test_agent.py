import asyncio
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.antigravity.agent import antigravity_agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

async def main():
    claim = "Chlorine in swimming pools kills the coronavirus."
    prompt = f"Claim: {claim}\nImage Requested: False"
    print(f"Testing claim: {claim}")
    runner = InMemoryRunner(agent=antigravity_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = UserContent(parts=[Part(text=prompt)])
    
    try:
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            print("Event received:")
            # print(event)
            if hasattr(event, 'content') and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)
    except Exception:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
