import asyncio
import json
from app.schemas import ModelConfig, StructuredDebateTurn, PooledResearchDossier, ResearchDossierItem
from app.providers.universal_client import (
    extract_and_repair_json,
    extract_scratchpad_and_json,
    parse_structured_turn,
    UniversalAIClient,
)
from app.engine.orchestrator import heal_unstructured_turn, DebateOrchestrator
from app.engine.consensus_eval import (
    unwrap_markdown_deliverable,
    sanitize_hallucinated_citations,
    fit_prompt,
)
from app.engine.prompts import classify_problem_domain, build_schema_guide
from app.main import classify_probe_failure, classify_model_tier, AUTH_SHORTCIRCUIT_REASONS

def test_json_repair():
    raw_bad_json = """Here is my proposal for the debate:
    ```json
    {
      "architect_lens": "Distributed offline-first architecture",
      "critic_devil_advocate_lens": "Weakness in initial sync delay",
      "security_reliability_lens": "Zero-trust tokens",
      "pragmatist_feasibility_lens": "Low cost using SQLite",
      "critiques": [
        {
          "target_model_id": "m1",
          "target_model_name": "Claude",
          "flaw_identified": "Relies too heavily on high bandwidth",
          "counter_argument": "In rural Indian areas, 3G bandwidth will bottleneck."
        },
      ],
      "positives_of_approach": ["Sub-10ms response", "Fully offline capable"],
      "negatives_and_risks": ["Storage limits on mobile client"],
      "consensus_vote": "AGREE",
      "agreement_percentage": 95,
    }
    ```
    I hope all models agree with this!"""

    parsed = extract_and_repair_json(raw_bad_json)
    assert parsed["architect_lens"] == "Distributed offline-first architecture", "Failed architect lens parse"
    assert parsed["consensus_vote"] == "AGREE", "Failed vote parse"
    assert len(parsed["critiques"]) == 1, "Failed critiques parse"

    structured = parse_structured_turn(raw_bad_json)
    assert structured.consensus_vote == "AGREE"
    assert structured.agreement_percentage == 95
    assert structured.parse_ok is True
    assert len(structured.positives_of_approach) == 2
    print("[SUCCESS] JSON Extraction & Repair Test Passed!")

def test_url_normalization():
    assert UniversalAIClient._normalize_chat_url("https://openrouter.ai/api/v1") == "https://openrouter.ai/api/v1/chat/completions"
    assert UniversalAIClient._normalize_chat_url("http://localhost:11434/v1/") == "http://localhost:11434/v1/chat/completions"
    assert UniversalAIClient._normalize_chat_url("https://api.openai.com") == "https://api.openai.com/v1/chat/completions"
    assert UniversalAIClient._normalize_chat_url("https://api.groq.com/openai/v1/chat/completions") == "https://api.groq.com/openai/v1/chat/completions"
    print("[SUCCESS] URL Normalization Test Passed!")

def test_no_vote_is_ever_fabricated():
    """
    The parser must NOT infer a position from prose. It used to keyword-match ("agree"
    anywhere -> AGREE/85, "do not agree" -> DISAGREE/25) and that guessed vote flowed
    straight into the headline consensus score.
    """
    turn = parse_structured_turn("I do not agree with the current proposal.")
    assert turn.consensus_vote is None, "Prose must not produce a vote"
    assert turn.agreement_percentage is None, "Prose must not produce a percentage"
    assert turn.parse_ok is False
    assert "do not agree" in turn.refined_solution, "Prose content must still be preserved"

    agreeable = parse_structured_turn("This is a great plan and I agree completely with the consensus.")
    assert agreeable.consensus_vote is None
    assert agreeable.agreement_percentage is None

    healed = heal_unstructured_turn("## Architecture\nOffline mesh with durable queues.\n## Critic\nNetwork partitions remain risky.", "Mock")
    assert healed.architect_lens
    assert healed.critic_lens
    assert healed.consensus_vote is None, "Healing must not fabricate a vote"
    assert healed.parse_ok is False

    empty = heal_unstructured_turn("", "Mock")
    assert empty.consensus_vote is None and empty.agreement_percentage is None
    print("[SUCCESS] No-Fabricated-Vote Test Passed!")

