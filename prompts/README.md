## How prompt/config changes work

The prompt and agent settings live on **VocalBridge's servers**, not locally.
These local files are snapshots for version control.

### To update the agent:

```python
# Prompt changes — use field name "prompt" (not "custom_prompt"):
requests.patch("https://vocalbridgeai.com/api/v1/agent",
    headers={"X-API-Key": VOCAL_BRIDGE_API_KEY, "Content-Type": "application/json"},
    json={"prompt": "new prompt text"})

# Settings changes (VAD, silence, etc):
requests.patch("https://vocalbridgeai.com/api/v1/agent",
    headers={"X-API-Key": VOCAL_BRIDGE_API_KEY, "Content-Type": "application/json"},
    json={"model_settings": {"realtime": {"vad_threshold": "0.85"}}})

# Read current config:
requests.get("https://vocalbridgeai.com/api/v1/agent",
    headers={"X-API-Key": VOCAL_BRIDGE_API_KEY})
```

### API quirks
- PATCH field for prompt is `prompt`, but GET returns it as `custom_prompt`
- `style` field (Chatty/Focused) can't be changed via API — use the GUI
- Must use `https://vocalbridgeai.com` (http redirects and breaks POST)
- The .env has an agent-scoped key (not account-level), so no X-Agent-Id header needed
- VocalBridge CLI (v0.1.2) has a bug with agent-scoped key auth — use the API directly
