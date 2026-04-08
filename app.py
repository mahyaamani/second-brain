"""VocalBridge voice agent prototype — Flask backend."""

import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

load_dotenv(override=True)

from tools.wiki import read_wiki_page, write_wiki_page, list_wiki_pages, log_activity
from tools.web import fetch_article, search_web
from config import VOCAL_BRIDGE_API_KEY, VOCAL_BRIDGE_URL, VOCAL_BRIDGE_AGENT_ID, TOOL_SECRET

app = Flask(__name__, static_folder="static")


def check_tool_auth():
    """Verify the request carries our tool secret."""
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if token != TOOL_SECRET:
        return jsonify({"error": "unauthorized"}), 401
    return None


# --- Static / UI ---

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# --- VocalBridge token proxy ---

@app.route("/api/voice-token", methods=["POST"])
def voice_token():
    if not VOCAL_BRIDGE_API_KEY:
        return jsonify({"error": "VOCAL_BRIDGE_API_KEY not set"}), 500

    # Inject current wiki index into the agent prompt before each call
    try:
        _update_prompt_with_wiki_index()
    except Exception as e:
        app.logger.warning("Failed to update prompt with wiki index: %s", e)

    try:
        resp = requests.post(
            f"{VOCAL_BRIDGE_URL}/api/v1/token",
            headers={
                "X-API-Key": VOCAL_BRIDGE_API_KEY,
                "Content-Type": "application/json",
                **({"X-Agent-Id": VOCAL_BRIDGE_AGENT_ID} if VOCAL_BRIDGE_AGENT_ID else {}),
            },
            json={"participant_name": "User"},
            timeout=10,
        )
        if not resp.ok:
            app.logger.error("VocalBridge responded %s: %s", resp.status_code, resp.text)
            return jsonify({"error": f"VocalBridge error: {resp.status_code}", "detail": resp.text}), resp.status_code
        return jsonify(resp.json())
    except requests.exceptions.Timeout:
        return jsonify({"error": "VocalBridge API timed out"}), 504
    except requests.exceptions.RequestException as e:
        app.logger.error("Token request failed: %s", e)
        return jsonify({"error": "Failed to get voice token"}), 502


# Base prompt stored here so we can append wiki index dynamically
BASE_PROMPT = None


def _get_base_prompt():
    """Fetch the base prompt once and cache it."""
    global BASE_PROMPT
    if BASE_PROMPT is not None:
        return BASE_PROMPT
    try:
        resp = requests.get(
            f"{VOCAL_BRIDGE_URL}/api/v1/agent",
            headers={"X-API-Key": VOCAL_BRIDGE_API_KEY},
            timeout=10,
        )
        if resp.ok:
            prompt = resp.json().get("custom_prompt", "")
            # Strip any previous wiki index appendage
            marker = "\n\n--- CURRENT WIKI INDEX ---"
            if marker in prompt:
                prompt = prompt[:prompt.index(marker)]
            BASE_PROMPT = prompt
            return BASE_PROMPT
    except Exception:
        pass
    return ""


def _update_prompt_with_wiki_index():
    """Append the current wiki page list to the agent prompt."""
    base = _get_base_prompt()
    if not base:
        return

    pages_raw = list_wiki_pages()
    if pages_raw.startswith("The wiki is empty"):
        wiki_section = "The wiki is currently empty. This is a new user — start by getting to know them."
    else:
        wiki_section = f"These pages already exist in the user's second brain:\n{pages_raw}\n\nYou already know things about this person. Reference this knowledge naturally. Use read_wiki_page to look up details from specific pages when relevant."

    full_prompt = f"{base}\n\n--- CURRENT WIKI INDEX ---\n{wiki_section}"

    requests.patch(
        f"{VOCAL_BRIDGE_URL}/api/v1/agent",
        headers={"X-API-Key": VOCAL_BRIDGE_API_KEY, "Content-Type": "application/json"},
        json={"prompt": full_prompt},
        timeout=10,
    )


# --- Second Brain tool endpoints (called by VocalBridge API tools) ---

@app.route("/tools/wiki/read", methods=["POST"])
def tool_read_wiki():
    auth_err = check_tool_auth()
    if auth_err:
        return auth_err
    title = request.json.get("title", "")
    result = read_wiki_page(title)
    return jsonify({"result": result})


@app.route("/tools/wiki/write", methods=["POST"])
def tool_write_wiki():
    auth_err = check_tool_auth()
    if auth_err:
        return auth_err
    title = request.json.get("title", "")
    content = request.json.get("content", "")
    result = write_wiki_page(title, content)
    log_activity(f"Voice agent wrote wiki page: {title}")
    return jsonify({"result": result})


@app.route("/tools/wiki/list", methods=["POST"])
def tool_list_wiki():
    auth_err = check_tool_auth()
    if auth_err:
        return auth_err
    result = list_wiki_pages()
    return jsonify({"result": result})


@app.route("/tools/web/search", methods=["POST"])
def tool_search_web():
    auth_err = check_tool_auth()
    if auth_err:
        return auth_err
    query = request.json.get("query", "")
    num_results = request.json.get("num_results", 3)
    result = search_web(query, num_results=num_results)
    return jsonify({"result": result})


@app.route("/tools/web/fetch", methods=["POST"])
def tool_fetch_article():
    auth_err = check_tool_auth()
    if auth_err:
        return auth_err
    url = request.json.get("url", "")
    result = fetch_article(url)
    return jsonify({"result": result})


@app.route("/tools/wiki/log", methods=["POST"])
def tool_log_activity():
    auth_err = check_tool_auth()
    if auth_err:
        return auth_err
    message = request.json.get("message", "")
    result = log_activity(message)
    return jsonify({"result": result})


# --- UI read-only endpoints (no auth needed, read-only) ---

@app.route("/api/wiki/pages")
def ui_wiki_pages():
    """List wiki pages for the UI (read-only, no auth)."""
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
    """Read a single wiki page for the UI (read-only, no auth)."""
    title = request.args.get("title", "")
    content = read_wiki_page(title)
    return jsonify({"title": title, "content": content})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
