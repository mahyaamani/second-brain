# "🧙🏻‍♂️ Hacker" — AI Engineer

Participating in the Spring 2026 Hackathon for my team at work. We can build something that's not specific to our job (our preference). 

The Mission: Your goal is to design, build, and deploy a functional AI Agent by Friday at 1:00 PM. We want to leave the day-to-day corporate use cases at the door and build something weird, wild, or personally useful—think fantasy football GMs, meal planners, or even a neutral diplomat for household chores. We will wrap up this Friday, April 10th, with a live Demo Day starting at 1:00 PM. 

You’ll be judged on
* Agentic Behavior (30%)
* The "Wow" Factor (30%)
* Everyday Utility (20%)
* Demo Quality (20%).

Bias toward shipping working systems over perfect ones.

---

## Working Style

- **Approach**: Implement → test → iterate. Don't overthink architecture before running code.
- **Communication**: Technical depth welcome. Skip the obvious context. Be extremely concise; think: "why use more word when few word do trick"
- **Autonomy**: Make reversible decisions without asking. Flag irreversible ones.

### Decision Rules
When uncertain:
- Run it and see what breaks
- Simpler model first, upgrade if needed
- Ship working v1 before adding features

---

## Core Behaviors

- Always test LLM calls with real API before marking complete
- Log token costs for any new AI feature (track spend)
- Never hardcode model names — use config/env vars
- Error handling for: rate limits, API timeouts, hallucinated output formats
- Confirm before: deleting data, posting to external services, making purchases

---

## AI/LLM Stack

- **Primary model**: Claude Sonnet 4.6 as I'm coding. Open to opinions on what we deploy
- **Fallback model**: Sonnet or even Haiku for fast/cheap tasks while coding. Open on what we deploy
- **Framework**: I'm using Claude Code to develop, and probably using Vocal Bridge for voice. I'm pretty open to frameworks; I just want to ship something that works fast and without costing myself a bunch of money
- **Orchestration**: Open right now
- **Memory**: Open right now

---

## Tech Stack

- **Backend**: Our preference for this competition is to build something for outside of work and so we prefer to work in GitHub, use Python, Claude code, etc. We're not super tied to other tech stack details
- **Frontend**: Open right now
- **Database**: Open right now
- **Queue/Jobs**: Open right now
- **Deployment**: Open right now

---

## Project Structure

Nothing written so far. Once we start building, we can fill something like this out:

| What | Where |
|------|-------|
| Agent code | [path] |
| Prompts | [path] |
| Skills/tools | [path] |
| Config | [path] |

---

## LLM-Specific Rules

- Test prompts with edge cases before committing
- Never expose raw API keys in logs or output
- Rate limit retries with exponential backoff
- Cap token output where possible (cost + latency)
- Validate structured output (JSON schema or pydantic) before trusting it

---

## Secrets Location

- API keys: Haven't dropped any for you, but will update when we do
- Never in: code, comments, git history
