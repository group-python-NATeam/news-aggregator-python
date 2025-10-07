# Triển khai và Quản lý Dự án (DEPLOYMENT.md)

Phần này cung cấp hướng dẫn chi tiết về cách triển khai ứng dụng Website Tin tức Tự động lên môi trường production và các khía cạnh liên quan đến quản lý, bảo trì dự án.

## 1. Tổng quan về Triển khai (Deployment)

Chúng ta sẽ triển khai ứng dụng Django lên nền tảng **Render.com**. Render là một nền tảng PaaS (Platform as a Service) thân thiện với nhà phát triển, hỗ trợ triển khai các ứng dụng web, database và các dịch vụ khác một cách dễ dàng. Render cũng cung cấp các gói miễn phí hoặc chi phí thấp phù hợp cho các dự án khởi đầu.

### Các thành phần cần triển khai:

*   **Web Service:** Ứng dụng Django của chúng ta.
*   **PostgreSQL Database:** Database chính cho ứng dụng.

## 2. Chuẩn bị cho Production (Sprint 5)

Trước khi triển khai, cần cấu hình dự án Django để hoạt động tối ưu và an toàn trong môi trường production.

### 2.1. Cấu hình `settings.py`

Trong file `news_agg_project/settings.py`, bạn cần đảm bảo các cấu hình sau:

*   **`DEBUG = False`:** Luôn đặt `DEBUG` thành `False` trong môi trường production để tránh rò rỉ thông tin nhạy cảm và cải thiện hiệu năng.
*   **`ALLOWED_HOSTS`:** Cấu hình danh sách các tên miền mà ứng dụng của bạn sẽ phục vụ. Khi triển khai lên Render, bạn sẽ nhận được một URL công khai. Hãy thêm URL đó vào `ALLOWED_HOSTS`.
    ```python
    # settings.py
    ALLOWED_HOSTS = ['your-render-app-name.onrender.com', 'localhost', '127.0.0.1']
    ```
*   **`SECRET_KEY`:** Đảm bảo `SECRET_KEY` được lấy từ biến môi trường và là một chuỗi ký tự mạnh, ngẫu nhiên. **Không bao giờ hardcode `SECRET_KEY` trong code production.**
    ```python
    # settings.py
    import os
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-insecure-default-key-for-dev')
    ```
*   **Cấu hình Database PostgreSQL:** Sử dụng biến môi trường để kết nối với database PostgreSQL của Render.
    ```python
    # settings.py
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
    ```
    Bạn cần cài đặt thư viện `dj-database-url`:
    ```bash
    pip install dj-database-url
    ```
*   **Static Files:** Cấu hình để Django phục vụ các file tĩnh (CSS, JavaScript, hình ảnh) trong production. Render có thể tự động xử lý việc này nếu bạn cấu hình đúng.
    ```python
    # settings.py
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
    ```
    Bạn cũng cần cài đặt `whitenoise` để phục vụ static files trong production:
    ```bash
    pip install whitenoise
    ```
    Và thêm `whitenoise.middleware.WhiteNoiseMiddleware` vào `MIDDLEWARE` trong `settings.py` (trên `django.middleware.security.SecurityMiddleware`).

### 2.2. File `requirements.txt`

Đảm bảo file `requirements.txt` của bạn được cập nhật đầy đủ với tất cả các thư viện cần thiết cho production:

```bash
pip freeze > requirements.txt
```

### 2.3. File `Procfile`

Render sử dụng `Procfile` để biết cách khởi động ứng dụng của bạn. Tạo một file tên `Procfile` ở thư mục gốc của dự án:

```
# Procfile
web: gunicorn news_agg_project.wsgi --log-file -
```

Bạn cần cài đặt `gunicorn`:

```bash
pip install gunicorn
```

## 3. Triển khai lên Render.com (Sprint 5)

### 3.1. Tạo PostgreSQL Database trên Render

1.  Đăng nhập vào Render Dashboard.
2.  Chọn `New` -> `PostgreSQL`.
3.  Điền tên database, chọn region và gói dịch vụ (có gói miễn phí).
4.  Sau khi tạo, Render sẽ cung cấp một `External Database URL`. Lưu URL này lại, bạn sẽ cần nó sau.

### 3.2. Triển khai Django Web Service trên Render

