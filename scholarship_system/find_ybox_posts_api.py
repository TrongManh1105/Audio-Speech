import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

r_js = requests.get("https://ybox.vn/public/app.8f5b115ae553b83e3857.js?a", headers=headers, timeout=10)
matches = re.findall(r"api/v1/[a-zA-Z0-9_\-\/]+", r_js.text)
print("Unique api/v1 paths found in Ybox JS bundle:", set(matches[:30]))

# Check if there is an article or post endpoint
for m in set(matches):
    if "post" in m or "article" in m or "category" in m or "scholarship" in m:
        print("-> Candidate:", m)
