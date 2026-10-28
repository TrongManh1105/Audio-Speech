"""
Base scraper and data schema for scholarship recommendation system.
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import json
import csv

@dataclass
class ScholarshipItem:
    scholarship_id: str
    title: str
    source_name: str
    source_url: str
    host_country: str = "Tất cả / Không xác định"
    degree_level: str = "Thạc sĩ / Cử nhân / Khác"  # Bachelor, Master, PhD, Exchange
    funding_type: str = "Toàn phần / Bán phần"      # Fully Funded, Partially Funded, Tuition
    funding_details: str = ""
    eligible_nationalities: str = "Mọi quốc gia (bao gồm Việt Nam)"
    min_gpa: Optional[float] = None                # thang 4.0
    min_ielts: Optional[float] = None
    min_work_exp_years: Optional[int] = None
    deadline: str = "Xem chi tiết"
    field_of_study: str = "Mọi ngành"
    criteria_summary: str = ""
    raw_description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def save_to_json(items: List[ScholarshipItem], filepath: str):
    data = [item.to_dict() for item in items]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] Đã lưu {len(items)} học bổng vào: {filepath}")

def save_to_csv(items: List[ScholarshipItem], filepath: str):
    if not items:
        return
    keys = items[0].to_dict().keys()
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for item in items:
            writer.writerow(item.to_dict())
    print(f"[+] Đã xuất file CSV: {filepath}")
