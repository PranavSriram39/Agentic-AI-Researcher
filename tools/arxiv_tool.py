import requests
import xml.etree.ElementTree as ET

#TODO 1: access arXiv using URL

def search_arxiv_papers(topic: str, max_results: int=5) -> dict:
    query = "+".join(topic.lower().split())
    sanitized = query.translate(str.maketrans("", "", "()-\" "))
    if sanitized != query:
        print(f"Removed invalid characters from query: '{query}' -> '{sanitized}'")
    query = sanitized
    url = (
        "https://export.arxiv.org/api/query"
        f"?search_query=all:{query}"
        f"&max_results={max_results}"
        "&sortBy=submittedDate"
        "&sortOrder=descending"
    )
    print(f"Making request to arXiv API: {url}")
    resp = requests.get(url)
    if not resp.ok:
        print(f"arXiv API request failed with status code {resp.status_code} - {resp.text}")
        raise ConnectionError(f"arXiv API request failed with status code {resp.status_code}\n{resp.text}")
    data = parse_arxiv_xml(resp.text)
    return data

#TODO 2: parse XML
def parse_arxiv_xml(xml_content: str) -> dict:
    entries = []
    namespaces = {
        "atom" : "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom"
    }
    root = ET.fromstring(xml_content)
    for entry in root.findall("atom:entry", namespaces):
        #extract authors
        authors = [author.findtext("atom:name", namespaces=namespaces) for author in entry.findall("atom:author", namespaces)]

        #extract categories
        categories = [cat.attrib.get("term") 
                      for cat in entry.findall("atom:category", namespaces)]

        #extract pdf link (rel = 'related' and type = 'application/pdf')
        pdf_link = None
        for link in entry.findall("atom:link", namespaces):
            if link.attrib.get("type") == "application/pdf":
                pdf_link = link.attrib.get("href")
                break
        
        entries.append({
            "title": entry.findtext("atom:title", namespaces=namespaces),
            "summary": entry.findtext("atom:summary", namespaces=namespaces).strip(),
            "authors": authors,
            "categories": categories,
            "pdf": pdf_link
        })

    return {"entries": entries}

# print(search_arxiv_papers("quantum computing", max_results=2))
#TODO 3: convert functionality into tool
from langchain_core.tools import tool
    
@tool
def arxiv_search(topic:str)->list[dict]:
    """Search for academic papers on arXiv related to the given topic.

    Args:
        topic (str): The topic to search for the papers.
    
    Returns:
        list of papers with their metadata including title, summary, authors, categories, and pdf link.

    """
    print("ARXIV Agent Called")
    print(f"Searching arXiv for topic: {topic}")
    papers = search_arxiv_papers(topic)
    if len(papers)==0:
        print(f"No papers found for topic: {topic}.")
        raise ValueError(f"No papers found for topic: {topic}.")
    print(f"Found {len(papers['entries'])} papers for topic: {topic}.")
    return papers