import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from backend.factguard.agent import factguard_agent
    print("Agent imported successfully")
    print(f"Type: {type(factguard_agent)}")
    print(f"Has 'run': {hasattr(factguard_agent, 'run')}")
    print(f"Has 'query': {hasattr(factguard_agent, 'query')}")
    print(f"Has 'invoke': {hasattr(factguard_agent, 'invoke')}")
    print(f"Has '__call__': {hasattr(factguard_agent, '__call__')}")
    print("Dir:", dir(factguard_agent))
except Exception as e:
    print(f"Error importing agent: {e}")