def test_explicit_prose_vote_is_recovered():
    healed = heal_unstructured_turn(
        "## Architecture\nEdge mesh.\nconsensus_vote: NEEDS_REFINEMENT\nagreement_percentage: 62",
        "Mock",
    )
    assert healed.consensus_vote == "NEEDS_REFINEMENT"
    assert healed.agreement_percentage == 62
    print("[SUCCESS] Explicit Prose Vote Recovery Test Passed!")

def test_scratchpad_outside_json():
    raw = """<scratchpad>
Let me reason. The peer said "bandwidth is fine" - it is not: 3G gives ~0.5 Mbps.
Braces { } and backticks ``` in here must not break anything.
</scratchpad>
```json
{"architect_lens": "Store and forward", "refined_solution": "Full design", "consensus_vote": "DISAGREE", "agreement_percentage": 40}
```"""
    scratchpad, data, ok = extract_scratchpad_and_json(raw)
    assert ok is True, "Unescaped quotes in the scratchpad must not break the JSON"
    assert "0.5 Mbps" in scratchpad
    assert data["consensus_vote"] == "DISAGREE"
    assert data["agreement_percentage"] == 40
    print("[SUCCESS] Scratchpad-Outside-JSON Test Passed!")

def test_truncated_json_is_recovered():
    truncated = """```json
{
  "architect_lens": "Three-tier edge to cloud pipeline",
  "critic_lens": "The gateway is a single point of failure",
  "refined_solution": "The full design begins with LoRa nodes and then the text is cut off mid-sen"""
    scratchpad, data, ok = extract_scratchpad_and_json(truncated)
    assert ok is True, "A truncated object must be closed and recovered, not discarded"
    assert data["architect_lens"] == "Three-tier edge to cloud pipeline"
    assert data["critic_lens"].startswith("The gateway")
    assert data.get("consensus_vote") is None, "A truncated turn has no vote"
    print("[SUCCESS] Truncated-JSON Recovery Test Passed!")

def test_deliverable_unwrapping():
    wrapped = json.dumps({"consensus_document": "# Title\n\n## 1. Executive Summary\nBody text."})
    out = unwrap_markdown_deliverable(wrapped)
    assert out.startswith("# Title"), out[:60]
    assert "\n" in out

    fenced = "```markdown\n# Fenced Title\n\nBody.\n```"
    assert unwrap_markdown_deliverable(fenced).startswith("# Fenced Title")

    escaped = '{"final_report": "# Escaped\\n\\n## Section\\nBody."}'
    out3 = unwrap_markdown_deliverable(escaped)
    assert out3.startswith("# Escaped") and "\n## Section" in out3
    print("[SUCCESS] Deliverable Unwrapping Test Passed!")

def test_citation_sanitizer():
    report = (
        "# Deliverable\n\nWe use LoRa per [Paper 3] and pricing per [Fact-Check 1].\n"
        "See also arXiv:2204.08912 and [Source 8].\n"
        "This [normal bracket] and this [link](https://example.com) must survive.\n"
    )

    cleaned_empty, removed_empty = sanitize_hallucinated_citations(report, None)
    assert removed_empty >= 4, f"expected >=4 removals with no ledger, got {removed_empty}"
    assert "[Paper 3]" not in cleaned_empty
    assert "arXiv:2204.08912" not in cleaned_empty
    assert "[normal bracket]" in cleaned_empty, "Non-citation brackets must be untouched"
    assert "[link](https://example.com)" in cleaned_empty, "Markdown links must be untouched"
    assert "Citation integrity notice" in cleaned_empty

    dossier = PooledResearchDossier(
        stage_1_fact_checks=[ResearchDossierItem(tag="Fact-Check 1", title="Price list")],
        stage_2_academic_papers=[ResearchDossierItem(tag="Paper 3", title="LoRa in dust")],
    )
    cleaned, removed = sanitize_hallucinated_citations(report, dossier)
    assert "[Paper 3]" in cleaned, "A real ledger tag must survive"
    assert "[Fact-Check 1]" in cleaned
    assert "[Source 8]" not in cleaned, "A tag absent from the ledger must be stripped"
    assert removed >= 1
    print("[SUCCESS] Citation Sanitizer Test Passed!")

