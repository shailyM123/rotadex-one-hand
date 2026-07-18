import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
downloaded_threejs = os.path.join(base_dir, "cad", "three.min.js")
viewer_path = os.path.join(base_dir, "view_stl_model.html")

print("Reading Three.js code from:", downloaded_threejs)
with open(downloaded_threejs, "r", encoding="utf-8") as f:
    threejs_code = f.read()

# Strip markdown metadata header
if "---" in threejs_code:
    threejs_code = threejs_code.split("---", 1)[1].strip()

# Verify it starts with standard minified js and not HTML/error
if "<!DOCTYPE" in threejs_code[:100] or "html" in threejs_code[:100].lower():
    print("Warning: The downloaded file looks like HTML/error rather than JS. Let's inspect it:")
    print(threejs_code[:200])
    exit(1)

print("Reading viewer HTML from:", viewer_path)
with open(viewer_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace the external CDN script tag with inline script
old_tag = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
new_tag = f'<script>\n{threejs_code}\n</script>'

if old_tag in html_content:
    html_content = html_content.replace(old_tag, new_tag)
    print("Successfully embedded Three.js offline!")
else:
    print("Warning: CDN tag not found. Let's check if it was already replaced.")

with open(viewer_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Saved viewer with offline support.")
