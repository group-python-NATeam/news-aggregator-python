# news-aggregator-python
Dự án tập trung xây dựng một hệ thống hoàn chỉnh nhằm thu thập tin tức tiếng Việt từ các nguồn báo hợp lệ, sau đó tự động xử lý và làm giàu dữ liệu. Quy trình xử lý bao gồm các bước: làm sạch văn bản, loại bỏ bài viết trùng lặp, phân loại nội dung vào 8 chuyên mục chung bằng Machine Learning, và tạo một đoạn tóm tắt ngắn (3-5 câu).

thành viên nhóm:
Lê Minh Nhựt
Đặng Phước Mới 
Lê Trần Phú
Nguyễn Thị Huyền Trang
Châu Nguyễn Trọng Hiếu

version thống nhất cho python: 3.12.6

### Prerequisites (Yêu cầu)

- Git
- Python 3.11+
- Podman

### Installation (Cài đặt)

1.  **Clone the repository:**
    ```bash
    git clone [your-repo-url]
    cd news-agg-git2
    ```

2.  **Start the PostgreSQL Database with Podman:**
    ```bash
    # Create a persistent volume for the data
    podman volume create postgres_data

    # Run the PostgreSQL container
    podman run -d --name news_db_container -e POSTGRES_DB=news_db -e POSTGRES_USER=news_user -e POSTGRES_PASSWORD=your_strong_password -v postgres_data:/var/lib/postgresql/data -p 127.0.0.1:5432:5432 postgres:16
    ```

3.  **Set up the Python Environment:**
    ```bash
    # Create a virtual environment
    python -m venv venv

    # Activate it
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Tạo một file tên là `.env` ở thư mục gốc và copy nội dung từ file `.env.example` (nếu có) hoặc dùng mẫu sau:
    ```
    SECRET_KEY='your-super-secret-django-key'
    DEBUG=True
    DB_NAME=news_db
    DB_USER=news_user
    DB_PASSWORD=your_strong_password
    DB_HOST=127.0.0.1
    DB_PORT=5432
    ```

5.  **Run Database Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