def test_prompt_contract_survives_truncation():
    contract = build_schema_guide("hybrid_cyberphysical")
    assembled = "HEADER\n" + ("evidence body. " * 20000) + "\n\n" + contract
    fitted = DebateOrchestrator._fit_debater_prompt(assembled, contract, 40000)
    assert len(fitted) <= 40000 + len(contract) + 500
    assert fitted.rstrip().endswith(contract.rstrip()), "The output contract must always survive at the tail"
    assert fitted.startswith("HEADER"), "The role/task header must survive at the head"
    assert "truncated" in fitted

    short = "HEADER\nbody\n\n" + contract
    assert DebateOrchestrator._fit_debater_prompt(short, contract, 40000).rstrip().endswith(contract.rstrip())
    print("[SUCCESS] Contract-Survives-Truncation Test Passed!")

def test_fit_prompt_keeps_head_and_tail():
    body = "A" * 5000 + "MIDDLE" + "Z" * 5000
    out = fit_prompt(body, 4000)
    assert out.startswith("A")
    assert out.rstrip().endswith("Z")
    assert "MIDDLE" not in out
    assert fit_prompt("short", 4000) == "short"
    print("[SUCCESS] Middle-Truncation Test Passed!")

def test_domain_classifier():
    assert classify_problem_domain(
        "Build a web portal with a dashboard and an NLP chatbot for e-governance document search"
    ) == "software_cloud"
    assert classify_problem_domain(
        "Design a solar powered LoRa sensor node with an ESP32 microcontroller and battery for field telemetry"
    ) == "hardware_iot"
    assert classify_problem_domain(
        "IoT sensor network feeding a cloud analytics dashboard with a mobile app and machine learning model"
    ) == "hybrid_cyberphysical"
    assert classify_problem_domain("") == "hybrid_cyberphysical"

    # D5: a pure-software problem must not be asked for battery curves and ambient-heat
    # derating, and a hardware problem must still be asked for them.
    from app.engine.prompts import build_system_prompt_for_debater
    sw = build_system_prompt_for_debater("M", "MeitY", "software_cloud")
    hw = build_system_prompt_for_debater("M", "MoRTH", "hardware_iot")
    assert "SOFTWARE / CLOUD / AI" in sw and "Do NOT introduce microcontrollers" in sw
    assert "HARDWARE / IoT / EMBEDDED" in hw

    sw_guide = build_schema_guide("software_cloud")
    hw_guide = build_schema_guide("hardware_iot")
    assert "45C" in hw_guide, "hardware turns must still demand real field operating limits"
    assert "45C" not in sw_guide, "software turns must not be forced to invent ambient-heat specs"
    assert "Bill of Materials" in hw_guide and "Bill of Materials" not in sw_guide
    print("[SUCCESS] Domain Classifier Test Passed!")

def test_no_anchored_example_numbers():
    """
    P3: literal example values (`"agreement_percentage": 75`) acted as anchors and the
    debaters clustered on them. Every example value must be an instruction placeholder.
    """
    guide = build_schema_guide("hybrid_cyberphysical")
    for anchor in ('"agreement_percentage": 75', '"agreement_percentage": 80', '"agreement_percentage": 85',
                   '"agreement_percentage": 95', '"agreement_percentage": 65'):
        assert anchor not in guide, f"Anchored example value still present: {anchor}"
    assert "<integer 0-100" in guide
    print("[SUCCESS] No-Anchored-Numbers Test Passed!")

