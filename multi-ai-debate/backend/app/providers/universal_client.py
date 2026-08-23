import json
import re
import asyncio
import httpx
from typing import AsyncGenerator, Dict, Any, Optional, Tuple, List
from app.schemas import ModelConfig, StructuredDebateTurn, CritiqueItem, ConcessionItem

def extract_and_repair_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    
    # 1. Match ```json ... ``` or ``` ... ``` code blocks
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
    else:
        # 2. Match the first outer { ... } block
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            cleaned = cleaned[first_brace:last_brace + 1]

    # Try standard json parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Basic repair: remove trailing commas before } or ]
    repaired = re.sub(r",\s*([}\]])", r"\1", cleaned)
    try:
        return json.loads(repaired)
    except Exception:
        pass

    # Fallback: extract key sections
    fallback_data: Dict[str, Any] = {
        "architect_lens": "",
        "critic_devil_advocate_lens": "",
        "security_reliability_lens": "",
        "pragmatist_feasibility_lens": "",
        "critiques": [],
        "concessions_and_defenses": [],
        "refined_solution": text,
        "positives_of_approach": [],
        "negatives_and_risks": [],
        "consensus_vote": "DISAGREE",
        "agreement_percentage": 50
    }
    
    if "agree" in text.lower() and "disagree" not in text.lower():
        fallback_data["consensus_vote"] = "AGREE"
        fallback_data["agreement_percentage"] = 85
    elif "refinement" in text.lower():
        fallback_data["consensus_vote"] = "NEEDS_REFINEMENT"
        fallback_data["agreement_percentage"] = 65

    return fallback_data

def parse_structured_turn(raw_json_or_text: Any) -> StructuredDebateTurn:
    if isinstance(raw_json_or_text, str):
        data = extract_and_repair_json(raw_json_or_text)
    elif isinstance(raw_json_or_text, dict):
        data = raw_json_or_text
    else:
        data = {}

    critiques_list = []
    for c in data.get("critiques", []):
        if isinstance(c, dict):
            critiques_list.append(CritiqueItem(
                target_model_id=str(c.get("target_model_id", "")),
                target_model_name=str(c.get("target_model_name", "")),
                flaw_identified=str(c.get("flaw_identified", "")),
                counter_argument=str(c.get("counter_argument", ""))
            ))

    concessions_list = []
    for cd in data.get("concessions_and_defenses", []):
        if isinstance(cd, dict):
            concessions_list.append(ConcessionItem(
                conceded_point=str(cd.get("conceded_point", "")),
                conceded_to=str(cd.get("conceded_to", "")),
                adaptation=str(cd.get("adaptation", ""))
            ))

    vote = data.get("consensus_vote", "DISAGREE")
    if vote not in ["AGREE", "DISAGREE", "NEEDS_REFINEMENT"]:
        vote = "DISAGREE"

    pct = data.get("agreement_percentage", 50)
    try:
        pct = int(pct)
    except Exception:
        pct = 50

    return StructuredDebateTurn(
        architect_lens=str(data.get("architect_lens", "")),
        critic_devil_advocate_lens=str(data.get("critic_devil_advocate_lens", "")),
        security_reliability_lens=str(data.get("security_reliability_lens", "")),
        pragmatist_feasibility_lens=str(data.get("pragmatist_feasibility_lens", "")),
        critiques=critiques_list,
        concessions_and_defenses=concessions_list,
        refined_solution=str(data.get("refined_solution", "")),
        positives_of_approach=[str(x) for x in data.get("positives_of_approach", []) if x],
        negatives_and_risks=[str(x) for x in data.get("negatives_and_risks", []) if x],
        research_queries_for_next_round=[str(x) for x in (data.get("research_queries_for_next_round") or data.get("research_topics") or data.get("open_research_questions") or []) if x],
        consensus_vote=vote,
        agreement_percentage=pct
    )

