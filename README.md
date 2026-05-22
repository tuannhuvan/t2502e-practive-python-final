Link Video: https://drive.google.com/drive/u/1/folders/1yNVrku__EqLvr2YZEQ21DdQEhpCyec5T

# 📰 Hệ Thống News Aggregator (CLI) - Python & MySQL

Hệ thống quản lý nguồn tin tức và tự động hóa quy trình thu thập dữ liệu bất đồng bộ từ các website báo chí sử dụng ngôn ngữ **Python **, thư viện bóc tách **BeautifulSoup4**, lập lịch tác vụ **Schedule**, hoạt động trên nền tảng cơ sở dữ liệu **MySQL**.

---

## 🏗️ 1. Kiến Trúc Phân Lớp & Cấu Trúc Thư Mục
Dự án được thiết kế theo nguyên lý thiết kế phần mềm hiện đại, chia tách độc lập các lớp đảm nhiệm (Separation of Concerns) để tối ưu hóa hiệu suất cào tin và quản trị mã nguồn:

```text
📂 news_aggregator_project/
├── 📄 database_schema.sql  # Định nghĩa cấu trúc Database (Schema) ở tầng DB
├── 📄 db_config.py        # Tập trung thông tin kết nối và thực hiện Seeding dữ liệu danh mục
├── 📄 db_handler.py       # Tầng Data Access Object (DAO) - Thực thi mọi truy vấn CRUD với MySQL
├── 📄 scraper.py          # Tầng Logic bóc tách DOM HTML (Sử dụng Requests & BeautifulSoup4)
├── 📄 scheduler.py        # Tầng tự động hóa (Quản lý các Cronjobs chạy ngầm bằng Multi-threading)
└── 📄 main.py             # Ứng dụng Entry Point - Điều khiển Menu Terminal (CLI) và Phân trang (Pagination)

⚡ 2. Điểm Nhấn Công Nghệ & Giải Thuật Cốt Lõi (Phục Vụ Thuyết Trình)
Đa Luồng (Multi-threading) Giải Quyết Treo Giao Diện
Thực trạng vấn đề: Thư viện lập lịch schedule bắt buộc phải duy trì một vòng lặp vô hạn while True: schedule.run_pending() để giám sát thời gian. Nếu thực thi vòng lặp này trên luồng chính (Main Thread), toàn bộ Menu tương tác bấm số của người dùng sẽ bị đóng băng.

Giải pháp kiến trúc: Hệ thống đóng gói vòng lặp giám sát vào phương thức chạy ngầm thông qua thư viện threading.Thread(..., daemon=True). Luồng phụ này sẽ chạy song song dưới nền hệ điều hành để kích hoạt các Cronjob đúng giờ, giải phóng hoàn toàn luồng chính giúp Menu CLI luôn luôn mượt mà và tiếp nhận lệnh điều hướng của người dùng bất cứ lúc nào.

Kiến Trúc Cào Tin Bất Đồng Bộ Qua Trạng Thái (Status Flag)
Hệ thống chia quy trình cào tin làm 2 bước độc lập nhằm giảm thiểu dung lượng chiếm dụng bộ nhớ RAM và băng thông mạng:

Cronjob 1 (Quét Link Thô - Chạy định kỳ lúc 08:00 AM): Chỉ quét nhanh qua các thẻ tiêu đề chuyên mục của nguồn báo nhằm lấy về Tiêu đề + URL của bài viết mới. Lưu thô dữ liệu vào Database với trạng thái status = 0 (Nội dung và Tóm tắt để trống).

Cronjob 2 (Tải Nội Dung Chi Tiết - Chạy định kỳ mỗi 30 phút): Quét trong Database tìm những bài viết có status = 0, truy cập trực tiếp vào liên kết của bài viết đó để bóc tách sâu phần Tóm tắt (summary) và Văn bản (content), sau đó lưu bổ sung và chuyển đổi sang trạng thái status = 1.

Cơ Chế Chống Trùng Lặp Tin Tức Tuyệt Đối (Tầng DB)
Trường dữ liệu url trong bảng articles cấu hình thuộc tính ràng buộc UNIQUE. Kết hợp với câu lệnh INSERT IGNORE INTO ở tầng Python, hệ thống đảm bảo dù một nguồn báo có bị quét đi quét lại hàng trăm lần, MySQL sẽ tự động loại bỏ các liên kết cũ đã tồn tại, không ghi đè rác dữ liệu và không gây crash ứng dụng.

🚀 3. Hướng Dẫn Cài Đặt & Vận Hành
Bước 1: Khởi tạo Cấu trúc Cơ sở dữ liệu
Sau khi tạo cơ sở dữ liệu trên máy chủ MySQL, bạn thực thi mã SQL trong file database_schema.sql trực tiếp thông qua công cụ quản trị của bạn (MySQL Workbench hoặc phpMyAdmin) để dựng cấu trúc các bảng.

Bước 2: Cài đặt các thư viện bổ trợ qua Terminal
Mở công cụ dòng lệnh tại thư mục dự án và thực thi lệnh cài đặt:

Bash
pip install mysql-connector-python requests beautifulsoup4 schedule
Bước 3: Cấu hình thông số Tài khoản
Truy cập file db_config.py, hiệu chỉnh lại tham số kết nối MySQL phù hợp với máy cá nhân của bạn:

Python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # Thay thế tài khoản MySQL của bạn
    'password': 'password',     # Thay thế mật khẩu MySQL của bạn
    'database': 'news_management'
}
Bước 4: Khởi chạy hệ thống
Thực hiện chạy tệp tin giao diện điều khiển chính:

Bash
python main.py
Lưu ý: Hệ thống sẽ tự động kích hoạt tiến trình Seed nạp dữ liệu 5 danh mục gốc bao gồm: Công nghệ, Kinh doanh, Thể thao, Giải trí, Sức khỏe vào hệ thống bảng ngay lần chạy đầu tiên.

📱 4. Quy Trình Sử Dụng & Điều Hướng Phân Trang Trên CLI
Quản lý Nguồn tin (Menu 1): Người dùng thực hiện cấu hình thêm mới các URL trang báo (Ví dụ mục số hóa của VnExpress: https://vnexpress.net/so-hoa). Hệ thống sẽ ép buộc bạn liên kết nguồn tin này tới một trong các mã ID danh mục hợp lệ có sẵn.

Xem danh sách bài viết (Menu 2): Hệ thống áp dụng thuật toán phân trang tối ưu hiệu năng thông qua mệnh đề LIMIT 10 OFFSET ((page-1)*10) trực tiếp từ câu lệnh MySQL.

Gõ phím N (Next): Tiến đến trang dữ liệu tiếp theo.

Gõ phím P (Previous): Quay lui về trang dữ liệu trước đó.

Gõ phím E (Exit): Thoát giao diện xem tin trở lại Menu tổng quản.

Điều khiển Cronjob (Menu 3): Cho phép bạn chủ động Bật/Tắt tiến trình quét tự động, hoặc kích hoạt Ép buộc chạy ngay lập tức (Force Execute) các hàm Cronjob 1 hoặc Cronjob 2 để kiểm thử dữ liệu mà không cần chờ đợi đúng thời gian cài đặt.