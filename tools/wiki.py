"""Wiki storage tools — read/write markdown pages to disk."""

import os
from datetime import datetime
from pathlib import Path

WIKI_DIR = Path(os.environ.get("WIKI_DIR", os.path.join(os.path.dirname(__file__), "..", "wiki")))


def _page_path(title: str) -> Path:
    """Convert a title like 'fitness/goals' to a file path."""
    safe = title.replace(" ", "_").strip("/")
    path = WIKI_DIR / (safe + ".md")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_wiki_page(title: str) -> str:
    """Read a wiki page. Returns content or a 'not found' message."""
    path = _page_path(title)
    if not path.exists():
        return f"[Page '{title}' does not exist yet]"
    return path.read_text(encoding="utf-8")


def write_wiki_page(title: str, content: str) -> str:
    """Create or overwrite a wiki page. Returns confirmation."""
    path = _page_path(title)
    path.write_text(content, encoding="utf-8")
    _update_index(title)
    return f"Wiki page '{title}' saved ({len(content)} chars)."


def delete_wiki_page(title: str) -> str:
    """Delete a wiki page. Returns confirmation or not-found message."""
    path = _page_path(title)
    if not path.exists():
        return f"[Page '{title}' does not exist]"
    path.unlink()
    # Remove empty parent dirs (but not WIKI_DIR itself)
    try:
        path.parent.rmdir()
    except OSError:
        pass
    return f"Wiki page '{title}' deleted."


def list_wiki_pages() -> str:
    """Return a list of all wiki page titles (skips empty files)."""
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    pages = []
    for f in sorted(WIKI_DIR.rglob("*.md")):
        rel = f.relative_to(WIKI_DIR)
        title = str(rel).replace("\\", "/").removesuffix(".md")
        if title not in ("index", "log") and f.stat().st_size > 0:
            pages.append(title)
    if not pages:
        return "The wiki is empty — no pages yet."
    return "Wiki pages:\n" + "\n".join(f"  - {p}" for p in pages)


def search_wiki_pages(query: str) -> str:
    """Full-text search across all wiki pages. Returns matching page titles and snippets."""
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    query_lower = query.lower()
    results = []
    for f in sorted(WIKI_DIR.rglob("*.md")):
        rel = f.relative_to(WIKI_DIR)
        title = str(rel).replace("\\", "/").removesuffix(".md")
        if title in ("index", "log"):
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if query_lower in text.lower():
            # Find a short snippet around the first match
            idx = text.lower().find(query_lower)
            start = max(0, idx - 60)
            end = min(len(text), idx + 120)
            snippet = text[start:end].replace("\n", " ").strip()
            results.append(f"  - {title}: …{snippet}…")
    if not results:
        return f"No pages found matching '{query}'."
    return f"Pages matching '{query}':\n" + "\n".join(results)


def get_wiki_summaries() -> str:
    """Return each wiki page title with its first non-empty line as a one-line summary."""
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []
    for f in sorted(WIKI_DIR.rglob("*.md")):
        rel = f.relative_to(WIKI_DIR)
        title = str(rel).replace("\\", "/").removesuffix(".md")
        if title in ("index", "log"):
            continue
        if f.stat().st_size == 0:
            continue
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
            first = next((l.strip().lstrip("#").strip() for l in lines if l.strip() and not l.startswith("#")), "")
            summaries.append(f"  - {title}: {first[:100]}" if first else f"  - {title}")
        except Exception:
            summaries.append(f"  - {title}")
    if not summaries:
        return "The wiki is empty."
    return "Wiki summaries:\n" + "\n".join(summaries)


def log_activity(message: str) -> str:
    """Append a timestamped entry to the activity log."""
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    log_path = WIKI_DIR / "log.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n**{timestamp}** — {message}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)
    return f"Logged: {message}"


def _update_index(new_title: str) -> None:
    """Add a new page to the index if not already listed."""
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        index_path.write_text("# Wiki Index\n", encoding="utf-8")
    content = index_path.read_text(encoding="utf-8")
    entry = f"- [{new_title}]({new_title}.md)"
    if new_title not in content:
        index_path.write_text(content.rstrip() + f"\n{entry}\n", encoding="utf-8")
