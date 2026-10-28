import cloudscraper
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

scraper = cloudscraper.create_scraper()

print("Testing Cloudscraper on Youth Opportunities...")
try:
    r_yo = scraper.get("https://www.youthop.com/scholarships", timeout=15)
    print("YouthOp Status:", r_yo.status_code, "Length:", len(r_yo.text))
except Exception as e:
    print("YouthOp error:", e)

print("\nTesting Cloudscraper on Chevening...")
try:
    r_ch = scraper.get("https://www.chevening.org/scholarships/", timeout=15)
    print("Chevening Status:", r_ch.status_code, "Length:", len(r_ch.text))
except Exception as e:
    print("Chevening error:", e)
