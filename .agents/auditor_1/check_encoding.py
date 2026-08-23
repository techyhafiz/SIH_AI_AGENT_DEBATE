target = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

with open(target, "rb") as f:
    raw = f.read()

try:
    decoded = raw.decode("utf-8")
    print(f"Decoded UTF-8 successfully. Total length: {len(decoded)} chars.")
    # Check for replacement character U+FFFD
    fffd_count = decoded.count("\ufffd")
    print(f"Count of U+FFFD (replacement chars): {fffd_count}")
    if fffd_count > 0:
        lines = decoded.splitlines()
        for idx, l in enumerate(lines, 1):
            if "\ufffd" in l:
                print(f"Line {idx}: {l}")
except Exception as e:
    print(f"UTF-8 Decode error: {e}")
