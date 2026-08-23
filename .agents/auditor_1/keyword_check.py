target = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

with open(target, "r", encoding="utf-8") as f:
    text = f.read()

keywords = [
    "Ministry Curveball",
    "Anti-Tokenism",
    "90-Minute Rotational Sleep",
    "1080p OBS",
    "C4 Level 2",
    "DFD Level 1",
    "docker-compose",
    "apiClient.ts",
    "seed.ts",
    "inference_service.py",
    "DPDP Act 2023",
    "Bhashini",
    "NIDHI-PRAYAS",
    "AICTE",
    "Nodal Center"
]

print("=== KEYWORD DEPTH & OCCURRENCE CHECK ===")
for kw in keywords:
    count = text.count(kw)
    print(f"Keyword '{kw}': {count} occurrences")

