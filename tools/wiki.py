"""Wiki storage tools — read/write markdown pages to disk."""

import os
from datetime import datetime
from pathlib import Path

WIKI_DIR = Path(__file__).parent.parent / "wiki"


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


def list_wiki_pages() -> str:
    """Return a list of all wiki page titles."""
    pages = []
    for f in sorted(WIKI_DIR.rglob("*.md")):
        rel = f.relative_to(WIKI_DIR)
        title = str(rel).replace("\\", "/").removesuffix(".md")
        if title not in ("index", "log"):
            pages.append(title)
    if not pages:
        return "The wiki is empty — no pages yet."
    return "Wiki pages:\n" + "\n".join(f"  - {p}" for p in pages)


def log_activity(message: str) -> str:
    """Append a timestamped entry to the activity log."""
    log_path = WIKI_DIR / "log.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n**{timestamp}** — {message}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)
    return f"Logged: {message}"


def _update_index(new_title: str) -> None:
    """Add a new page to the index if not already listed."""
    index_path = WIKI_DIR / "index.md"
    content = index_path.read_text(encoding="utf-8")
    entry = f"- [{new_title}]({new_title}.md)"
    if new_title not in content:
        index_path.write_text(content.rstrip() + f"\n{entry}\n", encoding="utf-8")
