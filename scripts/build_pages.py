"""Build script to bundle the Streamlit app into a standalone serverless WebAssembly static site (stlite) for GitHub Pages."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Files to embed into the stlite virtual file system
TARGET_FILES = [
    "app.py",
    "src/__init__.py",
    "src/channel.py",
    "src/demodulation.py",
    "src/encoding.py",
    "src/metrics.py",
    "src/modulation.py",
    "src/visualization.py",
]

file_map = {}
for rel_path in TARGET_FILES:
    full_path = ROOT / rel_path
    if full_path.exists():
        file_map[rel_path] = full_path.read_text(encoding="utf-8")
    else:
        print(f"Warning: {rel_path} not found")

files_json = json.dumps(file_map)

HTML_TEMPLATE = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
  <title>Wireless Digital Signal Modulation and Transmission Simulator</title>
  <meta name="description" content="Software-based wireless digital communication simulator running entirely client-side via WebAssembly." />
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📡</text></svg>" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/browser@1.11.0/build/stlite.css" />
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #090d16;
      color: #f3f4f6;
    }}
  </style>
</head>
<body>
  <div id="root"></div>

  <script type="module">
    import {{ mount }} from "https://cdn.jsdelivr.net/npm/@stlite/browser@1.11.0/build/stlite.js";

    const files = {files_json};

    mount(
      {{
        requirements: ["numpy", "scipy", "matplotlib"],
        entrypoint: "app.py",
        files: files,
      }},
      document.getElementById("root")
    );
  </script>
</body>
</html>
"""

output_path = ROOT / "index.html"
output_path.write_text(HTML_TEMPLATE, encoding="utf-8")
print(f"Successfully generated {output_path} ({len(HTML_TEMPLATE)} bytes)")
