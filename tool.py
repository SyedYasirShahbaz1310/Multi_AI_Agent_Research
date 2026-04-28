# from langchain.tools import tool
# import requests
# import os
# from dotenv import load_dotenv
# load_dotenv()
# from tavily import TavilyClient
# from bs4 import BeautifulSoup
# from rich import print
# tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# #Creating a tool
# @tool
# def web_search(query : str) -> str:
#     """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
#     results = tavily.search(query = query , max_results = 5)
# # now save the results of this tool
#     out = []
#     for r in results['results']:
#         out.append( f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n")
#     return "\n-----------\n".join(out)

# # creatinga second tool for scraping the content of a webpage

# @tool
# def scrape_url(url: str) -> str:
#     """Scrape and return clean text content from a given URL for deeper reading."""
#     try:
#         resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
#         soup = BeautifulSoup(resp.text, "html.parser")
#         for tag in soup(["script", "style", "nav", "footer"]):
#             tag.decompose()
#         return soup.get_text(separator=" ", strip=True)[:3000]
#     except Exception as e:
#         return f"Could not scrape URL: {str(e)}"

# # print(scrape_url.invoke("https://en.wikipedia.org/wiki/Babar_Azam"))


from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
from rich import print
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query,max_results=5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    
    return "\n----\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
