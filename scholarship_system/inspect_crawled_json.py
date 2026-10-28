import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

with open("crawled_specific_scholars4dev.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total crawled items: {len(data)}")
for i, item in enumerate(data[:12]):
    print(f"=== {i+1}. {item['title']} ===")
    print("Host:", item['host'])
    print("Country:", item['study_in'])
    print("Deadline:", item['deadline'])
    print("Quota:\n", item['quota'])
    print("-" * 50)
