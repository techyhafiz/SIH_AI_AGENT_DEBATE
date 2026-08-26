import json
import re
import asyncio
import httpx
import urllib.parse
from typing import AsyncGenerator, Dict, Any, Optional, Tuple, List
from app.schemas import ModelConfig, StructuredDebateTurn, CritiqueItem, ConcessionItem, AutonomousResearchCall
from app.providers.http_transport import build_async_client

# Marker key injected by the JSON recovery layer so downstream parsers can tell a
# genuinely-parsed object from a heuristically-salvaged one. Never sent to a provider.
PARSE_OK_KEY = "__parse_ok__"

# The scratchpad now lives OUTSIDE the JSON object (see prompts._CONTRACT_PREAMBLE).
# Both tag spellings are accepted: `<scratchpad>` is what the current contract asks for,
# `<deliberation_scratchpad>` is what older sessions and older prompts produced.
_SCRATCHPAD_RE = re.compile(
    r"<(scratchpad|deliberation_scratchpad|thinking)>([\s\S]*?)</\1>", re.IGNORECASE
)


def _strip_scratchpad(text: str) -> Tuple[str, str]:
    """Returns (scratchpad_text, text_with_scratchpad_removed)."""
    found: List[str] = []

    def _collect(m: "re.Match") -> str:
        found.append(m.group(2).strip())
        return "\n"

    remainder = _SCRATCHPAD_RE.sub(_collect, text)

    # An unclosed scratchpad tag (output truncated mid-reasoning) would otherwise leave
    # the opening tag glued to the JSON candidate.
    open_only = re.search(r"<(scratchpad|deliberation_scratchpad|thinking)>", remainder, re.IGNORECASE)
    if open_only:
        found.append(remainder[open_only.end():].strip())
        remainder = remainder[:open_only.start()]

    return "\n\n".join(p for p in found if p), remainder


def _close_truncated_json(candidate: str) -> str:
    """
    Repairs a JSON object that was cut off by a max_tokens ceiling by closing the open
    string, then the open containers, in the right order.

    This matters more than it looks: a debater that spends its budget on prose and gets
    truncated mid-object used to lose its entire turn - architecture, solution, critiques,
    vote - and be scored as a non-submission. Recovering the completed prefix keeps the
    argument in the debate.
    """
    stack: List[str] = []
    in_string = False
    escaped = False

    for ch in candidate:
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if stack:
                stack.pop()

    if not in_string and not stack:
        return candidate

    out = candidate
    if in_string:
        # Drop a dangling escape that would swallow our closing quote.
        if escaped:
            out = out[:-1]
        out += '"'

    # Remove a trailing key-with-no-value or a dangling comma before closing.
    out = re.sub(r",\s*$", "", out.rstrip())
    out = re.sub(r'(?:,\s*)?"[^"\\]*"\s*:\s*$', "", out.rstrip())
    out = re.sub(r",\s*$", "", out.rstrip())

    for opener in reversed(stack):
        out += "}" if opener == "{" else "]"
    return out


