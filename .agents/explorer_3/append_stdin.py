import sys

if len(sys.argv) < 2:
    sys.exit(1)

target = sys.argv[1]
content = sys.stdin.read()

with open(target, 'a', encoding='utf-8') as f:
    f.write(content)

print(f'Wrote {len(content)} chars to {target}')
