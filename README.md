# artistic-penguin
Spring 2026 Hackathon: Building an Agent

## Team
* Mahya
* Noah
* Sean

## Context
Participating in the Spring 2026 Hackathon at work. We can build something that's not specific to our job (our preference). 

**The Mission:** Your goal is to design, build, and deploy a functional AI Agent by Friday at 1:00 PM. We want you to leave the day-to-day corporate use cases at the door and build something weird, wild, or personally useful—think fantasy football GMs, meal planners, or even a neutral diplomat for household chores. We will wrap up this Friday, April 10th, with a live Demo Day starting at 1:00 PM. You’ll be judged on Agentic Behavior (30%), the "Wow" Factor (30%), Everyday Utility (20%), and Demo Quality (20%).

Bias toward shipping working systems over perfect ones.

## Architecture

**What runs where:**

- **Your machine (localhost:5050):** Flask server (`app.py`) + static HTML/JS frontend (`static/index.html`)
- **VocalBridge cloud:** The actual AI voice agent — prompt, voice model (ElevenLabs), GPT Realtime, VAD settings
- **LiveKit cloud:** WebRTC infrastructure that carries the audio between your browser and the agent

**How a call works:**

1. User clicks "Start Conversation" in the browser
2. Browser hits Flask backend (`/api/voice-token`), which calls VocalBridge API and returns a LiveKit token
3. Browser connects directly to LiveKit via WebRTC using that token
4. LiveKit routes audio to/from VocalBridge's agent
5. Transcript and heartbeat data come back over a LiveKit data channel and render in the UI

## Project Structure

| File | What it does |
|------|-------------|
| `app.py` | Flask server — serves UI, proxies token requests |
| `static/index.html` | Voice UI — connect/mute/end, live transcript |
| `config.py` | Reads env vars |
| `prompts/system_prompt.txt` | Local copy of the agent prompt (source of truth is VocalBridge) |
| `prompts/agent_config.json` | Local copy of agent settings (same caveat) |
| `.env` | API key (gitignored) |

> **Note:** The prompt and agent config live on VocalBridge's servers. The local `prompts/` files are snapshots for version control. Changes are pushed via their API, not by editing local files.

## Setup

```bash
cp .env.example .env
# Add your VocalBridge agent-scoped API key to .env
pip install -r requirements.txt
python3 app.py
# Open http://localhost:5050
```
