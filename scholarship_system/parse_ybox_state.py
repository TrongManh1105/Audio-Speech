import requests
from bs4 import BeautifulSoup
import json
import re

r = requests.get("https://ybox.vn/hoc-bong")
soup = BeautifulSoup(r.text, "html.parser")

initial_state = None
for s in soup.find_all("script"):
    if s.string and "window.__INITIAL_STATE__" in s.string:
        match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});", s.string, re.DOTALL)
        if match:
            try:
                initial_state = json.loads(match.group(1))
            except Exception as e:
                # In case trailing semicolon or something
                raw = match.group(1)
                print("Regex match found, length:", len(raw))
                # Let's save to a file to inspect
                with open("ybox_state_raw.json", "w", encoding="utf-8") as f:
                    f.write(raw)
                print("Saved raw state to ybox_state_raw.json")
        break

if initial_state:
    print("Keys in initial_state:", list(initial_state.keys()))
    for k, v in initial_state.items():
        if isinstance(v, dict):
            print(f"  {k} keys:", list(v.keys()))
