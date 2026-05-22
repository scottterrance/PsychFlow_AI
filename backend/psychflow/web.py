"""Lightweight web search via DuckDuckGo.

100% free. No API key required.

The agents that do web research call ``search()`` and pass the results
through ``format_for_prompt()`` to get a compact text block they can
inject into their LLM prompts.

If the search package isn't installed, or DuckDuckGo rate-limits us,
or the network is down, ``search()`` returns ``[]`` and the calling
agent gracefully falls back to its old behavior (LLM-only, no web
context).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable

logger = logging.getLogger("psychflow.web")

# `ddgs` is the current package name; `duckduckgo_search` was the old name.
# Try both so this still works on environments that have either installed.
try:
    from ddgs import DDGS  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    try:
        from duckduckgo_search import DDGS  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover
        DDGS = None  # type: ignore[assignment]


# Hard cap on how long a single search is allowed to take. DDG can hang on
# rate limits; we don't want one slow search to block a whole pipeline run.
SEARCH_TIMEOUT_SECONDS = 8.0


async def search(query: str, max_results: int = 5) -> list[dict]:
    """Run a DuckDuckGo text search and return up to ``max_results`` snippets.

    Each result is a dict with keys ``title``, ``href``, ``body``.
    Returns ``[]`` on any failure - the caller should treat that as
    "no web context available" and continue.
    """
    if DDGS is None:
        logger.warning(
            "ddgs / duckduckgo_search not installed - skipping web search "
            "(install with: pip install ddgs)"
        )
        return []

    def _sync() -> list[dict]:
        try:
            return list(DDGS().text(query, max_results=max_results))
        except Exception as exc:  # noqa: BLE001
            logger.warning("web search failed for %r: %s", query, exc)
            return []

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_sync), timeout=SEARCH_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        logger.warning(
            "web search for %r timed out after %.1fs", query, SEARCH_TIMEOUT_SECONDS
        )
        return []


def format_for_prompt(results: Iterable[dict]) -> str:
    """Render search results as a compact text block for an LLM prompt.

    Returns "(no web results found)" when the iterable is empty so the
    LLM can see we tried but came up empty.
    """
    lines: list[str] = []
    for i, r in enumerate(results, start=1):
        title = (r.get("title") or "").strip()
        href = (r.get("href") or "").strip()
        body = (r.get("body") or "").strip()
        # Truncate overly long bodies to keep token usage sensible.
        if len(body) > 500:
            body = body[:497] + "..."
        lines.append(f"[{i}] {title}\n    {href}\n    {body}")
    return "\n".join(lines) if lines else "(no web results found)"
