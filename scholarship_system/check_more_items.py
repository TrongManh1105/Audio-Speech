import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

with open("crawled_specific_scholars4dev.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for i in range(25, 40):
    if i < len(data):
        item = data[i]
        print(f"=== {i+1}. {item['title']} ===")
        print("Host:", item['host'][:60])
        print("Deadline:", item['deadline'][:50])
        print("Quota:\n", item['quota'][:150])
        print("-" * 50)
