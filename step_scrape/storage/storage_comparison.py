import json
import csv
import pickle
import gzip
import sqlite3
import time
import os
from datetime import datetime

def create_sample_data():
    """
    Tạo dữ liệu mẫu để test
    """
    sample_books = []
    for i in range(1000):
        book = {
            'id': i + 1,
            'title': f'Book {i + 1}',
            'price': f'£{20 + (i % 50)}.99',
            'stock': 'In stock' if i % 10 != 0 else 'Out of stock',
            'rating': ['One', 'Two', 'Three', 'Four', 'Five'][i % 5],
            'url': f'https://example.com/book/{i + 1}',
            'image_url': f'https://example.com/images/book_{i + 1}.jpg',
            'page': (i // 20) + 1,
            'scraped_at': datetime.now().isoformat()
        }
        sample_books.append(book)
    return sample_books

def test_json_storage(data):
    """
    Test lưu trữ JSON
    """
    print("📊 Testing JSON storage...")
    
    start_time = time.time()
    
    # Lưu JSON thường
    with open('test_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    save_time = time.time() - start_time
    file_size = os.path.getsize('test_data.json')
    
    # Load JSON
    start_time = time.time()
    with open('test_data.json', 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    load_time = time.time() - start_time
    
    print(f"   ✅ JSON: Save {save_time:.3f}s, Load {load_time:.3f}s, Size {file_size:,} bytes")
    return save_time, load_time, file_size

def test_json_gzip_storage(data):
    """
    Test lưu trữ JSON nén gzip
    """
    print("📊 Testing JSON + Gzip storage...")
    
    start_time = time.time()
    
    # Lưu JSON nén
    with gzip.open('test_data.json.gz', 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    save_time = time.time() - start_time
    file_size = os.path.getsize('test_data.json.gz')
    
    # Load JSON nén
    start_time = time.time()
    with gzip.open('test_data.json.gz', 'rt', encoding='utf-8') as f:
        loaded_data = json.load(f)
    load_time = time.time() - start_time
    
    print(f"   ✅ JSON+Gzip: Save {save_time:.3f}s, Load {load_time:.3f}s, Size {file_size:,} bytes")
    return save_time, load_time, file_size

def test_pickle_storage(data):
    """
    Test lưu trữ Pickle
    """
    print("📊 Testing Pickle storage...")
    
    start_time = time.time()
    
    # Lưu Pickle
    with open('test_data.pkl', 'wb') as f:
        pickle.dump(data, f)
    
    save_time = time.time() - start_time
    file_size = os.path.getsize('test_data.pkl')
    
    # Load Pickle
    start_time = time.time()
    with open('test_data.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    load_time = time.time() - start_time
    
    print(f"   ✅ Pickle: Save {save_time:.3f}s, Load {load_time:.3f}s, Size {file_size:,} bytes")
    return save_time, load_time, file_size

def test_csv_storage(data):
    """
    Test lưu trữ CSV
    """
    print("📊 Testing CSV storage...")
    
    start_time = time.time()
    
    # Lưu CSV
    with open('test_data.csv', 'w', newline='', encoding='utf-8') as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    save_time = time.time() - start_time
    file_size = os.path.getsize('test_data.csv')
    
    # Load CSV
    start_time = time.time()
    loaded_data = []
    with open('test_data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            loaded_data.append(row)
    load_time = time.time() - start_time
    
    print(f"   ✅ CSV: Save {save_time:.3f}s, Load {load_time:.3f}s, Size {file_size:,} bytes")
    return save_time, load_time, file_size

def test_sqlite_storage(data):
    """
    Test lưu trữ SQLite
    """
    print("📊 Testing SQLite storage...")
    
    start_time = time.time()
    
    # Tạo database
    conn = sqlite3.connect('test_data.db')
    cursor = conn.cursor()
    
    # Tạo bảng
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            price TEXT,
            stock TEXT,
            rating TEXT,
            url TEXT,
            image_url TEXT,
            page INTEGER,
            scraped_at TEXT
        )
    ''')
    
    # Lưu dữ liệu
    for book in data:
        cursor.execute('''
            INSERT INTO books (id, title, price, stock, rating, url, image_url, page, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            book['id'], book['title'], book['price'], book['stock'],
            book['rating'], book['url'], book['image_url'], book['page'], book['scraped_at']
        ))
    
    conn.commit()
    save_time = time.time() - start_time
    file_size = os.path.getsize('test_data.db')
    
    # Load dữ liệu
    start_time = time.time()
    cursor.execute('SELECT * FROM books')
    loaded_data = cursor.fetchall()
    load_time = time.time() - start_time
    
    conn.close()
    
    print(f"   ✅ SQLite: Save {save_time:.3f}s, Load {load_time:.3f}s, Size {file_size:,} bytes")
    return save_time, load_time, file_size

def compare_storage_methods():
    """
    So sánh tất cả phương pháp lưu trữ
    """
    print("🚀 Bắt đầu so sánh phương pháp lưu trữ...")
    
    # Tạo dữ liệu mẫu
    sample_data = create_sample_data()
    print(f"📊 Tạo {len(sample_data)} records mẫu")
    
    results = {}
    
    # Test các phương pháp
    results['JSON'] = test_json_storage(sample_data)
    results['JSON+Gzip'] = test_json_gzip_storage(sample_data)
    results['Pickle'] = test_pickle_storage(sample_data)
    results['CSV'] = test_csv_storage(sample_data)
    results['SQLite'] = test_sqlite_storage(sample_data)
    
    # In kết quả so sánh
    print("\n📊 KẾT QUẢ SO SÁNH:")
    print("=" * 80)
    print(f"{'Method':<12} {'Save Time':<12} {'Load Time':<12} {'File Size':<15} {'Compression':<12}")
    print("-" * 80)
    
    json_size = results['JSON'][2]
    
    for method, (save_time, load_time, file_size) in results.items():
        compression = (1 - file_size / json_size) * 100 if method != 'JSON' else 0
        print(f"{method:<12} {save_time:<12.3f} {load_time:<12.3f} {file_size:<15,} {compression:<12.1f}%")
    
    # Tìm phương pháp tốt nhất
    best_save = min(results.items(), key=lambda x: x[1][0])
    best_load = min(results.items(), key=lambda x: x[1][1])
    best_size = min(results.items(), key=lambda x: x[1][2])
    
    print("\n🏆 KẾT LUẬN:")
    print(f"✅ Nhanh nhất khi lưu: {best_save[0]} ({best_save[1][0]:.3f}s)")
    print(f"✅ Nhanh nhất khi load: {best_load[0]} ({best_load[1][1]:.3f}s)")
    print(f"✅ Nhỏ nhất: {best_size[0]} ({best_size[1][2]:,} bytes)")
    
    # Dọn dẹp file test
    cleanup_test_files()

def cleanup_test_files():
    """
    Xóa các file test
    """
    test_files = [
        'test_data.json',
        'test_data.json.gz',
        'test_data.pkl',
        'test_data.csv',
        'test_data.db'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    
    print("\n🧹 Đã dọn dẹp file test")

def storage_recommendations():
    """
    Đưa ra khuyến nghị về lưu trữ
    """
    print("\n💡 KHUYẾN NGHỊ LƯU TRỮ:")
    print("=" * 50)
    
    recommendations = [
        {
            "use_case": "Dữ liệu nhỏ (< 1MB)",
            "recommendation": "JSON thường",
            "reason": "Đơn giản, dễ đọc, tương thích tốt"
        },
        {
            "use_case": "Dữ liệu lớn (> 1MB)",
            "recommendation": "JSON + Gzip",
            "reason": "Tiết kiệm dung lượng, vẫn dễ đọc"
        },
        {
            "use_case": "Tốc độ load quan trọng",
            "recommendation": "Pickle",
            "reason": "Load nhanh nhất, nhưng chỉ dùng trong Python"
        },
        {
            "use_case": "Cần query phức tạp",
            "recommendation": "SQLite",
            "reason": "Hỗ trợ SQL, index, join"
        },
        {
            "use_case": "Chia sẻ với Excel/Google Sheets",
            "recommendation": "CSV",
            "reason": "Tương thích với nhiều tool"
        }
    ]
    
    for rec in recommendations:
        print(f"📋 {rec['use_case']}")
        print(f"   → {rec['recommendation']}")
        print(f"   → Lý do: {rec['reason']}")
        print()

if __name__ == "__main__":
    compare_storage_methods()
    storage_recommendations() 