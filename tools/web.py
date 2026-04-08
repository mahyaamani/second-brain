"""Web tools — fetch article text and search the web."""

import trafilatura
from ddgs import DDGS


def fetch_article(url: str) -> str:
    """Scrape and return the main text content of a URL."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return f"[Could not fetch URL: {url}]"
    text = trafilatura.extract(downloaded)
    if not text:
        return f"[Could not extract text from: {url}]"
    if len(text) > 8000:
        text = text[:8000] + "\n\n[... article truncated ...]"
    return text


def search_web(query: str, num_results: int = 3) -> str:
    """Search DuckDuckGo and return a list of URLs + titles."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                results.append(f"- [{r['title']}]({r['href']})\n  {r['body'][:120]}...")
        if not results:
            return f"[No results found for: {query}]"
        return f"Top results for '{query}':\n" + "\n".join(results)
    except Exception as e:
        return f"[Search failed: {e}]"
