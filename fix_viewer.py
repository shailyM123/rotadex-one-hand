import json, os, re

# Read STL files
stl_dir = 'cad/stl_models'
stl_data = {}
for fn in os.listdir(stl_dir):
    if fn.endswith('.stl') and not fn.startswith('rotadex_full'):
        with open(os.path.join(stl_dir, fn), 'r') as f:
            stl_data[fn] = f.read()

print(f"Loaded {len(stl_data)} STL files")

# Read current view_stl_model.html
with open('view_stl_model.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the STL_DATA JSON blob - replace with properly escaped JSON
match = re.search(r'const STL_DATA = (\{.*?\});', html, re.DOTALL)
if match:
    new_json = json.dumps(stl_data)
    html = html[:match.start(1)] + new_json + html[match.end(1):]
    print("Replaced STL_DATA JSON blob")
else:
    print("ERROR: STL_DATA not found!")
    exit(1)

# Verify the split call uses the correct escape
# In JS source code, split('\n') means split on newline character
# json.dumps produces \\n in the JSON string which JS interprets as newline
# The split call needs to match: split('\n') in JS source = split on newline char
# Check current state
if "split('\\\\n')" in html:
    print("Found double-escaped split, fixing...")
    html = html.replace("split('\\\\n')", "split('\\n')")
elif 'split("\\\\n")' in html:
    print("Found double-escaped split (double quotes), fixing...")
    html = html.replace('split("\\\\n")', 'split("\\n")')
else:
    print("split escape looks OK")

# Write fixed files
with open('view_stl_model.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done! File size: {len(html)} bytes")
