import subprocess
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any


class URLPerformanceTester:
    """
    Minimal wrapper around Lighthouse that:
    - Runs the exact Lighthouse CLI specified by the user
    - Saves the raw HTML report(s) (JSON generation is invoked by Lighthouse but not used)
    - Returns paths and contents so the UI can render and download the exact report(s)
    """
    
    def __init__(self):
        # Use the exact output directory requested
        self.output_dir = "/Users/ravi/Desktop/pdf"
        os.makedirs(self.output_dir, exist_ok=True)
        self.temp_items: List[str] = []
    
    def _check_lighthouse_installed(self) -> bool:
        try:
            subprocess.run(["lighthouse", "--version"], capture_output=True, check=True)
            return True
        except Exception:
            return False
    
    def _run_lighthouse_exact(self, url: str, index: int) -> Dict[str, Any]:
        """Run Lighthouse with the exact flags provided and return file paths for HTML/JSON outputs."""
        base_path = os.path.join(self.output_dir, f"report-{index}")
        cmd = [
            "lighthouse",
            url,
            "--output", "html",
            "--output", "json",
            # Use prefix (no extension) so LH writes both .html and .json with same base
            "--output-path", f"{base_path}",
            "--chrome-flags=--headless",
            "--preset=desktop",
        ]
        subprocess.run(cmd, check=True)
        # Robustly resolve the HTML file LH created
        candidates = [
            f"{base_path}.html",
            f"{base_path}.report.html",
            f"{base_path}.json.html",
        ]
        html_path = None
        for p in candidates:
            if os.path.isfile(p):
                html_path = p
                break
        # Fallback: scan directory for any .html starting with base name
        if not html_path:
            directory = os.path.dirname(base_path)
            prefix = os.path.basename(base_path)
            for name in os.listdir(directory):
                if name.startswith(prefix) and name.endswith('.html'):
                    html_path = os.path.join(directory, name)
                    break
        json_path = f"{base_path}.json"
        self.temp_items.extend([html_path, json_path])
        html_content = ""
        try:
            if html_path and os.path.isfile(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
        except Exception:
            html_content = ""
        return {
            "url": url,
            "html_path": html_path,
            "json_path": json_path,
            "html_content": html_content,
        }
    
    def _parse_multiple_urls(self, urls_text: str) -> List[str]:
        # Accepts input like: "url1", "url2" OR comma-separated without quotes
        text = (urls_text or "").strip()
        if not text:
            return []
        # Remove surrounding whitespace/quotes and split by comma
        parts = [p.strip().strip('"').strip("'") for p in text.split(',')]
        urls = [p for p in parts if p]
        # Ensure protocol
        normalized = [u if u.startswith("http://") or u.startswith("https://") else f"https://{u}" for u in urls]
        return normalized
    
    def test_single_url(self, url: str) -> Dict[str, Any]:
        if not self._check_lighthouse_installed():
            raise Exception("Lighthouse is not installed. Install with: npm install -g lighthouse")
        if not url or not isinstance(url, str):
            raise Exception("Invalid URL")
        try:
            result = self._run_lighthouse_exact(url, 1)
            return result
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error running Lighthouse for {url}: {e}")
    
    def test_multiple_urls(self, urls_text: str) -> List[Dict[str, Any]]:
        if not self._check_lighthouse_installed():
            raise Exception("Lighthouse is not installed. Install with: npm install -g lighthouse")
        urls = self._parse_multiple_urls(urls_text)
        if not urls:
            raise Exception("No valid URLs provided")
        results: List[Dict[str, Any]] = []
        for idx, url in enumerate(urls, start=1):
            try:
                results.append(self._run_lighthouse_exact(url, idx))
            except subprocess.CalledProcessError as e:
                results.append({
                    "url": url,
                    "error": str(e),
                    "html_path": None,
                    "json_path": None,
                    "html_content": "",
                })
        return results
    
    def get_summary_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Keep a minimal summary for UI; we are not computing metrics now
        return {
            "total_urls_tested": len(results or []),
            "urls_with_issues": sum(1 for r in (results or []) if r.get("error")),
        }
    
    def generate_html_report(self, results: List[Dict[str, Any]], test_mode: str) -> str:
        # Return the exact Lighthouse HTML report for single URL.
        # For multiple URLs, return a simple pagination wrapper embedding each exact report.
        if not results:
            return ""
        if test_mode == "single":
            return results[0].get("html_content", "")
        # Multiple: render each exact report in its own iframe using srcdoc
        def esc_srcdoc(s: str) -> str:
            return (
                (s or "")
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
        frames = []
        buttons = []
        for i, r in enumerate(results, start=1):
            src = esc_srcdoc(r.get("html_content", "") or f"<div style='padding:1rem;color:#f55'>No report for {r.get('url','')}</div>")
            display = 'block' if i == 1 else 'none'
            frames.append(f"<iframe id='f{i}' style='display:{display};width:100%;height:1800px;border:0' srcdoc=\"{src}\"></iframe>")
            buttons.append(f"<button onclick=\"showF({i})\">Report {i}</button>")
        html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Lighthouse Reports</title>
  <style>
    body {{ margin:0; background:#0e1117; color:#eee; }}
    .nav {{ position:sticky; top:0; background:#111; padding:10px; z-index:10 }}
    .nav button {{ background:#333; color:#fff; border:1px solid #6C47E5; padding:6px 10px; cursor:pointer; margin-right:6px; }}
    .nav button:hover {{ background:#6C47E5; }}
  </style>
  <script>
    function showF(i) {{
      var idx = 1;
      while (true) {{
        var el = document.getElementById('f'+idx);
        if (!el) break;
        el.style.display = (idx===i)?'block':'none';
        idx++;
      }}
      window.scrollTo(0,0);
    }}
  </script>
 </head>
 <body>
   <div class=\"nav\">{''.join(buttons)}</div>
   {''.join(frames)}
 </body>
 </html>
"""
        return html
    
    def cleanup(self):
        # Do not delete user's output_dir; only clear temp items we created if any leftover dirs exist
        for p in self.temp_items:
            try:
                if p and os.path.isfile(p):
                    os.remove(p)
            except Exception:
                pass
