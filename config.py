import os

VOCAL_BRIDGE_API_KEY = os.environ.get("VOCAL_BRIDGE_API_KEY")
VOCAL_BRIDGE_URL = os.environ.get("VOCAL_BRIDGE_URL", "https://vocalbridgeai.com")
VOCAL_BRIDGE_AGENT_ID = os.environ.get("VOCAL_BRIDGE_AGENT_ID")
MODEL_NAME = os.environ.get("MODEL_NAME", "claude-sonnet-4-6")
