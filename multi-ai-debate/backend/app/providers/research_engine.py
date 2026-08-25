import asyncio
import os
import re
import json
import httpx
import xml.etree.ElementTree as ET
import urllib.parse
from typing import Dict, List, Optional, Any, Tuple
from app.schemas import PooledResearchDossier, ResearchDossierItem, AutonomousResearchCall

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

RESEARCH_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "research_config.json")

class ResearchEngine:
    DEFAULT_CONFIG = {
        "enabled": True,
        "tavily_api_key": "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",
        "openalex_email": "campusprintexpress@gmail.com",
        "max_papers_per_round": 12,
        "max_web_sources_per_round": 8,
        "download_pdfs": True
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
    async def search_tavily(cls, query: str, api_key: Optional[str] = None, max_results: int = 4) -> Dict[str, Any]:
        cfg = cls.get_config()
        key = api_key or cfg.get("tavily_api_key", "").strip()
        if not key or not query.strip():
            return {"answer": "", "results": []}

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": key,
            "query": query.strip(),
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
    async def search_openalex(cls, query: str, max_results: int = 5, email: Optional[str] = None) -> List[Dict[str, Any]]:
        cfg = cls.get_config()
        user_email = email or cfg.get("openalex_email", "campusprintexpress@gmail.com")
        if not query.strip():
            return []
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
                        pdf_url = oa.get("oa_url", "")
                        # Structured abstract reconstruction if inverted index exists
                        abstract_text = ""
                        ab_idx = item.get("abstract_inverted_index")
                        if ab_idx and isinstance(ab_idx, dict):
                            word_positions = []
                            for word, positions in ab_idx.items():
                                for pos in positions:
                                    word_positions.append((pos, word))
                            word_positions.sort(key=lambda x: x[0])
                            abstract_text = " ".join([w[1] for w in word_positions])[:350]

                        papers.append({
                            "title": item.get("display_name", ""),
                            "year": item.get("publication_year", ""),
                            "citations": item.get("cited_by_count", 0),
                            "pdf_url": pdf_url,
                            "doi": item.get("doi", ""),
                            "summary": abstract_text or f"Academic publication indexed with {item.get('cited_by_count', 0)} citations.",
                            "concepts": [c.get("display_name") for c in item.get("concepts", [])[:3] if c.get("display_name")]
                        })
                    return papers
        except Exception as e:
            print(f"OpenAlex search error for '{query}': {e}")
        return []

    @classmethod
    async def search_arxiv(cls, query: str, max_results: int = 4) -> List[Dict[str, Any]]:
        if not query.strip():
            return []
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
                        pdf_link = link.replace("/abs/", "/pdf/") if "/abs/" in link else ""
                        summary = summary_el.text.strip()[:280] if summary_el is not None and summary_el.text else ""
                        papers.append({
                            "title": title,
                            "link": link,
                            "pdf_url": pdf_link,
                            "summary": summary
                        })
                    return papers
        except Exception as e:
            print(f"arXiv search error for '{query}': {e}")
        return []

    @classmethod
    async def download_and_extract_paper(cls, pdf_url: str, save_dir: str, filename_stem: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Downloads open-access PDF from arXiv/OpenAlex, saves both .pdf and .txt files,
        and returns (local_pdf_path, local_txt_path, extracted_capsule_text).
        """
        if not pdf_url or not pdf_url.startswith("http"):
            return None, None, ""

        os.makedirs(save_dir, exist_ok=True)
        pdf_path = os.path.join(save_dir, f"{filename_stem}.pdf")
        txt_path = os.path.join(save_dir, f"{filename_stem}.txt")

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=False) as client:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = await client.get(pdf_url, headers=headers)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    with open(pdf_path, "wb") as f:
                        f.write(resp.content)

                    extracted_text = ""
                    if PYPDF_AVAILABLE:
                        try:
                            reader = PdfReader(pdf_path)
                            pages_text = []
                            for p_idx in range(min(5, len(reader.pages))):
                                page_text = reader.pages[p_idx].extract_text()
                                if page_text:
                                    pages_text.append(page_text)
                            extracted_text = "\n\n".join(pages_text)
                        except Exception as parse_err:
                            extracted_text = f"PDF downloaded but parsing encountered: {parse_err}"
                    else:
                        extracted_text = "PDF downloaded (pypdf not available for local parsing)."

                    # Save full text to txt file
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(extracted_text)

                    # Return capsule (first 500 chars clean text)
                    capsule = re.sub(r'\s+', ' ', extracted_text[:500]).strip()
                    return pdf_path, txt_path, capsule
        except Exception as e:
            print(f"Failed to download/parse PDF from {pdf_url}: {e}")

        return None, None, ""

    @classmethod
    async def conduct_pooled_research(
        cls,
        workspace_dir: str,
        phase_index: int,
        round_num: int,
        session_title: str,
        problem_statement: str,
        debater_research_calls: Optional[List[AutonomousResearchCall]] = None,
        previous_friction: Optional[List[str]] = None,
        tavily_key: Optional[str] = None,
        openalex_email: Optional[str] = None
    ) -> PooledResearchDossier:
        """
        Standardized 3-Stage Pooled Research Engine (The Always-On Hive-Mind):
        Stage 1: Pooled Peer Fact-Check & Claims (Tavily)
        Stage 2: Pooled Frontier Academic Discovery & SOTA Papers (OpenAlex + arXiv + PDF Download & Distillation)
        Stage 3: Pooled Real-World Feasibility, Indian Standards & Failure Benchmarks (Tavily)
        """
        cfg = cls.get_config()
        if not cfg.get("enabled", True):
            return PooledResearchDossier(round_num=round_num, phase_index=phase_index, dossier_text="")

        research_folder = os.path.join(workspace_dir, "research")
        os.makedirs(research_folder, exist_ok=True)

        raw_problem = (problem_statement or session_title or "").strip()
        cleaned = re.sub(r'^(Develop|Design|Build|Create|Implement|Formulate|Propose)\s+(an?|the)?\s*', '', raw_problem, flags=re.IGNORECASE)
        cleaned = re.sub(r'^(AI-driven|AI-based|Smart|Intelligent|Automated)\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^(system|solution|platform|tool|framework)\s+(for|to)\s*', '', cleaned, flags=re.IGNORECASE)
        topic_clean = cleaned.split(".")[0].strip()[:80] or session_title.replace("_", " ")

        # 1. Harvest and group AI autonomous research calls into stages
        stage_1_queries = []
        stage_2_queries = []
        stage_3_queries = []

        if debater_research_calls:
            for rc in debater_research_calls:
                q = rc.search_query.strip()
                if not q:
                    continue
                if rc.stage == "fact_check":
                    stage_1_queries.append(q)
                elif rc.stage == "frontier_academic":
                    stage_2_queries.append(q)
                elif rc.stage == "field_feasibility":
                    stage_3_queries.append(q)

        # Fallback queries based on the actual problem domain if AI debater queries are sparse
        if not stage_1_queries:
            stage_1_queries.append(f"{topic_clean} specifications performance benchmarks fact check")
            stage_1_queries.append(f"{topic_clean} system architecture feasibility analysis")

        if not stage_2_queries:
            stage_2_queries.append(f"{topic_clean} state of the art algorithms models architecture")
            stage_2_queries.append(f"{topic_clean} optimization framework open access research")

        if not stage_3_queries:
            friction_hint = " ".join(previous_friction or [])[:60] if previous_friction else "scalability security Indian deployment"
            stage_3_queries.append(f"{topic_clean} {friction_hint} real world deployment benchmarks")
            stage_3_queries.append(f"{topic_clean} statutory compliance standards guidelines India")

        # --- EXECUTE STAGE 1: FACT-CHECK & CLAIMS ---
        stage_1_tasks = [cls.search_tavily(q[:80], api_key=tavily_key, max_results=3) for q in stage_1_queries[:3]]
        stage_1_results = await asyncio.gather(*stage_1_tasks, return_exceptions=True)

        stage_1_items: List[ResearchDossierItem] = []
        seen_urls = set()
        s1_counter = 1
        for res in stage_1_results:
            if isinstance(res, dict):
                for r in res.get("results", []):
                    u = r.get("url", "")
                    if u and u not in seen_urls:
                        seen_urls.add(u)
                        stage_1_items.append(ResearchDossierItem(
                            tag=f"Fact-Check {s1_counter}",
                            title=r.get("title", ""),
                            url=u,
                            type="Web",
                            summary=r.get("content", "")[:320]
                        ))
                        s1_counter += 1

        # --- EXECUTE STAGE 2: FRONTIER ACADEMIC & PREPRINTS ---
        alex_tasks = [cls.search_openalex(q[:75], max_results=4, email=openalex_email) for q in stage_2_queries[:2]]
        arxiv_tasks = [cls.search_arxiv(q[:60], max_results=3) for q in stage_2_queries[:2]]
        stage_2_raw = await asyncio.gather(*alex_tasks, *arxiv_tasks, return_exceptions=True)

        stage_2_items: List[ResearchDossierItem] = []
        seen_titles = set()
        s2_counter = 1
        download_tasks = []

        for group in stage_2_raw:
            if isinstance(group, list):
                for p in group:
                    t = p.get("title", "").strip()
                    t_low = t.lower()
                    if t and t_low not in seen_titles:
                        seen_titles.add(t_low)
                        is_arxiv = "arxiv" in p.get("link", "") or "Preprint" in p.get("type", "")
                        item_type = "arXiv Preprint" if is_arxiv else "Academic Paper"
                        url = p.get("pdf_url") or p.get("link") or p.get("doi") or "https://openalex.org"
                        tag = f"Paper {s2_counter}"

                        item = ResearchDossierItem(
                            tag=tag,
                            title=t,
                            url=url,
                            type=item_type,
                            year=p.get("year"),
                            citations=p.get("citations"),
                            summary=p.get("summary", "")
                        )
                        stage_2_items.append(item)
                        s2_counter += 1

                        # Async PDF Download for open access links
                        pdf_target = p.get("pdf_url")
                        if cfg.get("download_pdfs", True) and pdf_target and len(download_tasks) < 4:
                            stem = f"paper_p{phase_index}_r{round_num}_{len(download_tasks)+1}"
                            download_tasks.append((item, pdf_target, stem))

        # Download PDFs in background
        downloaded_count = 0
        if download_tasks:
            d_futures = [cls.download_and_extract_paper(target, research_folder, stem) for _, target, stem in download_tasks]
            d_results = await asyncio.gather(*d_futures, return_exceptions=True)
            for idx, d_res in enumerate(d_results):
                if isinstance(d_res, tuple) and d_res[0]:
                    item_ref = download_tasks[idx][0]
                    item_ref.local_pdf_path = d_res[0]
                    item_ref.local_txt_path = d_res[1]
                    if d_res[2]:
                        item_ref.summary = f"[Distilled Full-Text Excerpt]: {d_res[2]}"
                    downloaded_count += 1

        # --- EXECUTE STAGE 3: REAL-WORLD FEASIBILITY & FAILURE BENCHMARKS ---
        stage_3_tasks = [cls.search_tavily(q[:80], api_key=tavily_key, max_results=3) for q in stage_3_queries[:3]]
        stage_3_results = await asyncio.gather(*stage_3_tasks, return_exceptions=True)

        stage_3_items: List[ResearchDossierItem] = []
        s3_counter = 1
        for res in stage_3_results:
            if isinstance(res, dict):
                for r in res.get("results", []):
                    u = r.get("url", "")
                    if u and u not in seen_urls:
                        seen_urls.add(u)
                        stage_3_items.append(ResearchDossierItem(
                            tag=f"Feasibility {s3_counter}",
                            title=r.get("title", ""),
                            url=u,
                            type="Web",
                            summary=r.get("content", "")[:320]
                        ))
                        s3_counter += 1

        # --- COMPILE 3-STAGE POOLED RESEARCH INTELLIGENCE DOSSIER ---
        dossier_lines = [
            f"### 🔬 STANDARDIZED 3-STAGE POOLED RESEARCH DOSSIER (Phase {phase_index} · Round {round_num}):",
            f"*Pooled across OpenAlex (250M Papers Graph), arXiv Preprints, and Tavily Deep AI Search.*",
            f"*Downloaded & Ingested Full-Text Papers: {downloaded_count} papers stored in local workspace `research/` directory.*",
            ""
        ]

        # Stage 1 Lines
        if stage_1_items:
            dossier_lines.append("#### 🔍 STAGE 1: POOLED FACT-CHECK & CLAIM VERIFICATION")
            for item in stage_1_items[:4]:
                dossier_lines.append(f"- **[{item.tag}]** [{item.title}]({item.url}): {item.summary}")
            dossier_lines.append("")

        # Stage 2 Lines
        if stage_2_items:
            dossier_lines.append("#### 📚 STAGE 2: POOLED FRONTIER ACADEMIC & SOTA ALGORITHM PAPERS")
            for item in stage_2_items[:6]:
                cite_txt = f" ({item.year} · {item.citations} citations)" if item.year else ""
                local_badge = " [📥 PDF+TXT Downloaded]" if item.local_pdf_path else ""
                dossier_lines.append(f"- **[{item.tag}]** [{item.title}]({item.url}){cite_txt}{local_badge}: {item.summary}")
            dossier_lines.append("")

        # Stage 3 Lines
        if stage_3_items:
            dossier_lines.append("#### ⚙️ STAGE 3: POOLED REAL-WORLD FEASIBILITY, INDIAN BOM & FAILURE BENCHMARKS")
            for item in stage_3_items[:4]:
                dossier_lines.append(f"- **[{item.tag}]** [{item.title}]({item.url}): {item.summary}")
            dossier_lines.append("")

        dossier_lines.append("💡 **DEBATER MANDATORY CITATION PROTOCOL**:")
        dossier_lines.append("You MUST substantiate all architectural specs, BOM component costs, latency bounds, and algorithm parameters using explicit inline citations (e.g. `[Paper 1]`, `[Fact-Check 2]`, `[Feasibility 1]`).")

        dossier_text = "\n".join(dossier_lines)
        total_sources = len(stage_1_items) + len(stage_2_items) + len(stage_3_items)

        return PooledResearchDossier(
            round_num=round_num,
            phase_index=phase_index,
            stage_1_fact_checks=stage_1_items,
            stage_2_academic_papers=stage_2_items,
            stage_3_field_benchmarks=stage_3_items,
            dossier_text=dossier_text,
            web_summary=stage_1_items[0].summary if stage_1_items else "",
            total_sources=total_sources,
            downloaded_papers_count=downloaded_count
        )

    # Backwards-compatible bridge for any legacy calls
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
        temp_calls = [AutonomousResearchCall(search_query=q) for q in (ai_requested_queries or [])]
        dossier = await cls.conduct_pooled_research(
            workspace_dir=os.path.join(os.path.dirname(__file__), "..", "..", "data"),
            phase_index=1,
            round_num=round_num,
            session_title=session_title,
            problem_statement=problem_statement,
            debater_research_calls=temp_calls,
            previous_friction=previous_friction,
            tavily_key=tavily_key,
            openalex_email=openalex_email
        )
        sources_list = []
        for itm in (dossier.stage_1_fact_checks + dossier.stage_2_academic_papers + dossier.stage_3_field_benchmarks):
            sources_list.append({
                "tag": itm.tag,
                "title": itm.title,
                "url": itm.url,
                "type": itm.type,
                "year": itm.year,
                "citations": itm.citations,
                "local_pdf_path": itm.local_pdf_path,
                "local_txt_path": itm.local_txt_path
            })
        return {
            "round_num": round_num,
            "dossier_text": dossier.dossier_text,
            "web_summary": dossier.web_summary,
            "sources": sources_list,
            "total_sources": dossier.total_sources,
            "downloaded_papers_count": dossier.downloaded_papers_count
        }

