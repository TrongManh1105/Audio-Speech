import json
import csv
import os
import sys
import random

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Đọc file crawled_specific_scholars4dev.json
with open("crawled_specific_scholars4dev.json", "r", encoding="utf-8") as f:
    raw_items = json.load(f)

print(f"Loaded {len(raw_items)} raw crawled items.")
