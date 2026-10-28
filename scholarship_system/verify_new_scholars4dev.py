import csv
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

file_path = "data/scholars4dev.csv"

with open(file_path, mode="r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    print("Columns:", reader.fieldnames)
    print(f"Total columns: {len(reader.fieldnames)}")
    
    rows = []
    for i, row in enumerate(reader):
        if i < 8:
            rows.append(row)
        total_count = i + 1

print(f"Total rows in CSV: {total_count}")
print("\n" + "="*80)
for idx, r in enumerate(rows, start=1):
    print(f"--- DÒNG {idx} ---")
    print("Tên:", r["Tên học bổng"])
    print("Trường:", r["Trường / Cơ sở đào tạo"])
    print("Ngành:", r["Ngành học áp dụng"])
    print("Số lượng suất:", r["Số lượng suất học bổng"])
    print("Hạn nộp:", r["Hạn nộp"])
    print("Bậc học:", r["Bậc học"])
    print("Quốc gia:", r["Quốc gia du học"])
    print("Link:", r["Link bài viết trên Scholars4dev"])
    print()
