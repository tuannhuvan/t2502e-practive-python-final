import schedule
import time
import threading
from db_handler import NewsDatabaseHandler
from scraper import NewsScraper

# Lớp NewsScheduler để quản lý các tiến trình Cronjob tự động chạy ngầm định kỳ. 
# Lớp này bao gồm hai hàm chính là cronjob_1_fetch_links để quét nguồn báo lấy danh sách link bài viết mới và cronjob_2_fetch_content để cào tóm tắt và nội dung chi tiết cho các bài viết mới tìm được.
class NewsScheduler:
    # Phương thức __init__ để khởi tạo các đối tượng cần thiết như NewsDatabaseHandler và NewsScraper, cũng như biến is_running để kiểm soát trạng thái hoạt động của scheduler.
    def __init__(self):
        self.db = NewsDatabaseHandler()
        self.scraper = NewsScraper()
        self.is_running = False

    # Cronjob 1: Quét nguồn báo lấy danh sách link bài viết mới đưa vào DB. Hàm này sẽ được lên lịch chạy định kỳ vào lúc 08:00 AM hàng ngày.
    def cronjob_1_fetch_links(self):
        print("\n[Cronjob 1] Đang thực hiện tiến trình quét link thô tự động...")
        sources = self.db.get_all_sources()
        if not sources:
            print("[Cronjob 1] Trống: Chưa cấu hình nguồn báo nào trong hệ thống.")
            return

        total_inserted = 0
        for src in sources:
            links = self.scraper.fetch_links_from_source(src['url'])
            for item in links:
                count = self.db.insert_raw_article(src['id'], src['category_id'], item['title'], item['url'])
                total_inserted += count
        print(f"[Cronjob 1] Hoàn thành. Đã nạp thành công {total_inserted} link bài viết mới.")

    # Cronjob 2: Cào tóm tắt và nội dung chi tiết cho các bài viết mới tìm được. 
    # Hàm này sẽ được lên lịch chạy định kỳ 30 phút một lần để đảm bảo cập nhật nhanh chóng nội dung chi tiết cho các bài viết mới.
    def cronjob_2_fetch_content(self):
        print("\n[Cronjob 2] Đang thực hiện tiến trình cào nội dung chi tiết...")
        pending_articles = self.db.get_pending_articles()
        if not pending_articles:
            print("[Cronjob 2] Trống: Không có bài viết nào đang chờ xử lý nội dung.")
            return

        success_count = 0
        for article in pending_articles:
            detail = self.scraper.fetch_article_detail(article['url'])
            if detail:
                self.db.update_article_content(article['id'], detail['summary'], detail['content'])
                success_count += 1
                
        print(f"[Cronjob 2] Hoàn thành. Đã cập nhật xong nội dung chi tiết cho {success_count} bài viết.")

    # Phương thức _scheduler_loop để chạy vòng lặp kiểm tra và thực thi các công việc đã lên lịch. 
    # Vòng lặp này sẽ tiếp tục chạy miễn là biến is_running được đặt thành True, và sẽ gọi schedule.run_pending() để thực thi các công việc đã đến thời gian thực hiện.
    def _scheduler_loop(self):
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)

    # Phương thức start_scheduler để kích hoạt hệ thống Cronjobs chạy ngầm tự động định kỳ. 
    # Hàm này sẽ thiết lập các công việc cần thực hiện theo lịch đã định và khởi động một thread riêng để chạy vòng lặp kiểm tra công việc.
    def start_scheduler(self):
        if self.is_running:
            return
            
        schedule.clear()
        # Cronjob 1: Chạy định kỳ 15 giây một lần để lấy link bài mới
        schedule.every(15).seconds.do(self.cronjob_1_fetch_links)
        # Cronjob 2: Chạy định kỳ 10 giây một lần để xử lý sâu nội dung các link tìm được
        schedule.every(10).seconds.do(self.cronjob_2_fetch_content)
        
        self.is_running = True
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        print("[*] Đã kích hoạt hệ thống Cronjobs chạy ngầm tự động định kỳ.")

    # Phương thức stop_scheduler để tắt hệ thống Cronjobs chạy ngầm tự động. Hàm này sẽ đặt biến is_running thành False để dừng vòng lặp kiểm tra công việc, và in ra thông báo đã tạm dừng hệ thống.
    def stop_scheduler(self):
        self.is_running = False
        print("[*] Chế độ tự động chạy ngầm (Cronjobs) đã tạm dừng.")