import os

VOCAL_BRIDGE_API_KEY = os.environ.get("VOCAL_BRIDGE_API_KEY")
VOCAL_BRIDGE_URL = os.environ.get("VOCAL_BRIDGE_URL", "https://vocalbridgeai.com")
VOCAL_BRIDGE_AGENT_ID = os.environ.get("VOCAL_BRIDGE_AGENT_ID")
TOOL_SECRET = os.environ.get("TOOL_SECRET", "dev-secret-change-me")
WIKI_DIR = os.environ.get("WIKI_DIR")  # defaults handled in tools/wiki.py
MODEL_NAME = os.environ.get("MODEL_NAME", "claude-sonnet-4-6")
