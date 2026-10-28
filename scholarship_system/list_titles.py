import json
import re

with open("crawled_specific_scholars4dev.json", "r", encoding="utf-8") as f:
    items = json.load(f)

for i, it in enumerate(items):
    print(f"{i+1}. {it['title']} ({it['study_in']})")
