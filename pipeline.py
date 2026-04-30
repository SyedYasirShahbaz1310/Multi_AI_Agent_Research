import re
from agents import build_search_agent, writer_chain, critic_chain
from tool import scrape_url


# How many top URLs to actually scrape in full
MAX_SCRAPE = 3


# ─────────────────────────────────────────────────────────────
# URL extraction helpers
# ─────────────────────────────────────────────────────────────
URL_REGEX = re.compile(r"https?://[^\s\)\]\}<>\"']+")


def extract_urls(text: str) -> list[str]:
    """De-duplicated, order-preserving URL list from a string."""
    if not text:
        return []
    seen, out = set(), []
    for u in URL_REGEX.findall(text):
        u = u.rstrip(".,;:!?")
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _msg_text(msg) -> str:
    """Best-effort extraction of plain text from any LangChain message object."""
    content = getattr(msg, "content", msg)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                parts.append(str(p.get("text") or p.get("content") or p))
        return "\n".join(parts)
    return str(content)


def urls_from_agent_response(agent_response: dict) -> list[str]:
    """Scan EVERY message (incl. ToolMessage) for URLs."""
    urls = []
    for m in agent_response.get("messages", []):
        urls.extend(extract_urls(_msg_text(m)))
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def format_sources_block(urls: list[str]) -> str:
    return "\n".join(f"- {u}" for u in urls) if urls else "(no URLs were captured)"


def scrape_top_urls(urls: list[str], limit: int = MAX_SCRAPE) -> tuple[str, list[str]]:
    """Iterate through the URLs and scrape until we have `limit` SUCCESSFUL
    scrapes (i.e. results that are not BLOCKED/ERROR). Returns
    (concatenated_text, list_of_successfully_scraped_urls)."""
    chunks = []
    used = []
    for url in urls:
        if len(chunks) >= limit:
            break
        try:
            text = scrape_url.invoke(url)
        except Exception as e:
            text = f"ERROR: {e}"

        # skip cloudflare / paywall / error pages and try the next URL
        if text.startswith("BLOCKED:") or text.startswith("ERROR:"):
            print(f"  · skipped {url} → {text}")
            continue

        i = len(chunks) + 1
        chunks.append(
            f"────── SOURCE {i} ──────\n"
            f"URL: {url}\n\n"
            f"{text}\n"
        )
        used.append(url)

    if not chunks:
        return "(no URLs could be scraped — all blocked or errored)", []
    return "\n\n".join(chunks), used


# ─────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────
def run_research_pipeline(topic: str) -> dict:
    state = {}

    # ── Step 1: Search agent ─────────────────────────────────
    print("\n" + "=" * 50)
    print("step 1 - search agent is working ...")
    print("=" * 50)

    search_agent = build_search_agent()
    search_response = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_response["messages"][-1].content
    state["sources"] = urls_from_agent_response(search_response)

    print("\nsearch result:\n", state["search_results"])
    print("\nextracted URLs:", state["sources"])

    # ── Step 2: Direct scraping of top N URLs ────────────────
    print("\n" + "=" * 50)
    print(f"step 2 - directly scraping top {MAX_SCRAPE} URLs ...")
    print("=" * 50)

    scraped_text, scraped_urls = scrape_top_urls(state["sources"], limit=MAX_SCRAPE)
    state["scraped_content"] = scraped_text
    state["scraped_urls"] = scraped_urls

    print("\nscraped content:\n", state["scraped_content"][:1500], "...\n")
    print("scraped URLs:", state["scraped_urls"])

    # ── Step 3: Writer chain ─────────────────────────────────
    print("\n" + "=" * 50)
    print("step 3 - Writer is drafting the report ...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS (titles + snippets):\n{state['search_results']}\n\n"
        f"FULL SCRAPED CONTENT FROM TOP {MAX_SCRAPE} SOURCES:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
        "sources": format_sources_block(state["sources"]),
    })

    print("\nFinal Report:\n", state["report"])

    # ── Step 4: Critic chain ─────────────────────────────────
    print("\n" + "=" * 50)
    print("step 4 - critic is reviewing the report")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    print("\ncritic report:\n", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)
