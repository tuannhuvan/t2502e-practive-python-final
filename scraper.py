import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class NewsScraper:
    def __init__(self):
        # Thiết lập Header giả lập trình duyệt để tránh bị tường lửa của các trang báo chặn truy cập
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    # Phương thức fetch_links_from_source để quét nguồn báo lấy danh sách link bài viết mới. Hàm này sẽ được lên lịch chạy định kỳ vào lúc 08:00 AM hàng ngày.
    def fetch_links_from_source(self, url):
        articles_found = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return articles_found
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tag_name in ['h1', 'h2', 'h3']:
                for heading in soup.find_all(tag_name):
                    a_tag = heading.find('a')
                    if a_tag and a_tag.get('href') and a_tag.text.strip():
                        title = a_tag.text.strip()
                        link = a_tag['href']
                        
                        # Chuyển đổi đường dẫn tương đối (Relative URL) thành tuyệt đối (Absolute URL)
                        link = urljoin(url, link)
                        articles_found.append({'title': title, 'url': link})
        except Exception as e:
            print(f"[!] Lỗi khi quét danh sách link tại {url}: {e}")
            
        return articles_found

    # Phương thức fetch_article_detail để truy cập vào bài viết chi tiết và lấy phần Tóm tắt (Summary) và Văn bản nội dung (Content).
    def fetch_article_detail(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Trích xuất tóm tắt từ thẻ meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            summary = meta_desc['content'].strip() if meta_desc else "Không có tóm tắt."
            
            # 2. Thu thập nội dung chính từ toàn bộ thẻ <p> gộp lại
            paragraphs = soup.find_all('p')
            content_text = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])
            
            # Cắt ngắn chuỗi tránh việc tràn vùng nhớ dữ liệu văn bản quá lớn
            if len(content_text) > 1500:
                content_text = content_text[:1500] + "..."
                
            return {'summary': summary, 'content': content_text}
        except Exception as e:
            print(f"[!] Lỗi khi cào chi tiết bài viết tại {url}: {e}")
            return None