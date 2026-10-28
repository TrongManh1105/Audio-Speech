import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

r = requests.get("https://ybox.vn/public/app.8f5b115ae553b83e3857.js?a", headers=headers, timeout=10)
# Look for axios or fetch requests with URL
urls = re.findall(r'["\'](/api/v\d+/[^"\']+)["\']', r.text)
print("Axios relative endpoints:", set(urls[:25]))

urls_full = re.findall(r'["\'](https://[^"\']*ybox\.vn/[^"\']+)["\']', r.text)
print("\nFull ybox.vn URLs:", set(urls_full[:25]))

# Look for mentions of "hoc-bong"
hb_mentions = re.findall(r'[^"\';{}]{0,50}hoc-bong[^"\';{}]{0,50}', r.text)
print("\nMentions of hoc-bong:", set(hb_mentions[:10]))
