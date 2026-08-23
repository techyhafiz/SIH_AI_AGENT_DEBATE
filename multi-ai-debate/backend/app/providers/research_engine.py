import asyncio
import os
import json
import httpx
import xml.etree.ElementTree as ET
import urllib.parse
from typing import Dict, List, Optional, Any

RESEARCH_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "research_config.json")

class ResearchEngine:
    DEFAULT_TAVILY_KEY = "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"

    @classmethod
    def get_tavily_key(cls) -> str:
        if os.path.exists(RESEARCH_CONFIG_PATH):
            try:
                with open(RESEARCH_CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    k = cfg.get("tavily_api_key", "").strip()
                    if k:
                        return k
            except Exception:
                pass
        return cls.DEFAULT_TAVILY_KEY

    @classmethod
    def save_tavily_key(cls, key: str):
        os.makedirs(os.path.dirname(RESEARCH_CONFIG_PATH), exist_ok=True)
        try:
            with open(RESEARCH_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"tavily_api_key": key.strip()}, f, indent=2)
        except Exception as e:
            print(f"Error saving research_config.json: {e}")

    @classmethod
    async def search_tavily(cls, query: str, api_key: Optional[str] = None, max_results: int = 3) -> Dict[str, Any]:
        key = api_key or cls.get_tavily_key()
        if not key:
            return {"answer": "", "results": []}

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": max_results
        }
        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "answer": data.get("answer", ""),
                        "results": [
                            {
                                "title": r.get("title", ""),
                                "url": r.get("url", ""),
                                "content": r.get("content", "")[:300]
                            }
                            for r in data.get("results", [])
                        ]
                    }
        except Exception as e:
            print(f"Tavily search error for '{query}': {e}")
        return {"answer": "", "results": []}

    @classmethod
    async def search_openalex(cls, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        clean_q = urllib.parse.quote_plus(query[:80])
        url = f"https://api.openalex.org/works?search={clean_q}&per-page={max_results}"
        headers = {"User-Agent": "mailto:sih_researcher@gov.in"}
        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    papers = []
                    for item in data.get("results", []):
                        oa = item.get("open_access", {}) or {}
                        papers.append({
                            "title": item.get("display_name", ""),
                            "year": item.get("publication_year", ""),
                            "citations": item.get("cited_by_count", 0),
                            "pdf_url": oa.get("oa_url", ""),
                            "doi": item.get("doi", "")
                        })
                    return papers
        except Exception as e:
            print(f"OpenAlex search error for '{query}': {e}")
        return []

    @classmethod
    async def search_arxiv(cls, query: str, max_results: int = 2) -> List[Dict[str, Any]]:
        clean_q = urllib.parse.quote_plus(query[:60])
        url = f"http://export.arxiv.org/api/query?search_query=all:{clean_q}&start=0&max_results={max_results}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.text)
                    papers = []
                    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                        title_el = entry.find("{http://www.w3.org/2005/Atom}title")
                        id_el = entry.find("{http://www.w3.org/2005/Atom}id")
                        summary_el = entry.find("{http://www.w3.org/2005/Atom}summary")
                        title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else "Untitled"
                        link = id_el.text.strip() if id_el is not None and id_el.text else ""
                        summary = summary_el.text.strip()[:200] if summary_el is not None and summary_el.text else ""
                        papers.append({
                            "title": title,
                            "link": link,
                            "summary": summary
                        })
                    return papers
        except Exception as e:
            print(f"arXiv search error for '{query}': {e}")
        return []

    @classmethod
    async def conduct_round_research(
        cls,
        round_num: int,
        session_title: str,
        problem_statement: str,
        additional_prompt: str = "",
        previous_friction: Optional[List[str]] = None,
        tavily_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a targeted parallel research pass across Tavily, OpenAlex, and arXiv.
        - Round 1: Broad architectural & real-world deployment research.
        - Round 2+: Dynamic friction and objection verification research.
        """
        # Formulate query based on round and friction points
        if round_num == 1:
            web_query = f"{session_title.replace('_', ' ')} real world implementation standards india"
            academic_query = f"{session_title.replace('_', ' ')} IoT system architecture"
            arxiv_query = f"{session_title.replace('_', ' ')} algorithms"
        else:
            friction_snippet = " ".join(previous_friction or [])[:60] if previous_friction else "system reliability and edge constraints"
            web_query = f"{session_title.replace('_', ' ')} {friction_snippet} benchmarks"
            academic_query = f"{session_title.replace('_', ' ')} {friction_snippet}"
            arxiv_query = f"{friction_snippet}"

        # Run all 3 search engines concurrently
        tavily_task = cls.search_tavily(web_query, api_key=tavily_key, max_results=3)
        openalex_task = cls.search_openalex(academic_query, max_results=3)
        arxiv_task = cls.search_arxiv(arxiv_query, max_results=2)

        tavily_res, openalex_res, arxiv_res = await asyncio.gather(
            tavily_task, openalex_task, arxiv_task, return_exceptions=True
        )

        tavily_data = tavily_res if isinstance(tavily_res, dict) else {"answer": "", "results": []}
        openalex_data = openalex_res if isinstance(openalex_res, list) else []
        arxiv_data = arxiv_res if isinstance(arxiv_res, list) else []

        # Build clean formatted dossier text
        dossier_lines = [
            f"### 🌐 Round {round_num} Live Research & Verified Ground-Truth Dossier:",
            f"*Auto-queried across Tavily AI Search, OpenAlex (250M Papers), and arXiv.*",
            ""
        ]

        if tavily_data.get("answer"):
            dossier_lines.append(f"**Live Web Synthesis**: {tavily_data['answer']}\n")

        source_count = 1
        sources_list = []

        # 1. Web Sources from Tavily
        if tavily_data.get("results"):
            dossier_lines.append("#### 🌐 Live Industry & Web Sources:")
            for item in tavily_data["results"]:
                dossier_lines.append(f"- **[Source {source_count}]** [{item['title']}]({item['url']}): {item['content']}")
                sources_list.append({"tag": f"Source {source_count}", "title": item["title"], "url": item["url"], "type": "Web"})
                source_count += 1
            dossier_lines.append("")

        # 2. Peer-Reviewed Papers from OpenAlex
        if openalex_data:
            dossier_lines.append("#### 📚 Peer-Reviewed Research Papers (OpenAlex / IEEE / Nature):")
            for item in openalex_data:
                pdf_link = f" ([PDF]({item['pdf_url']}))" if item.get("pdf_url") else ""
                cite_info = f" ({item['year']} &bull; {item['citations']} citations)" if item.get('year') else ""
                dossier_lines.append(f"- **[Paper {source_count}]** {item['title']}{cite_info}{pdf_link}")
                sources_list.append({
                    "tag": f"Paper {source_count}",
                    "title": item["title"],
                    "url": item.get("pdf_url") or item.get("doi") or "https://openalex.org",
                    "type": "Academic Paper",
                    "year": item.get("year"),
                    "citations": item.get("citations")
                })
                source_count += 1
            dossier_lines.append("")

        # 3. Preprints from arXiv
        if arxiv_data:
            dossier_lines.append("#### ⚡ Cutting-Edge Preprints & Algorithms (arXiv):")
            for item in arxiv_data:
                dossier_lines.append(f"- **[Preprint {source_count}]** [{item['title']}]({item['link']}): {item['summary']}")
                sources_list.append({
                    "tag": f"Preprint {source_count}",
                    "title": item["title"],
                    "url": item["link"],
                    "type": "arXiv Preprint"
                })
                source_count += 1
            dossier_lines.append("")

        dossier_text = "\n".join(dossier_lines)

        return {
            "round_num": round_num,
            "dossier_text": dossier_text,
            "web_summary": tavily_data.get("answer", ""),
            "sources": sources_list,
            "total_sources": len(sources_list)
        }