class UniversalAIClient:

    @staticmethod
    def _normalize_chat_url(base_url: str) -> str:
        url = base_url.strip().rstrip("/")
        if not url.endswith("/chat/completions"):
            if url.endswith("/v1"):
                url = f"{url}/chat/completions"
            else:
                url = f"{url}/v1/chat/completions"
        return url

    @classmethod
    def _get_candidate_keys(cls, config: ModelConfig) -> List[str]:
        keys = []
        if config.api_key and config.api_key.strip():
            keys.append(config.api_key.strip())
        for bk in config.backup_api_keys:
            bk_clean = bk.strip()
            if bk_clean and bk_clean not in keys:
                keys.append(bk_clean)
        # If no keys specified (e.g. Ollama local), allow empty string as single candidate
        if not keys:
            keys.append("")
        return keys

    @classmethod
    def _get_candidate_models(cls, config: ModelConfig) -> List[str]:
        models = [config.model_id]
        for fm in config.fallback_model_ids:
            fm_clean = fm.strip()
            if fm_clean and fm_clean not in models:
                models.append(fm_clean)
        return models

    @classmethod
    async def test_connectivity(cls, config: ModelConfig) -> Tuple[bool, str, float, Optional[str]]:
        """
        Tests primary and backup keys across candidate models. Returns (success, message, latency_ms, working_key)
        """
        start_time = asyncio.get_event_loop().time()
        target_url = cls._normalize_chat_url(config.base_url)
        candidate_keys = cls._get_candidate_keys(config)
        candidate_models = cls._get_candidate_models(config)
        last_err = ""

        for key_idx, key in enumerate(candidate_keys):
            for model_id in candidate_models:
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "User-Agent": "Cline/3.0.0"
                    }
                    if key:
                        headers["Authorization"] = f"Bearer {key}"

                    payload = {
                        "model": model_id,
                        "messages": [{"role": "user", "content": "Respond with: READY"}],
                        "max_tokens": 10,
                        "temperature": 0.1
                    }

                    async with httpx.AsyncClient(timeout=config.timeout_seconds, verify=False) as client:
                        resp = await client.post(target_url, headers=headers, json=payload)
                        elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                        
                        if resp.status_code == 200:
                            data = resp.json()
                            msg_obj = data.get("choices", [{}])[0].get("message", {})
                            content = (msg_obj.get("content") or msg_obj.get("reasoning_content") or msg_obj.get("reasoning") or "READY")
                            key_desc = f"Key #{key_idx + 1}" if len(candidate_keys) > 1 else "Primary Key"
                            model_desc = f"Model '{model_id}'" if len(candidate_models) > 1 else ""
                            return True, f"Connected with {key_desc} {model_desc}! Response: {str(content).strip()[:30]}", elapsed_ms, key
                        else:
                            last_err = f"HTTP {resp.status_code} on {model_id}: {resp.text}"
                except Exception as e:
                    last_err = str(e)

        elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        return False, f"All {len(candidate_keys)} keys and {len(candidate_models)} models failed. Last error: {last_err}", elapsed_ms, None

    @classmethod
    async def stream_chat(
        cls,
        config: ModelConfig,
        messages: list,
        temperature: float = 0.7,
        on_key_promoted_cb=None
    ) -> AsyncGenerator[str, None]:
        """
        Streams response tokens. If a key or model fails with 401/403/429/5xx, it rotates
        automatically to backup keys and fallback model IDs (combining message quotas).
        """
        target_url = cls._normalize_chat_url(config.base_url)
        candidate_keys = cls._get_candidate_keys(config)
        candidate_models = cls._get_candidate_models(config)
        
        timeout = httpx.Timeout(
            connect=60.0,
            read=float(config.timeout_seconds),
            write=60.0,
            pool=60.0
        )

        last_exception = None

        for key_idx, key in enumerate(candidate_keys):
            for model_id in candidate_models:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Cline/3.0.0"
                }
                if key:
                    headers["Authorization"] = f"Bearer {key}"

                payload = {
                    "model": model_id,
                    "messages": messages,
                    "stream": True,
                    "temperature": temperature
                }

                try:
                    async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
                        async with client.stream("POST", target_url, headers=headers, json=payload) as response:
                            if response.status_code in [401, 402, 403, 429, 500, 502, 503, 504]:
                                err_body = await response.aread()
                                err_str = err_body.decode('utf-8', errors='ignore')
                                print(f"[FAILOVER] Model '{model_id}' Key #{key_idx + 1} failed with HTTP {response.status_code}. Rotating to fallback models/keys...")
                                last_exception = RuntimeError(f"HTTP {response.status_code}: {err_str}")
                                continue  # Try next model / backup key

                            if response.status_code != 200:
                                err_body = await response.aread()
                                last_exception = RuntimeError(f"HTTP {response.status_code}: {err_body.decode('utf-8', errors='ignore')}")
                                continue

                            # If we reached here on a backup key (key_idx > 0), promote this key as primary!
                            if key_idx > 0 and key != config.api_key:
                                config.api_key = key
                                print(f"[PROMOTED KEY] Promoted Backup Key #{key_idx + 1} to Primary for Model '{config.name}'")
                                if on_key_promoted_cb:
                                    await on_key_promoted_cb(config, key)

                            # If we reached here on a fallback model, update current active model
                            if model_id != config.model_id:
                                print(f"[ROTATED MODEL] Switched active model from '{config.model_id}' to pooled '{model_id}'")
                                config.model_id = model_id

                            async for line in response.aiter_lines():
                                line = line.strip()
                                if not line:
                                    continue
                                if line.startswith("data: "):
                                    data_str = line[6:].strip()
                                    if data_str == "[DONE]":
                                        break
                                    try:
                                        chunk_json = json.loads(data_str)
                                        if "error" in chunk_json:
                                            err_val = chunk_json["error"]
                                            err_text = err_val.get("message", str(err_val)) if isinstance(err_val, dict) else str(err_val)
                                            raise RuntimeError(f"Upstream provider error: {err_text}")

                                        delta_obj = chunk_json.get("choices", [{}])[0].get("delta", {})
                                        delta = delta_obj.get("content") or delta_obj.get("reasoning_content") or delta_obj.get("reasoning") or ""
                                        if delta:
                                            if delta.strip().startswith("[error:") or "Upstream error for model" in delta:
                                                raise RuntimeError(f"Upstream provider error: {delta.strip()}")
                                            yield delta
                                    except json.JSONDecodeError:
                                        if data_str.startswith("[error:") or "Upstream error" in data_str:
                                            raise RuntimeError(f"Upstream provider error: {data_str}")
                                        pass
                            return  # Stream finished successfully
                except Exception as e:
                    print(f"[FAILOVER] Error with Model '{model_id}' Key #{key_idx + 1}: {str(e)}")
                    last_exception = e
                    continue

        # If all candidate keys failed:
        if last_exception:
            raise last_exception
        raise RuntimeError(f"All candidate API keys failed for Model '{config.name}'.")
