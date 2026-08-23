import asyncio
import os
import json
import httpx
import xml.etree.ElementTree as ET
import urllib.parse
from typing import Dict, List, Optional, Any

RESEARCH_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "research_config.json")

class ResearchEngine:
    DEFAULT_CONFIG = {
        "enabled": True,
        "tavily_api_key": "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",
        "openalex_email": "campusprintexpress@gmail.com",
        "max_papers_per_round": 15,
        "max_web_sources_per_round": 8
    }

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        if os.path.exists(RESEARCH_CONFIG_PATH):
            try:
                with open(RESEARCH_CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    return {**cls.DEFAULT_CONFIG, **cfg}
            except Exception:
                pass
        return cls.DEFAULT_CONFIG.copy()

    @classmethod
    def save_config(cls, cfg: Dict[str, Any]):
        os.makedirs(os.path.dirname(RESEARCH_CONFIG_PATH), exist_ok=True)
        try:
            curr = cls.get_config()
            merged = {**curr, **cfg}
            with open(RESEARCH_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2)
        except Exception as e:
            print(f"Error saving research_config.json: {e}")

    @classmethod
    async def search_tavily(cls, query: str, api_key: Optional[str] = None, max_results: int = 5) -> Dict[str, Any]:
        cfg = cls.get_config()
        key = api_key or cfg.get("tavily_api_key", "").strip()
        if not key:
            return {"answer": "", "results": []}

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "max_results": max_results
        }
        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "answer": data.get("answer", ""),
                        "results": [
                            {
                                "title": r.get("title", ""),
                                "url": r.get("url", ""),
                                "content": r.get("content", "")[:350]
                            }
                            for r in data.get("results", [])
                        ]
                    }
        except Exception as e:
            print(f"Tavily search error for '{query}': {e}")
        return {"answer": "", "results": []}

    @classmethod
    async def search_openalex(cls, query: str, max_results: int = 6, email: Optional[str] = None) -> List[Dict[str, Any]]:
        cfg = cls.get_config()
        user_email = email or cfg.get("openalex_email", "campusprintexpress@gmail.com")
        clean_q = urllib.parse.quote_plus(query[:80])
        url = f"https://api.openalex.org/works?search={clean_q}&per-page={max_results}&mailto={user_email}"
        headers = {"User-Agent": f"mailto:{user_email}"}
        try:
            async with httpx.AsyncClient(timeout=9.0, verify=False) as client:
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
                            "doi": item.get("doi", ""),
                            "concepts": [c.get("display_name") for c in item.get("concepts", [])[:3] if c.get("display_name")]
                        })
                    return papers
        except Exception as e:
            print(f"OpenAlex search error for '{query}': {e}")
        return []

    @classmethod
    async def search_arxiv(cls, query: str, max_results: int = 4) -> List[Dict[str, Any]]:
        clean_q = urllib.parse.quote_plus(query[:60])
        url = f"http://export.arxiv.org/api/query?search_query=all:{clean_q}&start=0&max_results={max_results}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with httpx.AsyncClient(timeout=9.0, verify=False) as client:
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
                        summary = summary_el.text.strip()[:240] if summary_el is not None and summary_el.text else ""
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
        ai_requested_queries: Optional[List[str]] = None,
        tavily_key: Optional[str] = None,
        openalex_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a deep multi-angle parallel research sweep across:
        1. AI-Requested Technical Limits & Scope Topics from Previous Turns
        2. Core Physical Mechanism & Domain Specifications
        3. Hardware BOM, Wireless Topology & Edge Constraints
        4. Cutting-Edge AI/ML Algorithms & Preprints
        5. Indian Standards & Field Deployment Realities
        """
        cfg = cls.get_config()
        if not cfg.get("enabled", True):
            return {"round_num": round_num, "dossier_text": "", "web_summary": "", "sources": [], "total_sources": 0}

        import re
        raw_problem = (problem_statement or session_title or "").strip()
        cleaned = re.sub(r'^(Develop|Design|Build|Create|Implement|Formulate|Propose)\s+(an?|the)?\s*', '', raw_problem, flags=re.IGNORECASE)
        cleaned = re.sub(r'^(AI-driven|AI-based|Smart|Intelligent|Automated)\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^(system|solution|platform|tool|framework)\s+(for|to)\s*', '', cleaned, flags=re.IGNORECASE)
        topic_clean = cleaned.split(".")[0].strip()[:90] or session_title.replace("_", " ")
        
        # 1. Multi-Angle Query Decomposition (Prioritizing AI-Requested Topics)
        if ai_requested_queries and len(ai_requested_queries) > 0:
            ai_q1 = ai_requested_queries[0][:70]
            ai_q2 = ai_requested_queries[1][:70] if len(ai_requested_queries) > 1 else ai_q1
            q_web_1 = f"{topic_clean} {ai_q1} real world benchmarks"
            q_web_2 = f"{topic_clean} {ai_q2} specifications"
            q_academic_1 = f"{ai_q1}"
            q_academic_2 = f"{ai_q2}"
            q_arxiv_1 = f"{ai_q1}"
            q_arxiv_2 = f"{ai_q2}"
        elif round_num == 1:
            q_web_1 = f"{topic_clean} real world deployment architecture specifications india"
            q_web_2 = f"{topic_clean} hardware sensor BOM and power battery constraints"
            q_academic_1 = f"{topic_clean} architecture"
            q_academic_2 = f"{topic_clean} algorithms"
            q_arxiv_1 = f"{topic_clean} edge computing"
            q_arxiv_2 = f"{topic_clean} TinyML"
        else:
            friction_str = " ".join(previous_friction or [])[:80] if previous_friction else "system reliability and edge constraints"
            q_web_1 = f"{topic_clean} {friction_str} real world validation"
            q_web_2 = f"{topic_clean} {friction_str} industry standards"
            q_academic_1 = f"{topic_clean} {friction_str}"
            q_academic_2 = f"{friction_str} failure modes"
            q_arxiv_1 = f"{friction_str} models"
            q_arxiv_2 = f"{friction_str} protocol"

        # 2. Parallel Multi-Engine Sweep (Max Papers & Deep Search)
        tavily_task_1 = cls.search_tavily(q_web_1, api_key=tavily_key, max_results=4)
        tavily_task_2 = cls.search_tavily(q_web_2, api_key=tavily_key, max_results=4)
        openalex_task_1 = cls.search_openalex(q_academic_1, max_results=5, email=openalex_email)
        openalex_task_2 = cls.search_openalex(q_academic_2, max_results=5, email=openalex_email)
        arxiv_task_1 = cls.search_arxiv(q_arxiv_1, max_results=3)
        arxiv_task_2 = cls.search_arxiv(q_arxiv_2, max_results=3)

        results = await asyncio.gather(
            tavily_task_1, tavily_task_2,
            openalex_task_1, openalex_task_2,
            arxiv_task_1, arxiv_task_2,
            return_exceptions=True
        )

        tav_1 = results[0] if isinstance(results[0], dict) else {"answer": "", "results": []}
        tav_2 = results[1] if isinstance(results[1], dict) else {"answer": "", "results": []}
        alex_1 = results[2] if isinstance(results[2], list) else []
        alex_2 = results[3] if isinstance(results[3], list) else []
        arx_1 = results[4] if isinstance(results[4], list) else []
        arx_2 = results[5] if isinstance(results[5], list) else []

        # Deduplicate Web Results
        seen_urls = set()
        dedup_web = []
        for r in (tav_1.get("results", []) + tav_2.get("results", [])):
            u = r.get("url", "")
            if u and u not in seen_urls:
                seen_urls.add(u)
                dedup_web.append(r)

        # Deduplicate OpenAlex Papers
        seen_titles = set()
        dedup_alex = []
        for p in (alex_1 + alex_2):
            t = p.get("title", "").strip().lower()
            if t and t not in seen_titles:
                seen_titles.add(t)
                dedup_alex.append(p)

        # Deduplicate arXiv Preprints
        dedup_arx = []
        for p in (arx_1 + arx_2):
            t = p.get("title", "").strip().lower()
            if t and t not in seen_titles:
                seen_titles.add(t)
                dedup_arx.append(p)

        # 3. Build Rich Multi-Paper Cross-Disciplinary Evidence Dossier
        dossier_lines = [
            f"### 🌐 Round {round_num} Live Multi-Disciplinary Research Dossier ({len(dedup_alex) + len(dedup_arx)} Papers + {len(dedup_web)} Web Sources):",
            f"*Queried across OpenAlex (250M Papers Polite Pool), arXiv Preprints, and Tavily Deep AI Search.*",
            ""
        ]

        combined_answer = tav_1.get("answer", "") or tav_2.get("answer", "")
        if combined_answer:
            dossier_lines.append(f"**🌐 Live Web Synthesis**: {combined_answer}\n")

        source_count = 1
        sources_list = []

        # 1. Peer-Reviewed Papers from OpenAlex
        if dedup_alex:
            dossier_lines.append("#### 📚 Peer-Reviewed Research Papers (OpenAlex / IEEE / Nature / Springer):")
            for item in dedup_alex[:8]:
                pdf_link = f" ([PDF]({item['pdf_url']}))" if item.get("pdf_url") else ""
                cite_info = f" ({item['year']} · {item['citations']} citations)" if item.get('year') else ""
                concepts_info = f" [Tags: {', '.join(item.get('concepts', []))}]" if item.get("concepts") else ""
                dossier_lines.append(f"- **[Paper {source_count}]** {item['title']}{cite_info}{pdf_link}{concepts_info}")
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

        # 2. arXiv Preprints
        if dedup_arx:
            dossier_lines.append("#### ⚡ Cutting-Edge Preprints & AI Algorithms (arXiv):")
            for item in dedup_arx[:5]:
                dossier_lines.append(f"- **[Preprint {source_count}]** [{item['title']}]({item['link']}): {item['summary']}")
                sources_list.append({
                    "tag": f"Preprint {source_count}",
                    "title": item["title"],
                    "url": item["link"],
                    "type": "arXiv Preprint"
                })
                source_count += 1
            dossier_lines.append("")

        # 3. Web Sources from Tavily
        if dedup_web:
            dossier_lines.append("#### 🌐 Live Industry Standards & Government Portals (Tavily):")
            for item in dedup_web[:6]:
                dossier_lines.append(f"- **[Source {source_count}]** [{item['title']}]({item['url']}): {item['content']}")
                sources_list.append({
                    "tag": f"Source {source_count}",
                    "title": item["title"],
                    "url": item["url"],
                    "type": "Web"
                })
                source_count += 1
            dossier_lines.append("")

        # Cross-Paper Synthesis Prompting
        dossier_lines.append("💡 **CROSS-PAPER SYNTHESIS INSTRUCTION FOR DEBATERS**:")
        dossier_lines.append("Look for novel intersections across the papers above (e.g. combining Sensor Topology from [Paper 1] with the Edge ML Filter from [Preprint 2] and Network Protocol from [Source 3]). Ground all performance claims with explicit [Paper X] / [Source Y] citations.")

        dossier_text = "\n".join(dossier_lines)

        return {
            "round_num": round_num,
            "dossier_text": dossier_text,
            "web_summary": combined_answer,
            "sources": sources_list,
            "total_sources": len(sources_list)
        }
