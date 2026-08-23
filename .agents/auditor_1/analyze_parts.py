import re

target = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

with open(target, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Let's inspect parts and line counts per part
parts = re.split(r"\n# (PART \d+:.*?)\n", content)

print(f"Number of main sections found: {len(parts)}")
for i in range(1, len(parts), 2):
    title = parts[i]
    body = parts[i+1]
    lines = len(body.splitlines())
    words = len(body.split())
    print(f"\n=== {title} ===")
    print(f"Lines: {lines} | Words: {words}")
    
    # Subsections
    subsections = re.findall(r"\n##+ (.*?)\n", body)
    for sub in subsections:
        print(f"  - {sub}")
