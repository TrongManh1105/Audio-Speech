import csv
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

file_path = "data/scholars4dev.csv"

targets = [9, 15, 20, 25, 30, 35, 40]

with open(file_path, mode="r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        idx = i + 1
        if idx in targets:
            print(f"--- DÒNG {idx} ---")
            print("Tên:", row["Tên học bổng"])
            print("Trường:", row["Trường / Cơ sở đào tạo"])
            print("Ngành:", row["Ngành học áp dụng"])
            print("Số lượng suất:", row["Số lượng suất học bổng"])
            print("Hạn nộp:", row["Hạn nộp"])
            print("Bậc học:", row["Bậc học"])
            print()
