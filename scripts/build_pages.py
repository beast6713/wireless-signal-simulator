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
    #loading-overlay {{
      position: fixed;
      inset: 0;
      background: #090d16;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 99999;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      transition: opacity 0.5s ease;
    }}
    .spinner {{
      width: 50px;
      height: 50px;
      border: 3px solid rgba(56, 189, 248, 0.2);
      border-radius: 50%;
      border-top-color: #38bdf8;
      animation: spin 1s ease-in-out infinite;
      margin-bottom: 20px;
    }}
    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}
    .loading-title {{
      font-size: 1.25rem;
      font-weight: 700;
      color: #f1f5f9;
      margin-bottom: 8px;
    }}
    .loading-sub {{
      font-size: 0.85rem;
      color: #94a3b8;
    }}
  </style>
</head>
<body>
  <div id="loading-overlay">
    <div class="spinner"></div>
    <div class="loading-title">📡 Initializing Wireless Simulator...</div>
    <div class="loading-sub">Loading WebAssembly Python Runtime (Pyodide, NumPy, SciPy, Matplotlib)</div>
  </div>
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
    ).then(() => {{
      const loader = document.getElementById("loading-overlay");
      if (loader) {{
        loader.style.opacity = "0";
        setTimeout(() => loader.remove(), 500);
      }}
    }}).catch((err) => {{
      const loader = document.getElementById("loading-overlay");
      if (loader) {{
        loader.innerHTML = `
          <div style="color: #f87171; font-size: 1.2rem; font-weight: bold; margin-bottom: 8px;">Initialization Failed</div>
          <div style="color: #94a3b8; font-size: 0.9rem; max-width: 500px; text-align: center;">${{err}}</div>
        `;
      }}
    }});
  </script>
</body>
</html>
"""

output_path = ROOT / "index.html"
output_path.write_text(HTML_TEMPLATE, encoding="utf-8")
print(f"Successfully generated {output_path} ({len(HTML_TEMPLATE)} bytes)")
