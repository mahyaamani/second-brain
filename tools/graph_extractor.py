"""
Knowledge graph extractor.

Uses a fast Claude call to extract nodes and edges from a Q&A exchange,
showing how the answer was built from connected concepts.
"""

import json
import anthropic

client = anthropic.Anthropic()


def extract_knowledge_graph(question: str, response: str, tool_calls: list[str]) -> dict:
    """
    Extract a knowledge graph from a Q&A exchange.

    Args:
        question:   The user's input.
        response:   The assistant's response text.
        tool_calls: List of tool call summaries, e.g. ["read_wiki_page(title='fitness/goals')"]

    Returns:
        {"nodes": [...], "edges": [...]}
        Node: {"id": str, "label": str, "type": str}
        Edge: {"from": str, "to": str, "label": str}
    """
    tools_text = "\n".join(f"- {t}" for t in tool_calls) if tool_calls else "- (no tools used)"

    prompt = f"""Analyze this AI assistant exchange and extract a knowledge graph showing how the answer was built.

USER INPUT: {question}

TOOLS USED:
{tools_text}

ASSISTANT RESPONSE (truncated):
{response[:2500]}

Return ONLY valid JSON (no markdown, no explanation) matching this exact schema:
{{
  "nodes": [
    {{"id": "q", "label": "User question", "type": "question"}},
    {{"id": "c1", "label": "Concept name", "type": "concept"}},
    {{"id": "w1", "label": "wiki page title", "type": "wiki_page"}},
    {{"id": "s1", "label": "search topic", "type": "web_source"}}
  ],
  "edges": [
    {{"from": "q", "to": "c1", "label": "explores"}},
    {{"from": "w1", "to": "c1", "label": "informs"}}
  ]
}}

Rules:
- Always include the user input as one node (id="q", type="question"), label = short version of the question
- Extract 4–10 key concepts from the response as type="concept"
- Each wiki page that was read becomes a type="wiki_page" node
- Each web search / fetched URL becomes a type="web_source" node
- Connect nodes with short, meaningful edge labels (2–4 words)
- Show the reasoning chain: sources → concepts → answer
- Keep all labels under 5 words"""

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1:
            return {"nodes": [], "edges": []}
        return json.loads(text[start:end])
    except Exception as e:
        return {"nodes": [{"id": "q", "label": question[:40], "type": "question"}], "edges": [], "error": str(e)}
