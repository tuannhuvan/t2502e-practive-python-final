import mysql.connector
from mysql.connector import Error

# Cấu hình thông tin kết nối MySQL toàn cục
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'news_management'
}

# Phần này định nghĩa một hàm seed_initial_categories để nạp sẵn dữ liệu mẫu vào bảng categories. 
# Hàm này sử dụng câu lệnh SQL INSERT IGNORE để thêm các danh mục tin tức phổ biến vào bảng categories, 
# tránh lỗi nếu các danh mục đã tồn tại. Dữ liệu mẫu bao gồm các danh mục như "Công nghệ", "Kinh doanh", "Thể thao", "Giải trí" và "Sức khỏe". 
# Nếu có lỗi xảy ra trong quá trình kết nối hoặc thực thi câu lệnh SQL, lỗi sẽ được bắt và in ra màn hình.
def seed_initial_categories():
    query = "INSERT IGNORE INTO categories (category_name) VALUES (%s)"
    categories_data = [("Công nghệ",), ("Kinh doanh",), ("Thể thao",), ("Giải trí",), ("Sức khỏe",)]
    
    try:
        with mysql.connector.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, categories_data)
                conn.commit()
                print("[*] Đã kiểm tra và nạp sẵn dữ liệu mẫu (Seeding) thành công.")
    except Error as e:
        print(f"[!] Lỗi khi nạp dữ liệu danh mục: {e}")

if __name__ == "__main__":
    seed_initial_categories()