import os
import re

target = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

with open(target, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print(f"Total lines in handbook: {len(lines)}")

# 1. Check for Placeholder Words
placeholders = ["TODO", "TBD", "FIXME", "XXX", "LOREM IPSUM", "INSERT HERE", "YOUR_CODE_HERE", "PLACEHOLDER", "FOOBAR"]
print("\n=== CHECK 1: PLACEHOLDER KEYWORDS ===")
found_placeholders = 0
for i, line in enumerate(lines, 1):
    for p in placeholders:
        if p in line.upper():
            # filter out legitimate mentions (like explaining what not to do)
            print(f"Line {i} [{p}]: {line.strip()}")
            found_placeholders += 1

print(f"Total placeholder matches: {found_placeholders}")

# 2. Check for ellipsis inside code blocks indicating incomplete code snippets
print("\n=== CHECK 2: CODE BLOCKS & ELLIPSIS IN CODE ===")
in_code_block = False
code_block_lang = ""
code_block_start = 0
current_block_lines = []
code_blocks = []

for i, line in enumerate(lines, 1):
    if line.strip().startswith("```"):
        if not in_code_block:
            in_code_block = True
            code_block_lang = line.strip()[3:].strip()
            code_block_start = i
            current_block_lines = []
        else:
            in_code_block = False
            code_blocks.append((code_block_lang, code_block_start, i, current_block_lines))
    elif in_code_block:
        current_block_lines.append((i, line))

print(f"Total code blocks found: {len(code_blocks)}")
for lang, start, end, blines in code_blocks:
    print(f"  Block lines {start}-{end} (lang: '{lang}', count: {len(blines)} lines)")
    for lno, bline in blines:
        # Check for standalone '...' or '…' or '// etc' or '# etc'
        if re.search(r"^\s*(\.\.\.|…|//\s*etc|#\s*etc|/\*\s*etc\s*\*/)\s*$", bline):
            print(f"    WARNING: Suspicious ellipsis on line {lno}: {bline.strip()}")

# 3. Check for Markdown formatting issues (e.g. unclosed code blocks, broken tables)
print("\n=== CHECK 3: STRUCTURAL INTEGRITY ===")
if in_code_block:
    print(f"ERROR: Unclosed code block starting at line {code_block_start}")
else:
    print("Code block tags are balanced (all closed properly).")

# 4. Check Table consistency
table_lines = 0
table_errors = 0
for i, line in enumerate(lines, 1):
    if line.strip().startswith("|") and line.strip().endswith("|"):
        # Check pipe count consistency for headers vs rows if applicable
        pass

print("Structural scan complete.")
