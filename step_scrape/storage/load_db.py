import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from datetime import datetime
import os

class OptimizedScraper:
    def __init__(self):
        self.base_url = "https://books.toscrape.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def scrape_to_database(self):
        """
        Scrape và chỉ lưu vào database
        """
        print("🚀 Bắt đầu scrape và lưu vào database...")
        
        # Tạo thư mục lưu trữ
        os.makedirs('data', exist_ok=True)
        
        # Khởi tạo database
        self.init_database()
        
        page = 1
        total_books = 0
        
        while True:
            try:
                # Tạo URL
                if page == 1:
                    url = f"{self.base_url}/index.html"
                else:
                    url = f"{self.base_url}/catalogue/page-{page}.html"
                
                print(f"Trang {page}: {url}")
                
                response = self.session.get(url)
                
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                books = soup.find_all('article', class_='product_pod')
                
                if not books:
                    break
                
                print(f"Tìm thấy {len(books)} sách")
                
                # Xử lý từng sách và lưu vào database
                for book in books:
                    book_data = self.extract_book_info(book, page)
                    self.save_to_database(book_data)
                    total_books += 1
                
                print(f"Đã lưu {len(books)} sách vào database")
                
                page += 1
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Lỗi trang {page}: {e}")
                break
        
        print(f"\n Hoàn thành: {total_books} sách từ {page-1} trang đã được lưu vào database")
        return total_books
    
    def init_database(self):
        """
        Khởi tạo SQLite database
        """
        self.conn = sqlite3.connect('data/books.db')
        self.cursor = self.conn.cursor()
        
        # Tạo bảng
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price TEXT,
                stock TEXT,
                rating TEXT,
                url TEXT,
                image_url TEXT,
                page INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        print("✅ Database đã được khởi tạo")
    
    def save_to_database(self, book_data):
        """
        Lưu một cuốn sách vào database
        """
        try:
            self.cursor.execute('''
                INSERT INTO books (title, price, stock, rating, url, image_url, page)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                book_data['title'],
                book_data['price'],
                book_data['stock'],
                book_data['rating'],
                book_data['url'],
                book_data['image_url'],
                book_data['page']
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Lỗi lưu DB: {e}")
    
    def get_books_from_database(self):
        self.cursor.execute('SELECT * FROM books')
        return self.cursor.fetchall()
    
    def get_books_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM books')
        return self.cursor.fetchone()[0]
    
    def get_books_by_page(self, page):
        self.cursor.execute('SELECT * FROM books WHERE page = ?', (page,))
        return self.cursor.fetchall()
    
    def get_books_by_rating(self, rating):
        self.cursor.execute('SELECT * FROM books WHERE rating = ?', (rating,))
        return self.cursor.fetchall()
    
    def get_books_by_price_range(self, min_price, max_price):
        self.cursor.execute('''
            SELECT * FROM books 
            WHERE CAST(REPLACE(REPLACE(price, '£', ''), 'Â', '') AS REAL) 
            BETWEEN ? AND ?
        ''', (min_price, max_price))
        return self.cursor.fetchall()
    
    def get_statistics(self):
        self.cursor.execute('SELECT COUNT(*) FROM books')
        total_books = self.cursor.fetchone()[0]
        
        # Số trang
        self.cursor.execute('SELECT MAX(page) FROM books')
        total_pages = self.cursor.fetchone()[0] or 0
        
        # Thống kê rating
        self.cursor.execute('SELECT rating, COUNT(*) FROM books GROUP BY rating')
        ratings = dict(self.cursor.fetchall())
        
        # Thống kê giá
        self.cursor.execute('''
            SELECT 
                MIN(CAST(REPLACE(REPLACE(price, '£', ''), 'Â', '') AS REAL)) as min_price,
                MAX(CAST(REPLACE(REPLACE(price, '£', ''), 'Â', '') AS REAL)) as max_price,
                AVG(CAST(REPLACE(REPLACE(price, '£', ''), 'Â', '') AS REAL)) as avg_price
            FROM books 
            WHERE price != 'N/A'
        ''')
        price_stats = self.cursor.fetchone()
        
        return {
            'total_books': total_books,
            'total_pages': total_pages,
            'ratings': ratings,
            'price_stats': {
                'min': price_stats[0] if price_stats[0] else 0,
                'max': price_stats[1] if price_stats[1] else 0,
                'avg': price_stats[2] if price_stats[2] else 0
            }
        }
    
    def extract_book_info(self, book_element, page):
        """
        Trích xuất thông tin sách
        """
        try:
            title_elem = book_element.find('h3').find('a')
            title = title_elem.get('title', '').strip()
            url = self.base_url + '/catalogue/' + title_elem.get('href', '')
            
            price_elem = book_element.find('p', class_='price_color')
            if price_elem:
                price = price_elem.text.strip()
                # Làm sạch giá sách
                price = price.replace('Â', '').strip()
            else:
                price = 'N/A'
            
            stock_elem = book_element.find('p', class_='instock availability')
            stock = stock_elem.text.strip() if stock_elem else 'N/A'
            
            rating_elem = book_element.find('p', class_='star-rating')
            if rating_elem:
                rating_class = rating_elem.get('class', [])
                rating = [cls for cls in rating_class if cls != 'star-rating']
                rating = rating[0] if rating else 'N/A'
            else:
                rating = 'N/A'
            
            img_elem = book_element.find('img')
            image_url = self.base_url + img_elem.get('src', '').replace('../', '') if img_elem else 'N/A'
            
            return {
                'title': title,
                'price': price,
                'stock': stock,
                'rating': rating,
                'url': url,
                'image_url': image_url,
                'page': page
            }
            
        except Exception as e:
            print(f"❌ Lỗi xử lý sách: {e}")
            return {
                'title': 'Error',
                'price': 'N/A',
                'stock': 'N/A',
                'rating': 'N/A',
                'url': 'N/A',
                'image_url': 'N/A',
                'page': page
            }
    
    def close(self):
        """
        Đóng kết nối database
        """
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    scraper = OptimizedScraper()
    
    try:
        # Scrape dữ liệu vào database
        total_books = scraper.scrape_to_database()
        
        # Hiển thị thống kê
        print("\n📊 Thống kê từ database:")
        stats = scraper.get_statistics()
        print(f"📚 Tổng số sách: {stats['total_books']}")
        print(f"📄 Tổng số trang: {stats['total_pages']}")
        print(f"💰 Thống kê giá:")
        print(f"   - Giá thấp nhất: £{stats['price_stats']['min']:.2f}")
        print(f"   - Giá cao nhất: £{stats['price_stats']['max']:.2f}")
        print(f"   - Giá trung bình: £{stats['price_stats']['avg']:.2f}")
        print(f"⭐ Thống kê rating:")
        for rating, count in stats['ratings'].items():
            print(f"   - {rating}: {count} sách")
        
        # Demo truy vấn database
        print("\n🔍 Demo truy vấn database:")
        
        # Lấy 5 sách đầu tiên
        books = scraper.get_books_from_database()
        print(f"✅ Tổng số sách trong DB: {len(books)}")
        
        # Lấy sách từ trang 1
        page1_books = scraper.get_books_by_page(1)
        print(f"✅ Sách từ trang 1: {len(page1_books)} cuốn")
        
        # Lấy sách có rating Five
        five_star_books = scraper.get_books_by_rating('Five')
        print(f"✅ Sách 5 sao: {len(five_star_books)} cuốn")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()