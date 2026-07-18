import os

# Read current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add global onerror handler to display errors on screen
error_handler = """
window.onerror = function(message, source, lineno, colno, error) {
  var overlay = document.getElementById('overlay');
  if (overlay) {
    overlay.innerHTML = '<div style="text-align:center;padding:30px;color:#f87171;font-family:sans-serif;">' +
      '<h2 style="margin-bottom:15px;font-size:20px;">Application Error</h2>' +
      '<p style="margin-bottom:10px;font-size:14px;color:#e2e8f0;">' + message + '</p>' +
      '<p style="font-size:12px;color:#94a3b8;">Line ' + lineno + ' · Column ' + colno + '</p>' +
      '</div>';
    overlay.classList.remove('hide');
    overlay.style.opacity = 1;
    overlay.style.pointerEvents = 'auto';
  }
  return false;
};
"""

# Find first <script> tag and inject after it
script_tag = "<script>"
idx = html.find(script_tag)
if idx >= 0:
    insert_pos = idx + len(script_tag)
    html = html[:insert_pos] + error_handler + html[insert_pos:]
    print("Injected global error handler successfully!")

# 2. Replace implicit globals with safe window. references
html = html.replace("innerWidth", "window.innerWidth")
html = html.replace("innerHeight", "window.innerHeight")
html = html.replace("devicePixelRatio", "window.devicePixelRatio")
print("Replaced global variables with window. references")

# Write out the updated index.html and view_stl_model.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('view_stl_model.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done making viewer robust!")
