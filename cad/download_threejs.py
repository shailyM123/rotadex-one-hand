import urllib.request
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
threejs_local_path = os.path.join(base_dir, "cad", "three.min.js")
viewer_path = os.path.join(base_dir, "view_stl_model.html")

url = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"

print(f"Downloading Three.js from: {url}")
try:
    with urllib.request.urlopen(url) as response:
        js_code = response.read().decode('utf-8')
    print(f"Successfully downloaded Three.js! Length: {len(js_code)} characters")
    
    with open(threejs_local_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print(f"Saved locally to: {threejs_local_path}")
    
    # Read the viewer html
    print("Reading viewer HTML...")
    with open(viewer_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Find the script block for Three.js
    # In view_stl_model.html, the first script block starts right after the tip text and contains the Three.js library.
    # Let's search for the first <script>...</script> block.
    import re
    # We find the first script tag and replace its contents
    # Since Three.js is minified and very long, we can do a target replacement.
    # To be extremely safe, let's write a fresh template and replace __THREE_JS_PLACEHOLDER__!
    
except Exception as e:
    print("Error:", e)
