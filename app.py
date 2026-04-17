"""Second Brain — chat-only Flask backend (no voice)."""

import os
import anthropic
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

load_dotenv(override=True)

from tools.wiki import read_wiki_page, write_wiki_page, delete_wiki_page, list_wiki_pages, log_activity, search_wiki_pages, get_wiki_summaries
from tools.web import fetch_article, search_web
from tools.files import extract_text
from config import MODEL_NAME

app = Flask(__name__, static_folder="static")
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are Second Brain — a warm, curious AI assistant that helps the user capture and organize their personal knowledge.

## Wiki usage

At the start of EVERY conversation:
1. Call get_wiki_summaries to load a snapshot of everything you know.
2. Read any pages directly relevant to what the user just said.

Whenever the user shares something worth remembering:
1. Write or update the relevant wiki page.
2. Call search_wiki_pages with 2-3 keywords from the new content to find related pages.
3. For each related page found, read it and add a cross-reference link — append a "## Related" section listing `[[page/title]]` links if one doesn't exist, or update the existing one.
4. Also add a `[[page/title]]` back-link to the page you just wrote.

## Page organization
- Use category/title paths: personal/hobbies, work/projects, goals/2026, ideas, health, etc.
- Use `[[category/title]]` syntax for cross-reference links inside page content.

## Conversation style
- Concise and conversational. Ask one follow-up question at a time.
- Reference what you already know naturally — don't recite it robotically.
- Use web search when the user asks something outside your knowledge."""

TOOLS = [
    {
        "name": "read_wiki_page",
        "description": "Read a wiki page by title. Returns the page content.",
        "input_schema": {
            "type": "object",
            "properties": {"title": {"type": "string", "description": "Page title, e.g. 'personal/hobbies'"}},
            "required": ["title"],
        },
    },
    {
        "name": "write_wiki_page",
        "description": "Create or update a wiki page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Page title, e.g. 'work/projects'"},
                "content": {"type": "string", "description": "Full markdown content for the page"},
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "delete_wiki_page",
        "description": "Delete a wiki page by title.",
        "input_schema": {
            "type": "object",
            "properties": {"title": {"type": "string"}},
            "required": ["title"],
        },
    },
    {
        "name": "list_wiki_pages",
        "description": "List all wiki pages. Call this at the start of a conversation.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_web",
        "description": "Search the web for information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "num_results": {"type": "integer", "default": 3},
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_article",
        "description": "Fetch and read the content of a web page by URL.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "search_wiki_pages",
        "description": "Full-text search across all wiki pages. Use after writing a page to find related pages for cross-referencing.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Keywords to search for"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_wiki_summaries",
        "description": "Get all wiki page titles with one-line summaries. Call this at the start of every conversation.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def run_tool(name, inputs):
    if name == "read_wiki_page":
        return read_wiki_page(inputs["title"])
    if name == "write_wiki_page":
        log_activity(f"Chat wrote wiki page: {inputs['title']}")
        return write_wiki_page(inputs["title"], inputs["content"])
    if name == "delete_wiki_page":
        log_activity(f"Chat deleted wiki page: {inputs['title']}")
        return delete_wiki_page(inputs["title"])
    if name == "list_wiki_pages":
        return list_wiki_pages()
    if name == "search_web":
        return search_web(inputs["query"], num_results=inputs.get("num_results", 3))
    if name == "fetch_article":
        return fetch_article(inputs["url"])
    if name == "search_wiki_pages":
        return search_wiki_pages(inputs["query"])
    if name == "get_wiki_summaries":
        return get_wiki_summaries()
    return f"Unknown tool: {name}"


# --- Static / UI ---

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# --- Chat endpoint ---

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        body = request.get_json(force=True)
        history = body.get("history", [])

        messages = list(history)

        # Agentic loop: keep calling until no more tool use
        while True:
            resp = client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": resp.content})

            if resp.stop_reason != "tool_use":
                break

            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    try:
                        result = run_tool(block.name, block.input)
                    except Exception as e:
                        result = f"Tool error: {e}"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })

            messages.append({"role": "user", "content": tool_results})

        text = next((b.text for b in resp.content if hasattr(b, "text")), "")

        # Build clean history with plain text only (no SDK objects)
        clean_history = []
        for m in messages:
            if m["role"] == "user" and isinstance(m["content"], str):
                clean_history.append({"role": "user", "content": m["content"]})
            elif m["role"] == "assistant":
                content = m["content"]
                parts = [b.text for b in content if hasattr(b, "text")] if isinstance(content, list) else [content]
                joined = " ".join(p for p in parts if p)
                if joined:
                    clean_history.append({"role": "assistant", "content": joined})

        return jsonify({"reply": text, "history": clean_history})

    except Exception as e:
        app.logger.exception("Chat error")
        return jsonify({"error": str(e)}), 500


# --- Wiki read-only endpoints for UI ---

@app.route("/api/wiki/pages")
def ui_wiki_pages():
    raw = list_wiki_pages()
    if raw.startswith("The wiki is empty"):
        return jsonify({"pages": []})
    pages = []
    for line in raw.split("\n"):
        line = line.strip().lstrip("- ")
        if line and line != "Wiki pages:":
            pages.append(line)
    return jsonify({"pages": pages})


@app.route("/api/wiki/page")
def ui_wiki_page():
    title = request.args.get("title", "")
    content = read_wiki_page(title)
    return jsonify({"title": title, "content": content})


ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "docx", "csv", "rst"}


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported type .{ext}"}), 400

    data = f.read()
    if len(data) > 10 * 1024 * 1024:
        return jsonify({"error": "File too large (max 10 MB)"}), 413

    try:
        text = extract_text(f.filename, data)
    except Exception as e:
        return jsonify({"error": f"Could not extract text: {e}"}), 422

    if not text.strip():
        return jsonify({"error": "File appears empty"}), 422

    stem = f.filename.rsplit(".", 1)[0] if "." in f.filename else f.filename
    title = f"uploads/{stem}"
    write_wiki_page(title, f"# {stem}\n\n{text}")
    log_activity(f"Uploaded file: {f.filename} → {title}")

    return jsonify({"title": title, "chars": len(text)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5051))
    app.run(host="0.0.0.0", port=port, debug=True)
