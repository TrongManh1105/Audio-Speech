import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import csv
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(DATA_DIR, "scholars4dev_all_live.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def extract_section(text, header_name, next_headers):
    next_pattern = "|".join([re.escape(h) for h in next_headers])
    pattern = rf"{re.escape(header_name)}[:\s]+(.*?)(?=(?:{next_pattern})[:\s]|$)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

headers_list = [
    "Brief description", "Host Institution(s)", "Field(s) of study", 
    "Number of Scholarships", "Target group", "Scholarship value/inclusions", 
    "Eligibility", "Application instructions", "Website"
]

def parse_post(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.content, "html.parser")
        title_elem = soup.find("h1")
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        content_elem = soup.find("div", class_="entry") or soup.find("div", class_="post_content") or soup.find("article")
        if not content_elem:
            return None
        full_text = content_elem.get_text(separator="\n", strip=True)
        
        deadline_match = re.search(r"Deadline[:\s]+([^\n\r]+)", full_text, re.I)
        deadline = deadline_match.group(1).strip() if deadline_match else "Annual / Varies"
        
        country_match = re.search(r"Study in[:\s]+([^\n\r]+)", full_text, re.I)
        study_in = country_match.group(1).strip() if country_match else "International"
        
        degree = "Masters / Bachelors / PhD"
        if "Master" in full_text[:400]:
            degree = "Masters Degree"
        elif "Bachelor" in full_text[:400] or "Undergraduate" in full_text[:400]:
            degree = "Bachelors Degree"
        elif "PhD" in full_text[:400] or "Doctoral" in full_text[:400]:
            degree = "PhD / Doctoral"
            
        brief = extract_section(full_text, "Brief description", headers_list[1:])
        host = extract_section(full_text, "Host Institution(s)", headers_list[2:])
        fields = extract_section(full_text, "Field(s) of study", headers_list[3:])
        num_scholarships = extract_section(full_text, "Number of Scholarships", headers_list[4:])
        target = extract_section(full_text, "Target group", headers_list[5:])
        value = extract_section(full_text, "Scholarship value/inclusions", headers_list[6:])
        eligibility = extract_section(full_text, "Eligibility", headers_list[7:])
        app_instructions = extract_section(full_text, "Application instructions", headers_list[8:])
        
        return {
            "Title": title,
            "Brief description": brief.replace("\n", " ")[:300] if brief else title,
            "Host Institution(s)": host.replace("\n", " ")[:200] if host else study_in + " Universities",
            "Field(s) of study": fields.replace("\n", " ")[:250] if fields else "All eligible degree programs",
            "Number of Scholarships": num_scholarships.replace("\n", " ")[:150] if num_scholarships else "Varies",
            "Target group": target.replace("\n", " ")[:200] if target else "International students",
            "Scholarship value/inclusions": value.replace("\n", " ")[:300] if value else "Tuition fee waiver and/or living allowance",
            "Eligibility": eligibility.replace("\n", " ")[:400] if eligibility else "Academic merit and admission to eligible course",
            "Application instructions": app_instructions.replace("\n", " ")[:400] if app_instructions else "Apply online via host institution portal",
            "Deadline": deadline,
            "Study in": study_in,
            "Degree Level": degree,
            "Scholars4dev URL": url
        }
    except Exception:
        return None

def main():
    print("[*] Tải danh sách toàn bộ URL từ post-sitemap...")
    r = requests.get("https://www.scholars4dev.com/post-sitemap.xml", headers=HEADERS, timeout=10)
    urls = re.findall(r'<loc>(https://[^<]+)</loc>', r.text)
    print(f"[+] Tìm thấy tổng cộng {len(urls)} bài viết trên toàn bộ website Scholars4dev!")
    
    results = []
    print(f"[*] Bắt đầu cào song song toàn bộ các bài viết (10 threads)...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(parse_post, u): u for u in urls}
        for future in as_completed(future_to_url):
            res = future.result()
            if res:
                results.append(res)
                if len(results) % 50 == 0:
                    print(f"    -> Đã cào sống được {len(results)}/{len(urls)} bài viết...")
                    
    print(f"[✓] Đã cào xong {len(results)} bài học bổng thực tế từ Scholars4dev!")
    
    fieldnames = [
        "Title", "Brief description", "Host Institution(s)", "Field(s) of study",
        "Number of Scholarships", "Target group", "Scholarship value/inclusions",
        "Eligibility", "Application instructions", "Deadline", "Study in", "Degree Level", "Scholars4dev URL"
    ]
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"[✓] Đã lưu {len(results)} bài viết vào: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
