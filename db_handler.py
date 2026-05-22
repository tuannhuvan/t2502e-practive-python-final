import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG

# Đây là lớp NewsDatabaseHandler để quản lý tất cả các thao tác liên quan đến cơ sở dữ liệu MySQL. 
# Lớp này bao gồm các phương thức để lấy danh sách danh mục, thêm/sửa/xóa nguồn tin, xử lý dữ liệu bài viết thô và phân trang hiển thị bài viết. 
# Mỗi phương thức đều sử dụng kết nối MySQL được thiết lập thông qua hàm _get_connection và xử lý lỗi một cách cơ bản.
class NewsDatabaseHandler:
    def __init__(self):
        self.config = DB_CONFIG

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    # QUẢN LÝ DANH MỤC (CATEGORIES)
    def get_all_categories(self):
        query = "SELECT id, category_name FROM categories"
        try:
            with self._get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except Error:
            return []

    # CRUD CHO BẢNG NGUỒN TIN (SOURCES)
    # Các phương thức add_source, get_all_sources, update_source và delete_source để quản lý nguồn tin trong cơ sở dữ liệu.
    def add_source(self, name, url, category_id):
        query = "INSERT INTO sources (source_name, url, category_id) VALUES (%s, %s, %s)"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (name, url, category_id))
                    conn.commit()
                    return cursor.lastrowid
        except Error as e:
            print(f"[!] Lỗi thêm nguồn tin: {e}")
            return None

    # Lấy danh sách tất cả nguồn tin kèm tên danh mục (nếu có) để hiển thị trong menu quản lý nguồn tin.
    def get_all_sources(self):
        query = """
            SELECT s.id, s.category_id, s.source_name, s.url, c.category_name 
            FROM sources s
            LEFT JOIN categories c ON s.category_id = c.id
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except Error:
            return []


    # Cập nhật thông tin nguồn tin dựa trên ID. Trả về số lượng bản ghi bị ảnh hưởng để kiểm tra thành công hay không.
    def update_source(self, source_id, name, url, category_id):
        query = "UPDATE sources SET source_name = %s, url = %s, category_id = %s WHERE id = %s"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (name, url, category_id, source_id))
                    conn.commit()
                    return cursor.rowcount
        except Error:
            return 0

    # Xóa nguồn tin dựa trên ID. Trả về True nếu xóa thành công, False nếu có lỗi hoặc ID không tồn tại.
    def delete_source(self, source_id):
        query = "DELETE FROM sources WHERE id = %s"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (source_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Error:
            return False

    # XỬ LÝ DỮ LIỆU CÀO (ARTICLES)
    # Phương thức insert_raw_article để thêm các bài viết thô thu thập được từ Cronjob 1 vào bảng articles. Sử dụng INSERT IGNORE để tránh trùng lặp URL.
    def insert_raw_article(self, source_id, category_id, title, url):
        query = "INSERT IGNORE INTO articles (source_id, category_id, title, url, status) VALUES (%s, %s, %s, %s, 0)"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (source_id, category_id, title, url))
                    conn.commit()
                    return cursor.rowcount  # Trả về 1 nếu thành công thêm mới, 0 nếu trùng url
        except Error:
            return 0

    # Lấy các bài viết mới chỉ có link (status=0) để phục vụ cho Cronjob 2. Trả về danh sách các bài viết thô cần xử lý.
    def get_pending_articles(self):
        query = "SELECT id, url FROM articles WHERE status = 0"
        try:
            with self._get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except Error:
            return []

    # Cập nhật nội dung đã cào được cho bài viết dựa trên ID và đánh dấu trạng thái đã hoàn thành (status=1). Trả về True nếu cập nhật thành công, False nếu có lỗi.
    def update_article_content(self, article_id, summary, content):
        query = "UPDATE articles SET summary = %s, content = %s, status = 1 WHERE id = %s"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (summary, content, article_id))
                    conn.commit()
                    return True
        except Error:
            return False

    # PHÂN TRANG HIỂN THỊ (PAGINATION)
    # Phương thức get_articles_paginated để lấy danh sách bài viết đã được xử lý (status=1) theo trang và số lượng bài viết mỗi trang. Trả về danh sách bài viết kèm thông tin nguồn tin và danh mục để hiển thị trong giao diện CLI.
    def get_articles_paginated(self, page, page_size=10):
        offset = (page - 1) * page_size
        query = """
            SELECT a.id, a.title, a.url, c.category_name, s.source_name, a.status 
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            LEFT JOIN sources s ON a.source_id = s.id
            WHERE a.status = 1
            ORDER BY a.created_at DESC
            LIMIT %s OFFSET %s
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (page_size, offset))
                    return cursor.fetchall()
        except Error:
            return []