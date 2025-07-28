import requests
from bs4 import BeautifulSoup, Tag
from typing import Optional


# Lấy nội dung của một trang HTML tĩnh (Không cần đăng nhập)
# requests + bs4

def basic_scrape_HTML() -> Optional[BeautifulSoup]:
    url = "https://books.toscrape.com/"
    try:
        req = requests.get(url)
        if req.status_code == 200:
            print(f"Successfully fetched {url}")
            print(f"Status Code: {req.status_code}")
            print(f"Content Length: {len(req.text)} characters")

            html_content = req.text
            soup = BeautifulSoup(html_content, 'html.parser')

            title = soup.find('title')
            if title:
                print(f"Page Title: {title.text}")

            links = soup.find_all('a')
            print(f"Found {len(links)} links on the page")

            return soup
        else:
            print(f"Failed to fetch {url}")
            print(f"Status Code: {req.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
if __name__ == "__main__":
    basic_scrape_HTML()

base_url = "https://0ae3005004d6f14e80dbbc8a000e00e7.web-security-academy.net/files/transcript/{}.txt"

for i in range(1, 11):  # Thử từ 1.txt đến 10.txt, có thể tăng số lượng nếu cần
    url = base_url.format(i)
    response = requests.get(url)
    if response.status_code == 200:
        print(f"--- Nội dung {i}.txt ---")
        print(response.text)
    else:
        print(f"{i}.txt không tồn tại hoặc không truy cập được.")
