from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

service = Service(executable_path=r"E:\web-scraping\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://quotes.toscrape.com/js/")
print("Trang hiện tại:", driver.current_url)

# Chờ cho các quote xuất hiện
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "quote"))
)

quotes = []
quote_elements = driver.find_elements(By.CLASS_NAME, "quote")
for quote in quote_elements:
    text = quote.find_element(By.CLASS_NAME, "text").text
    author = quote.find_element(By.CLASS_NAME, "author").text
    tags = [tag.text for tag in quote.find_elements(By.CLASS_NAME, "tag")]
    quotes.append({
        "text": text,
        "author": author,
        "tags": tags
    })

# Lưu dữ liệu bằng pickle
with open("quotes_js.pkl", "wb") as f:
    pickle.dump(quotes, f)

# Lưu dữ liệu sang CSV
import csv
with open("quotes_js.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
    writer.writeheader()
    for q in quotes:
        writer.writerow({
            "text": q["text"],
            "author": q["author"],
            "tags": ", ".join(q["tags"])
        })

# Lưu dữ liệu sang JSON
import json
with open("quotes_js.json", "w", encoding="utf-8") as f:
    json.dump(quotes, f, ensure_ascii=False, indent=2)

print("Đã lưu xong dữ liệu vào quotes_js.pkl, quotes_js.csv, quotes_js.json")
driver.quit()
