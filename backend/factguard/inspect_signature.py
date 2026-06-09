import sys
import os
import inspect
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.factguard.agent import factguard_agent

try:
    sig = inspect.signature(factguard_agent.run_async)
    print(f"Signature of run_async: {sig}")
except Exception as e:
    print(f"Error inspecting signature: {e}")
