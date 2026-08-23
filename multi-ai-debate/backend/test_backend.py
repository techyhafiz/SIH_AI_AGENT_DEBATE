import asyncio
import json
from app.schemas import ModelConfig, StructuredDebateTurn
from app.providers.universal_client import extract_and_repair_json, parse_structured_turn, UniversalAIClient

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
    assert len(structured.positives_of_approach) == 2
    print("[SUCCESS] JSON Extraction & Repair Test Passed!")

def test_url_normalization():
    assert UniversalAIClient._normalize_chat_url("https://openrouter.ai/api/v1") == "https://openrouter.ai/api/v1/chat/completions"
    assert UniversalAIClient._normalize_chat_url("http://localhost:11434/v1/") == "http://localhost:11434/v1/chat/completions"
    assert UniversalAIClient._normalize_chat_url("https://api.openai.com") == "https://api.openai.com/v1/chat/completions"
    assert UniversalAIClient._normalize_chat_url("https://api.groq.com/openai/v1/chat/completions") == "https://api.groq.com/openai/v1/chat/completions"
    print("[SUCCESS] URL Normalization Test Passed!")

if __name__ == "__main__":
    test_json_repair()
    test_url_normalization()
    print("[ALL PASSED] All Backend Unit Tests Passed Successfully!")
