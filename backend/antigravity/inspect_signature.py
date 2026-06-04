import sys
import os
import inspect
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.antigravity.agent import antigravity_agent

try:
    sig = inspect.signature(antigravity_agent.run_async)
    print(f"Signature of run_async: {sig}")
except Exception as e:
    print(f"Error inspecting signature: {e}")