def extract_scratchpad_and_json(text: str) -> Tuple[str, Dict[str, Any], bool]:
    """
    Splits a model turn into (scratchpad, parsed_json, parse_ok).

    parse_ok is False when no JSON object could be recovered and the caller is holding
    heuristically-salvaged prose. It must NOT be treated as a valid structured position:
    the old code manufactured a `DISAGREE`/50 verdict here from keyword matching, which
    then flowed straight into the headline consensus score.
    """
    scratchpad_content, body = _strip_scratchpad((text or "").strip())
    body = body.strip()

    candidates: List[str] = []

    fenced = re.findall(r"```(?:json)?\s*([\s\S]*?)```", body, re.IGNORECASE)
    candidates.extend(f.strip() for f in fenced if f.strip())

    # An unterminated ```json fence (truncated output) leaves no closing backticks.
    open_fence = re.search(r"```(?:json)?\s*", body, re.IGNORECASE)
    if open_fence and not fenced:
        candidates.append(body[open_fence.end():].strip())

    first_brace = body.find("{")
    last_brace = body.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidates.append(body[first_brace:last_brace + 1])
    if first_brace != -1:
        candidates.append(body[first_brace:])

    if body:
        candidates.append(body)

    seen = set()
    for cand in candidates:
        if not cand or cand in seen:
            continue
        seen.add(cand)
        for attempt in (
            cand,
            re.sub(r",\s*([}\]])", r"\1", cand),
            _close_truncated_json(re.sub(r",\s*([}\]])", r"\1", cand)),
        ):
            try:
                data = json.loads(attempt)
            except Exception:
                continue
            if isinstance(data, dict):
                if scratchpad_content and not data.get("deliberation_scratchpad"):
                    data["deliberation_scratchpad"] = scratchpad_content
                data[PARSE_OK_KEY] = True
                return scratchpad_content, data, True

    # No JSON survived. Salvage the prose as the solution body and leave the position
    # fields ABSENT so no fabricated vote enters the consensus arithmetic.
    salvage_source = body or (text or "")
    salvaged = re.sub(r"```(?:json|markdown)?|```", "", salvage_source).strip()
    fallback_data: Dict[str, Any] = {
        "deliberation_scratchpad": scratchpad_content,
        "architect_lens": "",
        "critic_lens": "",
        "critic_devil_advocate_lens": "",
        "field_hardware_lens": "",
        "pragmatist_feasibility_lens": "",
        "security_compliance_lens": "",
        "security_reliability_lens": "",
        "critiques": [],
        "self_identified_flaws": [],
        "concessions_and_defenses": [],
        "refined_solution": salvaged or scratchpad_content,
        "positives_of_approach": [],
        "negatives_and_risks": [],
        "autonomous_research_calls": [],
        "research_queries_for_next_round": [],
        "consensus_vote": None,
        "agreement_percentage": None,
        PARSE_OK_KEY: False,
    }
    return scratchpad_content, fallback_data, False


def extract_and_repair_json(text: str) -> Dict[str, Any]:
    """Back-compatible wrapper. Callers that only need the object keep working."""
    _scratchpad, data, _ok = extract_scratchpad_and_json(text)
    return data

def parse_structured_turn(raw_json_or_text: Any) -> StructuredDebateTurn:
    parse_ok = True
    if isinstance(raw_json_or_text, str):
        _scratchpad, data, parse_ok = extract_scratchpad_and_json(raw_json_or_text)
    elif isinstance(raw_json_or_text, dict):
        data = raw_json_or_text
        parse_ok = bool(data.get(PARSE_OK_KEY, True))
    else:
        data = {}
        parse_ok = False

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

    research_calls = []
    for rc in data.get("autonomous_research_calls", []):
        if isinstance(rc, dict):
            stage = rc.get("stage", "fact_check")
            if stage not in ["fact_check", "frontier_academic", "field_feasibility"]:
                stage = "fact_check"
            target_engine = rc.get("target_engine", "tavily_web")
            if target_engine not in ["openalex_arxiv", "tavily_web"]:
                target_engine = "tavily_web"
            research_calls.append(AutonomousResearchCall(
                stage=stage,
                target_engine=target_engine,
                query_purpose=str(rc.get("query_purpose", "")),
                search_query=str(rc.get("search_query", ""))
            ))

    # P3: a missing or unreadable position stays None. The old code defaulted to
    # DISAGREE/50, which silently injected a fabricated dissenting vote into the
    # consensus average every time a model's JSON failed to parse - understating the
    # measured score by ~10 points in the observed runs.
    vote = data.get("consensus_vote")
    if isinstance(vote, str):
        vote = vote.strip().upper().replace(" ", "_").replace("-", "_")
    if vote not in ["AGREE", "DISAGREE", "NEEDS_REFINEMENT"]:
        vote = None

    raw_pct = data.get("agreement_percentage")
    pct: Optional[int] = None
    if raw_pct is not None and not isinstance(raw_pct, bool):
        try:
            if isinstance(raw_pct, str):
                m = re.search(r"-?\d+", raw_pct)
                raw_pct = m.group(0) if m else None
            if raw_pct is not None:
                pct = max(0, min(100, int(float(raw_pct))))
        except Exception:
            pct = None

    architect = str(data.get("architect_lens", "")).strip()
    critic = str(data.get("critic_lens") or data.get("critic_devil_advocate_lens", "")).strip()
    hardware = str(data.get("field_hardware_lens") or data.get("pragmatist_feasibility_lens", "")).strip()
    security = str(data.get("security_compliance_lens") or data.get("security_reliability_lens", "")).strip()
    solution = str(data.get("refined_solution", "")).strip()

    # Fallback if refined_solution is empty so no model ever shows an empty card
    if not solution:
        if architect:
            solution = architect
        elif critic:
            solution = critic
        elif hardware:
            solution = hardware
        elif security:
            solution = security
        elif data.get("deliberation_scratchpad"):
            solution = str(data.get("deliberation_scratchpad")).strip()
        elif isinstance(raw_json_or_text, str) and raw_json_or_text.strip():
            # Clean up JSON code fences if raw text is passed
            clean_raw = re.sub(r"```(?:json)?|```", "", raw_json_or_text).strip()
            solution = clean_raw[:800]

    def _safe_str_list(val) -> List[str]:
        if isinstance(val, list):
            return [str(x).strip() for x in val if x and str(x).strip()]
        elif isinstance(val, str) and val.strip():
            return [val.strip()]
        return []

    queries = _safe_str_list(data.get("research_queries_for_next_round") or data.get("research_topics") or data.get("open_research_questions"))
    for rc in research_calls:
        if rc.search_query and rc.search_query not in queries:
            queries.append(rc.search_query)

    # P15: Phase-1 self red-teaming. Kept out of `critiques` so a model attacking its own
    # Pass 1.1 is never routed to a peer as if it were a peer critique.
    raw_flaws = data.get("self_identified_flaws") or data.get("self_identified_flaws_and_attacks")
    flaws: List[str] = []
    if isinstance(raw_flaws, list):
        for f in raw_flaws:
            if isinstance(f, dict):
                joined = " - ".join(str(v).strip() for v in f.values() if v and str(v).strip())
                if joined:
                    flaws.append(joined)
            elif f and str(f).strip():
                flaws.append(str(f).strip())
    elif isinstance(raw_flaws, str) and raw_flaws.strip():
        flaws.append(raw_flaws.strip())

    return StructuredDebateTurn(
        deliberation_scratchpad=str(data.get("deliberation_scratchpad", "")),
        architect_lens=architect,
        critic_lens=critic,
        critic_devil_advocate_lens=critic,
        field_hardware_lens=hardware,
        pragmatist_feasibility_lens=hardware,
        security_compliance_lens=security,
        security_reliability_lens=security,
        critiques=critiques_list,
        self_identified_flaws=flaws,
        concessions_and_defenses=concessions_list,
        refined_solution=solution,
        positives_of_approach=_safe_str_list(data.get("positives_of_approach")),
        negatives_and_risks=_safe_str_list(data.get("negatives_and_risks")),
        autonomous_research_calls=research_calls,
        research_queries_for_next_round=queries,
        consensus_vote=vote,
        agreement_percentage=pct,
        parse_ok=parse_ok
    )



