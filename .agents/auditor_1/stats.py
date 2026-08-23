import os
import re

target = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

with open(target, "r", encoding="utf-8") as f:
    text = f.read()

lines = text.splitlines()
words = text.split()

print("=== STATISTICAL SUMMARY ===")
print(f"Total Lines: {len(lines)}")
print(f"Total Words: {len(words)}")
print(f"File Size: {len(text.encode('utf-8'))} bytes")

headers_h1 = len(re.findall(r"^#\s+.*", text, re.MULTILINE))
headers_h2 = len(re.findall(r"^##\s+.*", text, re.MULTILINE))
headers_h3 = len(re.findall(r"^###\s+.*", text, re.MULTILINE))
headers_h4 = len(re.findall(r"^####\s+.*", text, re.MULTILINE))
tables = len(re.findall(r"^\|.*?\|.*?\|", text, re.MULTILINE))
code_blocks = len(re.findall(r"^```", text, re.MULTILINE)) // 2

print(f"H1 Sections: {headers_h1}")
print(f"H2 Sections: {headers_h2}")
print(f"H3 Subsections: {headers_h3}")
print(f"H4 Subsections: {headers_h4}")
print(f"Markdown Tables (rows): {tables}")
print(f"Code / ASCII Diagram Blocks: {code_blocks}")

