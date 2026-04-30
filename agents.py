from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from tool import web_search, scrape_url
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the Google GenAI model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",   # ✅ FIXED
    temperature=0
)

# 1st agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )


# 2nd agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )


# ─────────────────────────────────────────────────────────────
# Writer chain — STRICT about including the source URLs
# ─────────────────────────────────────────────────────────────
writer_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert research writer. Write clear, structured, insightful "
     "reports in clean Markdown. You ALWAYS include every source URL you are "
     "given, exactly as provided, in a final 'Sources' section. You never "
     "drop, paraphrase, or summarise URLs."),
    ("human",
     """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Verified Source URLs (you MUST include every single one of these verbatim
in the final 'Sources' section as a numbered markdown list):
{sources}

Structure the report EXACTLY as:

## Introduction
(2-3 paragraphs)

## Key Findings
(minimum 3 well-explained points, each as a numbered item with a bold title)

## Conclusion
(1-2 paragraphs)

## Sources
A numbered list of every URL from the "Verified Source URLs" block above,
formatted as clickable Markdown links like:
1. [example.com](https://example.com)
2. [another-site.org/article](https://another-site.org/article)

Rules:
- Do NOT invent URLs. Only use URLs from the Verified Source URLs block.
- Do NOT skip any URL — include all of them.
- Keep URLs exactly as given (no shortening, no editing).
- Be detailed, factual and professional.
""")
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ─────────────────────────────────────────────────────────────
# Critic chain
# ─────────────────────────────────────────────────────────────
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