1.  Đăng nhập vào Render Dashboard.
2.  Chọn `New` -> `Web Service`.
3.  Kết nối với tài khoản GitHub của bạn và chọn repository của dự án.
4.  **Cấu hình Web Service:**
    *   **Name:** Đặt tên cho dịch vụ web của bạn (ví dụ: `news-aggregator-app`).
    *   **Region:** Chọn region gần với database của bạn.
    *   **Branch:** `main` hoặc `develop` (tùy thuộc vào nhánh bạn muốn deploy).
    *   **Root Directory:** Thư mục gốc của dự án (thường là để trống).
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn news_agg_project.wsgi --log-file -`
    *   **Environment Variables:** Thêm các biến môi trường sau:
        *   `SECRET_KEY`: Một chuỗi ký tự mạnh, ngẫu nhiên.
        *   `DATABASE_URL`: Dán `External Database URL` bạn đã lấy từ bước tạo PostgreSQL database.
        *   `WEB_CONCURRENCY`: Số lượng worker của Gunicorn (ví dụ: `2` hoặc `4`).
        *   `DISABLE_COLLECTSTATIC`: `0` (để Render tự động chạy `collectstatic`).
5.  **Tạo Web Service.** Render sẽ tự động build và deploy ứng dụng của bạn.

### 3.3. Chạy Migrations trên Render

Sau khi deploy lần đầu, bạn cần chạy migrations để tạo bảng trong database production.

1.  Trong Render Dashboard, vào dịch vụ web của bạn.
2.  Chọn tab `Shell`.
3.  Chạy lệnh:
    ```bash
    python manage.py migrate
    ```
4.  Nếu cần, tạo superuser cho admin:
    ```bash
    python manage.py createsuperuser
    ```

## 4. Tự động hóa Crawler trên Production

Để đảm bảo dữ liệu luôn mới, chúng ta sẽ sử dụng GitHub Actions (như đã mô tả trong `CRAWLER.md`) để chạy các crawler định kỳ. GitHub Actions sẽ chạy trên môi trường riêng của nó và cần truy cập vào database production.

### 4.1. Cấu hình GitHub Secrets

Để GitHub Actions có thể kết nối với database production, bạn cần lưu `DATABASE_URL` vào GitHub Secrets:

1.  Trong repository GitHub của bạn, vào `Settings` -> `Secrets and variables` -> `Actions`.
2.  Chọn `New repository secret`.
3.  Tạo một secret tên `DATABASE_URL` và dán giá trị `External Database URL` của Render vào đó.

### 4.2. Cập nhật Workflow GitHub Actions

Trong file `.github/workflows/crawler.yml`, đảm bảo workflow có thể truy cập `DATABASE_URL`:

```yaml
# .github/workflows/crawler.yml

# ... (các phần khác)

jobs:
  crawl:
    runs-on: ubuntu-latest
    steps:
    # ... (các bước khác)

    - name: Run Crawlers
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }} # Truyền biến môi trường DATABASE_URL
      run: |
        python manage.py crawl_vnexpress cong-nghe --limit=20
        # ... các command crawler khác
```

## 5. Giám sát và Cảnh báo (Monitoring & Alerting) (Sprint 5)

Để đảm bảo ứng dụng hoạt động ổn định, việc giám sát là rất quan trọng.

*   **Render Logs:** Render cung cấp hệ thống log tích hợp. Bạn có thể xem log của Web Service và Database trực tiếp từ Dashboard của Render.
*   **Sentry:** Tích hợp Sentry (hoặc một dịch vụ tương tự) để theo dõi lỗi và hiệu năng của ứng dụng. Sentry có gói miễn phí cho các dự án nhỏ.
    *   Cài đặt `sentry-sdk`:
        ```bash
        pip install sentry-sdk
        ```
    *   Cấu hình trong `settings.py`:
        ```python
        # settings.py
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN"), # Lấy DSN từ biến môi trường
            integrations=[
                DjangoIntegration(),
            ],
            traces_sample_rate=1.0, # Adjust this value in production
            send_default_pii=True
        )
        ```
    *   Thêm biến môi trường `SENTRY_DSN` vào Render và GitHub Secrets.

## 6. Bảo trì và Cập nhật

*   **Cập nhật Dependencies:** Định kỳ cập nhật các thư viện Python (`pip install --upgrade -r requirements.txt`) và kiểm tra các lỗ hổng bảo mật.
*   **Kiểm tra Log:** Thường xuyên kiểm tra log của ứng dụng và crawler để phát hiện sớm các vấn đề.
*   **Tối ưu hóa Database:** Định kỳ kiểm tra và tối ưu hóa database (ví dụ: `VACUUM` trong PostgreSQL).
*   **Cập nhật Code:** Khi có thay đổi code, đẩy lên GitHub và Render sẽ tự động triển khai (nếu bạn cấu hình auto-deploy).

---

**Tác giả:** Manus AI
**Ngày:** 07/10/2025
