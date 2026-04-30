from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ─────────────────────────────────────────────────────────────
# Web search
# ─────────────────────────────────────────────────────────────
@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    results = tavily.search(query=query, max_results=5)

    out = []
    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    return "\n----\n".join(out)


# ─────────────────────────────────────────────────────────────
# Scraper
# ─────────────────────────────────────────────────────────────
# Browser-like headers — many sites (Medium, NYT, etc.) block "python-requests"
# or sparse User-Agents and serve a Cloudflare challenge page instead.
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# Phrases that indicate the page is a bot-challenge / paywall, NOT real content
BLOCK_MARKERS = [
    "just a moment",
    "enable javascript and cookies to continue",
    "checking your browser",
    "please verify you are a human",
    "cloudflare",
    "access denied",
    "attention required",
    "are you a robot",
    "captcha",
    "subscribe to continue reading",
    "this content is for subscribers",
]


def _looks_blocked(text: str) -> bool:
    if not text:
        return True
    low = text.lower()
    # very short pages are almost always challenge / error pages
    if len(text) < 250:
        return True
    return any(m in low for m in BLOCK_MARKERS)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading.

    Returns either the cleaned page text (up to ~3000 chars) or a string
    that starts with 'BLOCKED:' / 'ERROR:' so callers can decide to skip
    this URL and try another one.
    """
    try:
        resp = requests.get(
            url,
            timeout=12,
            headers=BROWSER_HEADERS,
            allow_redirects=True,
        )
        if resp.status_code >= 400:
            return f"ERROR: HTTP {resp.status_code} for {url}"

        soup = BeautifulSoup(resp.text, "html.parser")
        # strip non-content tags
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "form", "noscript", "iframe"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if _looks_blocked(text):
            return f"BLOCKED: site appears to require JavaScript / login ({url})"

        return text[:3000]

    except requests.exceptions.Timeout:
        return f"ERROR: request timed out for {url}"
    except Exception as e:
        return f"ERROR: could not scrape {url} — {e}"
