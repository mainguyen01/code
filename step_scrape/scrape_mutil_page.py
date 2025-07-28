import requests
from bs4 import BeautifulSoup
import csv
import json
import time

def scrape_books_toscrape():
    base_url = "https://books.toscrape.com"
    all_books = []
    page = 1

    while True:
        try:
            if page == 1:
                url = f"{base_url}/index.html"
            else:
                url = f"{base_url}/catalogue/page-{page}.html"
            
            req = requests.get(url)

            if req.status_code != 200:
                print(f"Không thể truy cập trang {page}")
                break

            soup = BeautifulSoup(req.text, 'html.parser')
            books = soup.find_all('article', class_='product_pod')

            if not books:
                print(f"Đã scrape xong tất cả trang (dừng ở trang {page-1})")
                break

            # Xử lý từng cuốn sách
            for book in books:
                book_data = extract_book_info(book, base_url)
                all_books.append(book_data)
                print(f"{book_data['title']} - £{book_data['price']}")
            
            page += 1
            time.sleep(1)  # Delay để tránh overload server
        
        except Exception as e:
            print(f"❌ Lỗi ở trang {page}: {e}")
            break
    
    save_results(all_books)
    return all_books

def extract_book_info(book_element, base_url):
    book_data = {}
    
    try:
        # Tiêu đề
        title_elem = book_element.find('h3').find('a')
        book_data['title'] = title_elem.get('title', '').strip()
        book_data['url'] = base_url + '/catalogue/' + title_elem.get('href', '')
        
        # Giá
        price_elem = book_element.find('p', class_='price_color')
        clean_price1 = price_elem.text.strip()
        clean_price2 = clean_price1.replace('Â', '').strip()
        book_data['price'] = clean_price2 if price_elem else 'N/A'
        
        # Tình trạng stock
        stock_elem = book_element.find('p', class_='instock availability')
        book_data['stock'] = stock_elem.text.strip() if stock_elem else 'N/A'
        
        # Rating (số sao)
        rating_elem = book_element.find('p', class_='star-rating')
        if rating_elem:
            rating_class = rating_elem.get('class', [])
            rating = [cls for cls in rating_class if cls != 'star-rating']
            book_data['rating'] = rating[0] if rating else 'N/A'
        else:
            book_data['rating'] = 'N/A'
        
        # Hình ảnh
        img_elem = book_element.find('img')
        if img_elem:
            book_data['image_url'] = base_url + img_elem.get('src', '').replace('../', '')
        else:
            book_data['image_url'] = 'N/A'
            
    except Exception as e:
        print(f"Lỗi khi xử lý sách: {e}")
        book_data = {
            'title': 'Error',
            'price': 'N/A',
            'stock': 'N/A',
            'rating': 'N/A',
            'url': 'N/A',
            'image_url': 'N/A'
        }
    
    return book_data

def save_results(books):

    # Lưu CSV
    try:
        with open('books_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'price', 'stock', 'rating', 'url', 'image_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for book in books:
                writer.writerow(book)     
    except Exception as e:
        print(f"❌ Lỗi khi lưu CSV: {e}")
    
    # Lưu JSON
    try:
        with open('books_data.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(books, jsonfile, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Lỗi khi lưu JSON: {e}")


#Scrape sách theo từng category
def scrape_by_category():
    base_url = "https://books.toscrape.com"
    
    # Lấy trang chủ để tìm categories
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tìm sidebar categories
    sidebar = soup.find('div', class_='side_categories')
    if sidebar:
        categories = sidebar.find_all('a')
        
        for category in categories:
            category_name = category.text.strip()
            category_url = base_url + '/' + category.get('href', '')
            
            print(f"Category: {category_name}")
            print(f"🔗 URL: {category_url}")
            
            # Scrape category này
            scrape_category(category_url, category_name)

def scrape_category(category_url, category_name):
    all_books = []
    page = 1

    while True:
        try:
            if page == 1:
                url = category_url
            else:
                url = category_url.replace('/index.html', f'/page-{page}.html')
            
            print(f"Trang {page}: {url}")
            response = requests.get(url)
            
            if response.status_code != 200:
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            books = soup.find_all('article', class_='product_pod')
            
            if not books:
                break
            
            for book in books:
                book_data = extract_book_info(book, "https://books.toscrape.com")
                book_data['category'] = category_name
                all_books.append(book_data)
            
            page += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"Lỗi: {e}")
            break

    # Lưu category
    if all_books:
        filename = f"books_{category_name.lower().replace(' ', '_')}.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['title', 'price', 'stock', 'rating', 'url', 'image_url', 'category']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for book in all_books:
                    writer.writerow(book)
            print(f"Đã lưu {len(all_books)} sách vào {filename}")
        except Exception as e:
            print(f"Lỗi khi lưu: {e}")

if __name__ == "__main__":
    print("Chọn mode scrape:")
    print("1. Scrape tất cả sách (tất cả trang)")
    print("2. Scrape theo category")
    
    choice = input("Nhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == "1":
        scrape_books_toscrape()
    elif choice == "2":
        scrape_by_category()
    else:
        print("Lựa chọn không hợp lệ!") 