from db_config import seed_initial_categories
from db_handler import NewsDatabaseHandler
from scheduler import NewsScheduler

# Lớp chính để chạy ứng dụng CLI quản lý hệ thống News Aggregator với các chức năng CRUD nguồn tin, xem bài viết phân trang và điều khiển tiến trình Cronjob thủ công.
class NewsAggregatorCLI:
    def __init__(self):
        # Thực hiện Seeding nạp dữ liệu danh mục mẫu vào các bảng đã tạo bằng SQL trước đó
        seed_initial_categories()
        
        self.db = NewsDatabaseHandler()
        self.scheduler = NewsScheduler()
        # Tự động bật tính năng chạy ngầm ngay khi mở ứng dụng
        self.scheduler.start_scheduler()

    def run(self):
        while True:
            print("\n=== HỆ THỐNG NEWS AGGREGATOR (CLI) ===")
            print(f"Trạng thái Cronjob tự động: {'[ĐANG BẬT]' if self.scheduler.is_running else '[ĐÃ TẮT]'}")
            print("1. Quản lý nguồn tin (Sources)")
            print("2. Xem danh sách bài viết (Articles - Phân trang)")
            print("3. Điều khiển thủ công / Cấu hình Cronjob")
            print("4. Thoát ứng dụng")
            print("====================================================================")
            
            choice = input("Nhập lựa chọn của bạn (1-4): ").strip()
            if choice == '1':
                self._menu_sources()
            elif choice == '2':
                self._view_articles_pagination()
            elif choice == '3':
                self._menu_cronjob()
            elif choice == '4':
                self.scheduler.stop_scheduler()
                print("Đang đóng ứng dụng... Tạm biệt!")
                break
            else:
                print("[!] Nhập sai định dạng. Vui lòng chọn từ 1 đến 4.")

    # MENU CHỨC NĂNG CRUD NGUỒN TIN (SOURCES)
    def _menu_sources(self):
        while True:
            print("\n--- QUẢN LÝ NGUỒN TIN ---")
            print("1. Xem danh sách nguồn báo hiện tại")
            print("2. Thêm nguồn báo mới")
            print("3. Cập nhật thông tin nguồn báo")
            print("4. Xóa nguồn báo")
            print("5. Quay lại Menu chính")
            
            choice = input("Chọn thao tác (1-5): ").strip()
            if choice == '1':
                sources = self.db.get_all_sources()
                print("\nDANH SÁCH NGUỒN TIN:")
                print(f"{'ID':<5} {'Tên Nguồn':<20} {'Danh Mục':<15} {'Đường dẫn URL'}")
                print("-" * 75)
                for s in sources:
                    print(f"{s['id']:<5} {s['source_name']:<20} {s['category_name'] if s['category_name'] else 'N/A':<15} {s['url']}")
            
            elif choice == '2':
                name = input("Nhập tên nguồn báo (Ví dụ: VnExpress Sức Khỏe): ")
                url = input("Nhập URL trang chuyên mục cần cào tin: ")
                
                categories = self.db.get_all_categories()
                print("\nChọn mã ID danh mục tương ứng:")
                for c in categories:
                    print(f"[{c['id']}] - {c['category_name']}")
                while True:
                    try:
                        cat_id = int(input("Nhập số ID danh mục: "))
                        break
                    except ValueError:
                        print("[!] Vui lòng nhập một số hợp lệ.")

                new_id = self.db.add_source(name, url, cat_id)
                if new_id:
                    print(f"[+] Thêm nguồn tin thành công. Mã ID mới: {new_id}")
                    
            elif choice == '3':
                source_id = int(input("Nhập ID nguồn báo cần sửa thông tin: "))
                name = input("Nhập tên nguồn mới: ")
                url = input("Nhập URL chuyên mục mới: ")
                categories = self.db.get_all_categories()
                for c in categories:
                    print(f"[{c['id']}] - {c['category_name']}")
                while True:
                    try:
                        cat_id = int(input("Nhập ID danh mục mới: "))
                        break
                    except ValueError:
                        print("[!] Vui lòng nhập một số hợp lệ.")

                if self.db.update_source(source_id, name, url, cat_id) > 0:
                    print("[+] Cập nhật dữ liệu thành công!")
                else:
                    print("[!] Sửa thất bại. Không tìm thấy ID hoặc thông tin không có thay đổi.")
                    
            elif choice == '4':
                source_id = int(input("Nhập ID nguồn báo muốn xóa: "))
                if self.db.delete_source(source_id):
                    print("[+] Đã xóa nguồn tin thành công (Hệ thống tự động xóa bài viết thuộc nguồn này).")
                else:
                    print("[!] Xóa thất bại. ID không hợp lệ.")
            elif choice == '5':
                break

    # GIAO DIỆN XỬ LÝ PHÂN TRANG BÀI VIẾT (PAGINATION)
    def _view_articles_pagination(self):
        current_page = 1
        page_size = 10
        
        while True:
            articles = self.db.get_articles_paginated(current_page, page_size)
            print(f"\n--- DANH SÁCH BÀI VIẾT - TRANG {current_page} ---")
            if not articles:
                print("[!] Không có dữ liệu hiển thị tại trang này.")
            else:
                print(f"{'STT':<5} {'Tiêu đề bài báo thu thập':<50} {'Nguồn':<12} {'Danh Mục':<12} {'Trạng thái'}")
                print("-" * 90)
                for idx, a in enumerate(articles, start=1):
                    status_text = "[Đã cào đủ]" if a['status'] == 1 else "[Thô - Chỉ có link]"
                    title_short = a['title'][:47] + "..." if len(a['title']) > 47 else a['title']
                    print(f"{(current_page-1)*page_size + idx:<5} {title_short:<50} {a['source_name'] if a['source_name'] else 'N/A':<12} {a['category_name'] if a['category_name'] else 'N/A':<12} {status_text}")
            
            print("\nLệnh điều hướng: [N] Trang sau | [P] Trang trước | [E] Thoát về Menu chính")
            action = input("Nhập lệnh điều hướng: ").strip().upper()
            
            if action == 'N':
                if len(articles) == page_size:
                    current_page += 1
                else:
                    print("[!] Bạn đang đứng tại trang cuối cùng.")
            elif action == 'P':
                if current_page > 1:
                    current_page -= 1
                else:
                    print("[!] Bạn đang đứng tại trang đầu tiên.")
            elif action == 'E':
                break

    # MENU ĐIỀU KHIỂN HỆ THỐNG CRONJOB THỦ CÔNG
    def _menu_cronjob(self):
        while True:
            print("\n--- ĐIỀU KHIỂN TIẾN TRÌNH CRONJOB ---")
            print(f"Trạng thái tự động chạy ngầm: {'[ĐANG BẬT]' if self.scheduler.is_running else '[ĐÃ TẮT]'}")
            print("1. Kích hoạt chạy ngầm tự động")
            print("2. Tạm dừng chạy ngầm tự động")
            print("3. ÉP CHẠY NGAY: Cronjob 1 (Quét lấy danh sách link thô)")
            print("4. ÉP CHẠY NGAY: Cronjob 2 (Tải nội dung chi tiết bài viết)")
            print("5. Quay lại Menu chính")
            
            choice = input("Chọn thao tác (1-5): ").strip()
            if choice == '1':
                self.scheduler.start_scheduler()
            elif choice == '2':
                self.scheduler.stop_scheduler()
            elif choice == '3':
                self.scheduler.cronjob_1_fetch_links()
            elif choice == '4':
                self.scheduler.cronjob_2_fetch_content()
            elif choice == '5':
                break

if __name__ == "__main__":
    app = NewsAggregatorCLI()
    app.run()