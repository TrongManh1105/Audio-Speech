import requests
from bs4 import BeautifulSoup
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

r = requests.get("https://ybox.vn/hoc-bong", headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

# Find js script urls
scripts = [s.get("src") for s in soup.find_all("script") if s.get("src")]
print(f"Total script tags with src: {len(scripts)}")
for src in scripts[:5]:
    print("Script:", src)

# Try fetching one main bundle to search for api URLs
for src in scripts:
    if "main" in src or "app" in src or "index" in src or "bundle" in src:
        full_src = src if src.startswith("http") else f"https://ybox.vn{src}"
        print(f"Checking bundle: {full_src}")
        r_js = requests.get(full_src, headers=headers, timeout=10)
        # Search for api endpoints
        apis = re.findall(r"https?://[a-zA-Z0-9\.-]+/api/[a-zA-Z0-9_\-\/]+", r_js.text)
        print("Found APIs:", set(apis[:10]))
        apis_relative = re.findall(r'"/api/[a-zA-Z0-9_\-\/]+"', r_js.text)
        print("Found relative APIs:", set(apis_relative[:10]))
        break
