import re
import yaml
import py_compile
import subprocess
import os

target = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

with open(target, "r", encoding="utf-8", errors="replace") as f:
    text = f.read()

# Extract code blocks
blocks = re.findall(r"```(yaml|typescript|python)?\n(.*?)```", text, re.DOTALL)

print(f"Extracted {len(blocks)} code blocks.")

test_dir = r"c:\Users\mujaw\Downloads\SIH\.agents\auditor_1\code_tests"
os.makedirs(test_dir, exist_ok=True)

# 1. Test docker-compose YAML
yaml_blocks = [b[1] for b in blocks if b[0] == "yaml" or "version:" in b[1] or "services:" in b[1]]
print(f"\n--- Testing YAML Blocks ({len(yaml_blocks)}) ---")
for idx, ycontent in enumerate(yaml_blocks):
    ypath = os.path.join(test_dir, f"test_{idx}.yml")
    with open(ypath, "w", encoding="utf-8") as yf:
        yf.write(ycontent)
    try:
        parsed = yaml.safe_load(ycontent)
        print(f"YAML Block {idx}: Successfully parsed. Root keys: {list(parsed.keys()) if isinstance(parsed, dict) else type(parsed)}")
    except Exception as e:
        print(f"YAML Block {idx} ERROR: {e}")

# 2. Test Python code blocks
py_blocks = [b[1] for b in blocks if b[0] == "python" or "from fastapi import" in b[1] or "import uvicorn" in b[1]]
print(f"\n--- Testing Python Blocks ({len(py_blocks)}) ---")
for idx, pycontent in enumerate(py_blocks):
    pypath = os.path.join(test_dir, f"test_{idx}.py")
    with open(pypath, "w", encoding="utf-8") as pyf:
        pyf.write(pycontent)
    try:
        py_compile.compile(pypath, doraise=True)
        print(f"Python Block {idx}: Syntax valid and compiled successfully.")
    except Exception as e:
        print(f"Python Block {idx} Syntax ERROR: {e}")

# 3. Test TypeScript code blocks (syntax check with node or regex analysis)
ts_blocks = [b[1] for b in blocks if b[0] == "typescript" or "export class" in b[1] or "interface " in b[1]]
print(f"\n--- Testing TypeScript Blocks ({len(ts_blocks)}) ---")
for idx, tscontent in enumerate(ts_blocks):
    tspath = os.path.join(test_dir, f"test_{idx}.ts")
    with open(tspath, "w", encoding="utf-8") as tsf:
        tsf.write(tscontent)
    print(f"TypeScript Block {idx}: Saved to {tspath}, lines: {len(tscontent.splitlines())}")

