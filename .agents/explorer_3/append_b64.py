import sys, base64

if len(sys.argv) < 3:
    print('Usage: python append_b64.py <filepath> <b64_content>')
    sys.exit(1)

filepath = sys.argv[1]
b64_content = sys.argv[2]
text = base64.b64decode(b64_content.encode('ascii')).decode('utf-8')

with open(filepath, 'a', encoding='utf-8') as f:
    f.write(text)

print(f'Successfully appended {len(text)} chars to {filepath}')
