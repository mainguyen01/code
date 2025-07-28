import requests
from bs4 import BeautifulSoup
import csv

def get_gdp_table_data(url):
    req = requests.get(url)
    if req.ok:
        soup = BeautifulSoup(req.text, "html.parser")
        table = soup.find("table", {"class": "wikitable"})
        rows = table.find_all("tr")
        headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        data = []
        for row in rows[1:]:
            cols = row.find_all(["td", "th"])
            row_data = [col.get_text(strip=True) for col in cols]
            if row_data:
                data.append(row_data)
        return headers, data
    else:
        print("khong truy cap duoc trang web")
        return None, None

def export_to_csv(headers, data, filename):
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"Đã xuất dữ liệu ra file {filename}")

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    headers, data = get_gdp_table_data(url)
    if headers and data:
        export_to_csv(headers, data, "gdp_countries.csv")
