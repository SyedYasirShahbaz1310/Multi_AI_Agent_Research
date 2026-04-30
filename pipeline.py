import re
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


# ─────────────────────────────────────────────────────────────
# Helper: pull every URL out of the search-agent output
# ─────────────────────────────────────────────────────────────
URL_REGEX = re.compile(r"https?://[^\s\)\]\}<>\"']+")

def extract_urls(text: str) -> list[str]:
    """Return a de-duplicated, order-preserving list of URLs found in text."""
    if not text:
        return []
    seen = set()
    urls = []
    for u in URL_REGEX.findall(text):
        # strip common trailing punctuation
        u = u.rstrip(".,;:!?")
        if u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def format_sources_block(urls: list[str]) -> str:
    if not urls:
        return "(no URLs were captured)"
    return "\n".join(f"- {u}" for u in urls)


def run_research_pipeline(topic: str) -> dict:
    state = {}

    # ── Step 1: Search agent ─────────────────────────────────
    print("\n" + "=" * 50)
    print("step 1 - search agent is working ...")
    print("=" * 50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result["messages"][-1].content
    state["sources"] = extract_urls(state["search_results"])

    print("\nsearch result:\n", state["search_results"])
    print("\nextracted URLs:", state["sources"])

    # ── Step 2: Reader agent ─────────────────────────────────
    print("\n" + "=" * 50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("=" * 50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = reader_result["messages"][-1].content

    # also pick up any extra URLs the reader saw
    state["sources"] = list(dict.fromkeys(
        state["sources"] + extract_urls(state["scraped_content"])
    ))

    print("\nscraped content:\n", state["scraped_content"])

    # ── Step 3: Writer chain ─────────────────────────────────
    print("\n" + "=" * 50)
    print("step 3 - Writer is drafting the report ...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
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
