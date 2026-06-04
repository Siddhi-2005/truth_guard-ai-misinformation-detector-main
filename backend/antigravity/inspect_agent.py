import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from backend.antigravity.agent import antigravity_agent
    print("Agent imported successfully")
    print(f"Type: {type(antigravity_agent)}")
    print(f"Has 'run': {hasattr(antigravity_agent, 'run')}")
    print(f"Has 'query': {hasattr(antigravity_agent, 'query')}")
    print(f"Has 'invoke': {hasattr(antigravity_agent, 'invoke')}")
    print(f"Has '__call__': {hasattr(antigravity_agent, '__call__')}")
    print("Dir:", dir(antigravity_agent))
except Exception as e:
    print(f"Error importing agent: {e}")