class UniversalAIClient:

    UNIVERSAL_HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": "Cline/3.0.0",
        "HTTP-Referer": "https://sih.gov.in",
        "X-Title": "SIH Multi-AI Consensus Arena",
        "anthropic-version": "2023-06-01"
    }

    # Endpoints observed to reject `response_format`. Populated at runtime from the first
    # HTTP 400 so the probe cost is paid once per process, not once per turn.
    _JSON_MODE_BLOCKLIST: set = set()

    # Hosts whose OpenAI-compatible surface is known to accept
    # `response_format: {"type": "json_object"}`. Used only to resolve json_mode="auto";
    # an unlisted host simply falls back to prompt-level JSON, and a listed host that
    # turns out not to support it is caught by the 400 handler and blocklisted.
    _JSON_CAPABLE_HOST_HINTS = (
        "api.openai.com", "openrouter.ai", "api.deepseek.com", "api.together.xyz",
        "api.fireworks.ai", "api.groq.com", "api.mistral.ai", "api.x.ai",
        "generativelanguage.googleapis.com", "openai.azure.com", "api.cerebras.ai",
        "api.moonshot.cn", "dashscope", "api.perplexity.ai",
    )

    @classmethod
    def _supports_json_mode(cls, config: ModelConfig, target_url: str) -> bool:
        mode = getattr(config, "json_mode", "auto")
        if mode == "off":
            return False
        if target_url in cls._JSON_MODE_BLOCKLIST:
            return False
        if mode == "json_object":
            return True
        host = (urllib.parse.urlsplit(target_url).hostname or "").lower()
        return any(hint in host for hint in cls._JSON_CAPABLE_HOST_HINTS)

    @staticmethod
    def _normalize_chat_url(base_url: str) -> str:
        url = base_url.strip().rstrip("/")
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Provider base_url must use http or https and include a hostname")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Provider base_url cannot contain credentials, query parameters, or fragments")
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
                    headers = dict(cls.UNIVERSAL_HEADERS)
                    if key:
                        headers["Authorization"] = f"Bearer {key}"

                    # Allocate 120 max_tokens so reasoning models don't exhaust budget on thinking tokens.
                    # The probe text carries the model id because some routers (XKiro) de-duplicate
                    # in-flight requests by payload and answer the second one with
                    # HTTP 409 "A duplicate request is already being processed" - so a fleet sweep
                    # sending byte-identical probes was colliding with itself and reporting the
                    # losers as broken.
                    payload = {
                        "model": model_id,
                        "messages": [{"role": "user", "content": f"Respond with: READY [{model_id}#{key_idx}]"}],
                        "max_tokens": 120,
                        "temperature": 0.1
                    }

                    # Timed per attempt, not from the top of the loop: a model reached on the
                    # third candidate id used to report the cumulative cost of the two failures
                    # before it as its own latency, which is the number the wizard sorts on.
                    attempt_start = asyncio.get_event_loop().time()
                    # Clamped so a ModelConfig carrying the debate default of 600s cannot stall a
                    # connectivity check, but high enough that a caller asking for a deliberately
                    # patient probe (the discovery sweep's serial second-chance pass) gets it -
                    # small free hosts need well over 25s to cold-start their larger models, and
                    # clipping them reported working endpoints as dead.
                    timeout = min(90.0, float(config.timeout_seconds or 45))
                    async with build_async_client(timeout=timeout) as client:
                        resp = await client.post(target_url, headers=headers, json=payload)
                        elapsed_ms = (asyncio.get_event_loop().time() - attempt_start) * 1000

                        # Parameter auto-recovery. Reasoning-tier models on OpenAI-compatible
                        # surfaces reject `temperature` and require `max_completion_tokens`
                        # instead of `max_tokens`; without shedding both, an entire model family
                        # is reported dead over a payload detail.
                        if resp.status_code in (400, 422):
                            body_lower = resp.text.lower()
                            retry_payload = dict(payload)
                            dropped = []
                            if "temperature" in body_lower and "temperature" in retry_payload:
                                retry_payload.pop("temperature", None)
                                dropped.append("temperature")
                            if "max_completion_tokens" in body_lower or (
                                "max_tokens" in body_lower and "unsupported" in body_lower
                            ):
                                retry_payload.pop("max_tokens", None)
                                retry_payload["max_completion_tokens"] = 120
                                dropped.append("max_tokens->max_completion_tokens")
                            if dropped:
                                attempt_start = asyncio.get_event_loop().time()
                                resp = await client.post(target_url, headers=headers, json=retry_payload)
                                elapsed_ms = (asyncio.get_event_loop().time() - attempt_start) * 1000
                    if resp.status_code == 200:
                        data = resp.json()
                        
                        # 1. Check if error object exists in body
                        if isinstance(data, dict) and "error" in data:
                            err_val = data["error"]
                            err_str = err_val.get("message", str(err_val)) if isinstance(err_val, dict) else str(err_val)
                            last_err = f"API Error: {err_str}"
                            continue

                        # 2. Check choices array
                        choices = data.get("choices", []) if isinstance(data, dict) else []
                        if not isinstance(choices, list) or len(choices) == 0:
                            last_err = "No choices returned in API response"
                            continue

                        first_choice = choices[0]
                        if not isinstance(first_choice, dict):
                            last_err = "Invalid choice format"
                            continue

                        msg_obj = first_choice.get("message", {})
                        if not isinstance(msg_obj, dict):
                            last_err = "Invalid message object"
                            continue

                        raw_content = msg_obj.get("content")
                        reasoning = msg_obj.get("reasoning_content") or msg_obj.get("reasoning")
                        content_str = str(raw_content if raw_content is not None else (reasoning if reasoning is not None else "")).strip()

                        # 3. Empty content is only a failure if the model actually stopped.
                        # A reasoning model can spend the whole 120-token probe budget on hidden
                        # thinking and return finish_reason="length" with no visible content. The
                        # endpoint answered, billed tokens and is demonstrably alive, so reporting
                        # it as dead is a false negative.
                        if not content_str:
                            finish_reason = str(first_choice.get("finish_reason") or "").lower()
                            if finish_reason in ("length", "max_tokens"):
                                return (
                                    True,
                                    f"Verified Online! ({round(elapsed_ms)}ms) -> reasoning model, "
                                    f"probe budget consumed by thinking tokens",
                                    elapsed_ms,
                                    key,
                                )
                            last_err = "Empty token content returned by model"
                            continue

                        # 4. Check for plan/credit/quota rejection keywords
                        lower_content = content_str.lower()
                        error_keywords = [
                            "insufficient quota", "insufficient credits", "exceeded your current quota",
                            "requires credits", "no credits", "payment required", "out of credits",
                            "not available on your plan", "not available on your tier", "plan does not allow",
                            "unauthorized", "invalid api key", "[error:", "upstream error", "user not found"
                        ]
                        if any(kw in lower_content for kw in error_keywords):
                            last_err = f"Plan restriction: {content_str[:80]}"
                            continue

                        return True, f"Verified Online! ({round(elapsed_ms)}ms) -> {content_str[:30]}", elapsed_ms, key
                    elif resp.status_code == 402:
                        last_err = f"Balance Depleted (HTTP 402) on {model_id}: {resp.text[:200]}"
                    elif resp.status_code == 429:
                        last_err = f"Rate Limited (HTTP 429) on {model_id}: {resp.text[:200]}"
                    elif resp.status_code in (401, 403):
                        # The body must be carried through. Routers overwhelmingly use 403 for
                        # "this model needs credits / a paid plan" rather than for a bad key, so
                        # the caller can only tell a billing wall from a rejected credential by
                        # reading the message. Reporting all of these as "key rejected" both
                        # mislabels them and, in a full-catalogue sweep, trips the provider-wide
                        # auth short-circuit that then skips the models that would have worked.
                        last_err = f"HTTP {resp.status_code} on {model_id}: {resp.text[:250]}"
                    else:
                        last_err = f"HTTP {resp.status_code} on {model_id}: {resp.text[:200]}"
                except Exception as e:
                    # httpx connection errors frequently stringify to "", which produced the
                    # useless failure line "All 1 keys/models failed." with no cause attached.
                    detail = str(e).strip()
                    last_err = f"{type(e).__name__}: {detail}" if detail else type(e).__name__

        elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        # Counted honestly: the old line read "All 1 keys/models failed" even when it had walked
        # one key across four candidate ids, which made the message look like a single attempt.
        attempted = len(candidate_keys) * len(candidate_models)
        return False, f"All {attempted} key/model attempt(s) failed. {last_err}", elapsed_ms, None

    @classmethod
    async def stream_chat(
        cls,
        config: ModelConfig,
        messages: list,
        temperature: float = 0.7,
        on_key_promoted_cb=None,
        require_json: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Streams response tokens. If a key or model fails with 401/403/429/5xx, it rotates
        automatically to backup keys and fallback model IDs. If streaming yields 0 tokens or fails,
        it automatically falls back to standard non-streaming HTTP POST to ensure 100% completion.

        `require_json=True` asks for provider-native constrained JSON decoding when the endpoint
        is believed to support it. It is deliberately NOT used for debater turns: those emit a
        `<scratchpad>` block outside the JSON object (so long free-form reasoning can never
        invalidate the object through a stray quote), which pure-JSON mode forbids. It IS used for
        the arbiter evaluation, whose contract is a single bare JSON object with no prose around it.
        """
        target_url = cls._normalize_chat_url(config.base_url)
        candidate_keys = cls._get_candidate_keys(config)
        candidate_models = cls._get_candidate_models(config)
        use_json_mode = require_json and cls._supports_json_mode(config, target_url)

        timeout = httpx.Timeout(
            connect=60.0,
            read=float(config.timeout_seconds or 600),
            write=60.0,
            pool=60.0
        )

        last_exception: Optional[Exception] = None

        for key_idx, key in enumerate(candidate_keys):
            for model_id in candidate_models:
                headers = dict(cls.UNIVERSAL_HEADERS)
                if key:
                    headers["Authorization"] = f"Bearer {key}"

                payload = {
                    "model": model_id,
                    "messages": messages,
                    "stream": True,
                    "temperature": temperature,
                    "max_tokens": config.max_tokens
                }
                if use_json_mode:
                    payload["response_format"] = {"type": "json_object"}

                tokens_emitted = 0

                async def consume_response(response: httpx.Response) -> AsyncGenerator[str, None]:
                    nonlocal tokens_emitted
                    if response.status_code != 200:
                        body = (await response.aread()).decode("utf-8", errors="ignore")
                        raise RuntimeError(f"HTTP {response.status_code}: {body}")

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_json = json.loads(data_str)
                        except json.JSONDecodeError:
                            if data_str.startswith("[error:") or "Upstream error" in data_str:
                                raise RuntimeError(f"Upstream provider error: {data_str}")
                            continue

                        if not isinstance(chunk_json, dict):
                            continue
                        if "error" in chunk_json:
                            err_val = chunk_json["error"]
                            err_text = err_val.get("message", str(err_val)) if isinstance(err_val, dict) else str(err_val)
                            raise RuntimeError(f"Upstream provider error: {err_text}")
                        choices = chunk_json.get("choices")
                        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
                            continue
                        delta_obj = choices[0].get("delta")
                        if not isinstance(delta_obj, dict):
                            continue
                        delta = delta_obj.get("content") or delta_obj.get("reasoning_content") or delta_obj.get("reasoning") or ""
                        if not isinstance(delta, str) or not delta:
                            continue
                        clean_delta = delta.strip()
                        if clean_delta.startswith("[error:") or "Upstream error for model" in clean_delta:
                            raise RuntimeError(f"Upstream provider error: {clean_delta}")
                        tokens_emitted += 1
                        yield delta

                try:
                    async with build_async_client(timeout=timeout) as client:
                        async with client.stream("POST", target_url, headers=headers, json=payload) as response:
                            if response.status_code == 400:
                                error_body = (await response.aread()).decode("utf-8", errors="ignore")
                                lowered = error_body.lower()
                                # Progressive parameter shedding, retried inside the SAME live
                                # client so the connection and headers are preserved.
                                retry_payload = dict(payload)
                                dropped = []
                                if "response_format" in retry_payload and (
                                    "response_format" in lowered or "json_object" in lowered
                                    or "json mode" in lowered or "unsupported" in lowered
                                ):
                                    retry_payload.pop("response_format", None)
                                    cls._JSON_MODE_BLOCKLIST.add(target_url)
                                    dropped.append("response_format")
                                if "temperature" in lowered and "temperature" in retry_payload:
                                    retry_payload.pop("temperature", None)
                                    dropped.append("temperature")

                                if dropped:
                                    print(f"[PARAM RECOVERY] '{model_id}' rejected {dropped}; retrying without them.")
                                    async with client.stream("POST", target_url, headers=headers, json=retry_payload) as retry_response:
                                        async for delta in consume_response(retry_response):
                                            yield delta
                                else:
                                    raise RuntimeError(f"HTTP 400: {error_body}")
                            else:
                                async for delta in consume_response(response):
                                    yield delta

                    if tokens_emitted > 0:
                        if (key_idx > 0 or model_id != config.model_id) and on_key_promoted_cb:
                            promoted = config.model_copy(update={"api_key": key, "model_id": model_id})
                            await on_key_promoted_cb(promoted, key)
                        return

                except Exception as e:
                    if tokens_emitted > 0:
                        raise RuntimeError(f"Stream interrupted after partial output: {e}") from e
                    print(f"[FAILOVER] Streaming error on '{model_id}': {str(e)}. Attempting non-streaming fallback...")
                    last_exception = e

                if tokens_emitted == 0:
                    try:
                        payload_non_stream = {
                            "model": model_id,
                            "messages": messages,
                            "stream": False,
                            "max_tokens": config.max_tokens
                        }
                        async with build_async_client(timeout=timeout) as client:
                            post_resp = await client.post(target_url, headers=headers, json=payload_non_stream)
                            if post_resp.status_code == 200:
                                post_data = post_resp.json()
                                choices = post_data.get("choices", [])
                                if choices and isinstance(choices[0], dict):
                                    msg = choices[0].get("message", {})
                                    full_content = msg.get("content") or msg.get("reasoning_content") or ""
                                    if full_content:
                                        print(f"[NON-STREAM RESCUE] Rescued Model '{model_id}' via direct HTTP POST fallback ({len(full_content)} chars)")
                                        if (key_idx > 0 or model_id != config.model_id) and on_key_promoted_cb:
                                            promoted = config.model_copy(update={"api_key": key, "model_id": model_id})
                                            await on_key_promoted_cb(promoted, key)
                                        yield full_content
                                        return
                    except Exception as ns_err:
                        print(f"[NON-STREAM RESCUE FAILED] {ns_err}")
                        last_exception = ns_err
                        continue

        if last_exception:
            raise last_exception
        raise RuntimeError(f"All candidate API keys failed for Model '{config.name}'.")
