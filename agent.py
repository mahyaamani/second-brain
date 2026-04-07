"""
Second Brain Agent — Claude tool-use loop.

Claude decides which tools to call. Tools do the actual work.
Loop continues until Claude stops requesting tools (end_turn).
"""

import anthropic
from tools.wiki import read_wiki_page, write_wiki_page, list_wiki_pages, log_activity
from tools.web import fetch_article, search_web
from tools import interaction

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are Second Brain — a personal AI knowledge assistant that grows smarter over time.

You maintain a persistent wiki of markdown pages that you read and write to. Your job:

1. **Ingest** — When given an article URL or text, fetch it, extract key knowledge, and update relevant wiki pages.
2. **Research** — When asked to research a topic, search the web for top articles, ingest them, and synthesize into wiki pages.
3. **Interview** — When asked to interview the user, ask focused questions about a topic and store their answers as structured wiki pages.
4. **Answer** — When asked a question, search your wiki for relevant pages, then give a personalized answer grounded in stored knowledge.

## Wiki conventions
- Page titles use snake_case with "/" for categories: "fitness/goals", "nutrition/protein_sources", "personal/preferences"
- Always read existing related pages before writing, to avoid overwriting good content
- Write clean, structured markdown with headers and bullet points
- Log every significant action using log_activity

## Workflow for ingesting
1. fetch_article(url) to get the text
2. list_wiki_pages() to see what exists
3. Read any relevant existing pages
4. write_wiki_page() to create/update pages with synthesized knowledge
5. log_activity() to record what was done

## Workflow for researching
1. search_web(topic) to find top articles
2. fetch_article() each relevant URL
3. Synthesize and write wiki pages
4. log_activity()

## Workflow for interviewing
1. ask_user() with specific, focused questions one at a time
2. Synthesize answers into wiki pages
3. log_activity()

## Workflow for answering
1. list_wiki_pages() to see what's available
2. read_wiki_page() on relevant pages
3. Synthesize a personalized answer using stored knowledge
4. Cite which pages you used

Be concise but thorough. The wiki is your persistent memory — treat it carefully."""

TOOLS = [
    {
        "name": "read_wiki_page",
        "description": "Read the content of a wiki page by title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Page title, e.g. 'fitness/goals'"}
            },
            "required": ["title"],
        },
    },
    {
        "name": "write_wiki_page",
        "description": "Create or update a wiki page with markdown content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Page title, e.g. 'nutrition/protein_sources'"},
                "content": {"type": "string", "description": "Full markdown content for the page"},
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "list_wiki_pages",
        "description": "List all pages currently stored in the wiki.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "log_activity",
        "description": "Append a note to the activity log.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "What was done"}
            },
            "required": ["message"],
        },
    },
    {
        "name": "fetch_article",
        "description": "Scrape and return the main text content from a URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The article URL to fetch"}
            },
            "required": ["url"],
        },
    },
    {
        "name": "search_web",
        "description": "Search the web for articles on a topic. Returns titles, URLs, and snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results to return (1-5)", "default": 3},
            },
            "required": ["query"],
        },
    },
    {
        "name": "ask_user",
        "description": "Ask the user a question and return their answer. Use during interviews.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The question to ask the user"}
            },
            "required": ["question"],
        },
    },
]

TOOL_DISPATCH = {
    "read_wiki_page": lambda args: read_wiki_page(args["title"]),
    "write_wiki_page": lambda args: write_wiki_page(args["title"], args["content"]),
    "list_wiki_pages": lambda args: list_wiki_pages(),
    "log_activity": lambda args: log_activity(args["message"]),
    "fetch_article": lambda args: fetch_article(args["url"]),
    "search_web": lambda args: search_web(args["query"], args.get("num_results", 3)),
    "ask_user": lambda args: interaction.ask_user(args["question"]),
}


def run(user_message: str, history: list) -> tuple[str, list]:
    """
    Run one user turn through the agent loop.

    Args:
        user_message: The user's input text.
        history: The conversation history (list of message dicts).

    Returns:
        (final_text_response, updated_history)
    """
    history = history + [{"role": "user", "content": user_message}]
    final_response = ""

    while True:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=history,
        ) as stream:
            response = stream.get_final_message()

        history.append({"role": "assistant", "content": response.content})

        # Collect any text to show the user
        for block in response.content:
            if block.type == "text":
                final_response = block.text

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason != "tool_use":
            break

        # Execute all tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [Tool] {block.name}({_summarize_args(block.input)})")
                try:
                    result = TOOL_DISPATCH[block.name](block.input)
                except Exception as e:
                    result = f"[Error running {block.name}: {e}]"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })

        history.append({"role": "user", "content": tool_results})

    return final_response, history


def _summarize_args(args: dict) -> str:
    """Format tool args for display, truncating long values."""
    parts = []
    for k, v in args.items():
        s = str(v)
        if len(s) > 60:
            s = s[:57] + "..."
        parts.append(f"{k}={s!r}")
    return ", ".join(parts)