def test_probe_failure_classification():
    """
    Every message below is a real body captured from the live fleet during a catalogue sweep.
    The aggregator routers do not use HTTP status codes the way the spec suggests - XKiro and
    TokenRouter both answer "you need credits / a paid plan" with 403 - so reading the status
    code alone marked valid keys as rejected. That misclassification fed the provider-wide auth
    short-circuit, which then abandoned the rest of the catalogue including the free models that
    do work. This test pins the body-first ordering that fixes it.
    """
    cases = [
        # 403 that is really a plan wall, not a bad key.
        ("plan", 'HTTP 403 on x-ai/grok-4.6: {"error": {"message": "This is a paid model. The Free plan '
                 'only allows free models - top up your wallet or subscribe to a plan to use it."}}'),
        ("plan", 'HTTP 403 on anthropic/claude-opus-5: {"error": {"message": "This premium model requires '
                 'an active paid plan or real deposited balance."}}'),
        # 403 that is really an empty wallet.
        ("billing", 'HTTP 403 on openai/gpt-5.4-nano: {"error": {"message": "User\'s credit limit is '
                    'insufficient, remaining credit limit: 0.000000"}}'),
        ("billing", 'Balance Depleted (HTTP 402) on myt/gpt-5: {"error": {"message": "Saldo tidak cukup '
                    'untuk memproses request ini.", "type": "insufficient_balance"}}'),
        ("billing", 'Balance Depleted (HTTP 402) on z-ai/glm-5.3: {"error": {"message": "Insufficient '
                    'credits. This account never purchased credits."}}'),
        # Genuinely rejected credentials - the only class allowed to kill a provider.
        ("auth", 'HTTP 401 on gpt-5.6-sol: {"error":{"message":"unauthorized client detected"}}'),
        ("auth", 'HTTP 401 on x: {"error":{"message":"Invalid token (request id: 2026)"}}'),
        # Account-level day allowance, distinct from momentary throttling.
        ("quota", 'Rate Limited (HTTP 429) on dots-3:free: {"error": {"message": "Rate limit exceeded: '
                  'free-models-per-day. Add 10 credits to unlock 1000 free model requests per day"}}'),
        ("rate_limited", 'Rate Limited (HTTP 429) on gpt-4o: '),
        ("policy", 'HTTP 404 on meta/muse-spark: {"error": {"message": "No endpoints available matching '
                   'your guardrail restrictions and data policy."}}'),
        ("missing", 'HTTP 404 on models/gemini-2.5-pro: [{"error": {"code": 404, "message": "This model '
                    'models/gemini-2.5-pro is no longer available to new users."}}]'),
        ("unsupported", 'HTTP 400 on models/gemini-2.5-flash-preview-tts: [{"error": {"code": 400, '
                        '"message": "The requested combination of response modalities (TEXT) is not '
                        'supported by the model."}}]'),
        ("server", 'HTTP 502 on deepseek-v4-pro: {"error": {"message": "openai_error"}}'),
        ("timeout", 'All 1 key/model attempt(s) failed. ReadTimeout: '),
        ("empty", 'All 1 key/model attempt(s) failed. Empty token content returned by model'),
    ]
    for expected, message in cases:
        got = classify_probe_failure(message)
        assert got == expected, f"expected {expected}, got {got} for: {message[:90]}"

    # Only a credential rejection may trip the provider-wide kill switch.
    assert AUTH_SHORTCIRCUIT_REASONS == {"auth"}
    for benign in ("plan", "billing", "missing", "unsupported", "policy"):
        assert benign not in AUTH_SHORTCIRCUIT_REASONS, \
            f"'{benign}' must not abandon a provider - its key is fine"
    print("[SUCCESS] Probe Failure Classification Test Passed!")

