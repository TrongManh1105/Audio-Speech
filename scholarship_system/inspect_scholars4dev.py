import csv
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

with open("data/scholars4dev.csv", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print("Headers:", reader.fieldnames)
    for i, row in enumerate(reader):
        if i < 5:
            print(f"=== Row {i+1} ===")
            print("Tên:", row.get("Tên học bổng"))
            print("Trường:", row.get("Trường / Cơ sở đào tạo"))
            print("Số lượng suất:", row.get("Số lượng suất học bổng"))
            print("Hạn nộp:", row.get("Hạn nộp"))
            print("Ngành:", row.get("Ngành học áp dụng"))
            print("Link:", row.get("Link bài viết trên Scholars4dev"))
            print()
        if i == 5:
            break
