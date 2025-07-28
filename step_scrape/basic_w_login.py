# Có 2 cách 
# Dùng requests để giả lập đăng nhập
# Dùng Selenium để tự động hóa trình duyệt (good -> JS)


### Cách 1

# import requests
# from bs4 import BeautifulSoup, Tag
# from typing import Optional

# login_url = 'https://quotes.toscrape.com/login'
# protected_url = 'https://quotes.toscrape.com/'

# #Tạo session để duy trì trạng thái đăng nhập
# session = requests.Session()

# # Lấy CSRF token từ trang login
# login_page = session.get(login_url)
# soup = BeautifulSoup(login_page.text, 'html.parser')
# csrf_token = soup.find('input',{'name': 'csrf_token'})['value']

# payload = {
#     'username': 'admin',
#     'password': 'admin',
#     'csrf_token': csrf_token
# }

# # Gửi POST để đăng nhập
# response = session.post(login_url, data=payload)

# if 'Logout' in response.text:
#     print('Đăng nhập thành công!')
#     # Truy cập trang cần scrape sau khi đăng nhập
#     protected_response = session.get(protected_url)
#     if protected_response.ok:
#         # In ra 5 quote đầu tiên làm ví dụ
#         soup = BeautifulSoup(protected_response.text, 'html.parser')
#         quotes = soup.find_all('span', class_='text')
#         for i, quote in enumerate(quotes[:5], 1):
#             print(f"Quote {i}: {quote.text}")
#     else:
#         print('Không truy cập được trang bảo vệ!')
# else:
#     print('Đăng nhập thất bại!')


### Cách 2

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(executable_path=r"E:\web-scraping\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    driver.get("https://quotes.toscrape.com/login")
    print("Trang hiện tại:", driver.current_url)

    # Đợi và điền username, password
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys("admin")
    password_input.send_keys("admin")
    password_input.send_keys(Keys.RETURN)

    # Đợi trang load sau đăng nhập
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
    )
    print("Đăng nhập thành công!")

    # Lấy 5 quote đầu tiên
    quotes = driver.find_elements(By.CSS_SELECTOR, 'span.text')
    for i, quote in enumerate(quotes[:5], 1):
        print(f"Quote {i}: {quote.text}")

finally:
    driver.quit()