def test_model_tier_classification():
    """
    Every id below is real, taken from the live catalogue sweep. The wizard shows ~90 verified
    models and nobody can pick from 90 raw names, so each row is pre-tiered by model family.
    The trap this pins: `nvidia/llama-3.1-nemoguard-8b-content-safety` contains the flagship
    token `llama-3.1`, and a naive substring match tiered a safety classifier as a frontier
    debater. Special-purpose is therefore tested before family strength.
    """
    cases = [
        # Frontier debaters.
        ("top", "anthropic/claude-opus-5"),
        ("top", "claude-opus-4-8"),
        ("top", "openai/gpt-5.6-sol"),
        ("top", "deepseek/deepseek-v4-pro"),
        ("top", "qwen/qwen3.8-max-free"),
        ("top", "mistralai/mistral-large-2512"),
        ("top", "minimax/minimax-m2.7"),
        ("top", "stealth/ox-alpha"),
        ("top", "x-ai/grok-4.6"),
        ("top", "gemini-3.5-pro"),
        # Sheer parameter count is a family-independent flagship signal. The quick sweep found
        # nemotron-3-ultra sitting in "mid" beside 27b models because no family token matched it.
        # The MoE active count (`a55b`, `a17b`) must not be what gets read.
        ("top", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        ("top", "qwen/qwen3.5-397b-a17b:free"),
        ("top", "meta-llama/llama-3.1-405b-instruct"),
        # Flagship family, small variant -> mid, not top. A small variant of a merely
        # strong family (gpt-5.4) drops all the way to low - it is not a debater.
        ("mid", "openai/gpt-5.6-nano"),
        ("low", "gpt-5.4-nano"),
        # Solid general chat models.
        ("mid", "unlimited/claude-sonnet-5"),
        ("mid", "gemini-3.7-flash"),
        ("mid", "openai/gpt-oss-120b"),
        ("mid", "nvidia/nemotron-3-super-120b-a12b:free"),
        ("mid", "meta/llama-3.3-70b-instruct"),
        # Small variants and special-purpose endpoints.
        ("low", "gemini-3.5-flash-lite"),
        ("low", "gemini-flash-lite-latest"),
        ("low", "nvidia/nemotron-mini-4b-instruct"),
        ("low", "meta/llama-3.1-8b-instruct"),
        ("low", "google/gemma-4-26b"),
        ("low", "anthropic/claude-haiku-4-5"),
        # Not debaters at any size - the naive-substring trap.
        ("low", "nvidia/llama-3.1-nemoguard-8b-content-safety"),
        ("low", "nvidia/llama-3.1-nemoguard-8b-topic-control"),
        ("low", "nvidia/riva-translate-4b-instruct-v1.1"),
        ("low", "models/gemini-2.5-flash-preview-tts"),
        ("low", "lyria-3-pro-preview"),
        ("low", "google/diffusiongemma-26b-a4b-it"),
    ]
    for expected, model_id in cases:
        got = classify_model_tier(model_id)
        assert got == expected, f"expected {expected}, got {got} for {model_id}"

    # An unrecognised name must land in mid: guessing "top" flatters it and "low" buries it.
    assert classify_model_tier("some-vendor/unheard-of-model-v3") == "mid"
    # The display name is consulted too, since some routers expose only an opaque id.
    assert classify_model_tier("router-internal-42", "Claude Opus 5 (Unlimited)") == "top"
    print("[SUCCESS] Model Tier Classification Test Passed!")

if __name__ == "__main__":
    test_json_repair()
    test_url_normalization()
    test_no_vote_is_ever_fabricated()
    test_explicit_prose_vote_is_recovered()
    test_scratchpad_outside_json()
    test_truncated_json_is_recovered()
    test_deliverable_unwrapping()
    test_citation_sanitizer()
    test_prompt_contract_survives_truncation()
    test_fit_prompt_keeps_head_and_tail()
    test_domain_classifier()
    test_no_anchored_example_numbers()
    test_probe_failure_classification()
    test_model_tier_classification()
    print("[ALL PASSED] All Backend Unit Tests Passed Successfully!")
