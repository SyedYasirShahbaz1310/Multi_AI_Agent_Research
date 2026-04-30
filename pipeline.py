import re
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


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
        # content may be a list of dict parts (tool calls / multimodal)
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                parts.append(str(p.get("text") or p.get("content") or p))
        return "\n".join(parts)
    return str(content)


def urls_from_agent_response(agent_response: dict) -> list[str]:
    """Scan EVERY message (incl. ToolMessage) for URLs — the LLM's final
    summary often drops them, but the tool output always contains them."""
    urls = []
    for m in agent_response.get("messages", []):
        urls.extend(extract_urls(_msg_text(m)))
    # de-dup, preserve order
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def format_sources_block(urls: list[str]) -> str:
    return "\n".join(f"- {u}" for u in urls) if urls else "(no URLs were captured)"


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

    # ── Step 2: Reader agent ─────────────────────────────────
    print("\n" + "=" * 50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("=" * 50)

    reader_agent = build_reader_agent()
    reader_response = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = reader_response["messages"][-1].content

    # merge any extra URLs from the reader's messages too
    state["sources"] = list(dict.fromkeys(
        state["sources"] + urls_from_agent_response(reader_response)
    ))

    print("\nscraped content:\n", state["scraped_content"])
    print("\nfinal source list:", state["sources"])

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
