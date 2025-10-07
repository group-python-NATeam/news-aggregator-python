# Hướng dẫn Cài đặt Môi trường Phát triển (SETUP.md)

Chào mừng bạn đến với dự án Website Tin tức Tự động! Tài liệu này sẽ hướng dẫn bạn từng bước thiết lập môi trường phát triển trên máy cục bộ của mình. Chúng ta sẽ sử dụng **WSL2 (Ubuntu)** hoặc **Fedora** làm môi trường Linux, **Podman** để quản lý PostgreSQL database, và **Python/Django** cho ứng dụng chính.

## 1. Yêu cầu hệ thống

*   Hệ điều hành: Windows 10/11 (với WSL2) hoặc Fedora Linux.
*   RAM: Tối thiểu 8GB (khuyến nghị 16GB).
*   Dung lượng ổ đĩa trống: Tối thiểu 20GB.

## 2. Cài đặt WSL2 (Đối với người dùng Windows)

Nếu bạn đang dùng Windows, WSL2 là cách tốt nhất để có môi trường Linux mạnh mẽ. Nếu bạn dùng Fedora, bỏ qua bước này.

1.  **Kích hoạt WSL và Virtual Machine Platform:**
    Mở PowerShell với quyền Administrator và chạy các lệnh sau:
    ```bash
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    ```
    Khởi động lại máy tính khi được yêu cầu.

2.  **Cài đặt Kernel Linux:**
    Tải và cài đặt gói cập nhật kernel Linux cho WSL2 từ [đây](https://wslstore.blob.core.windows.net/wsl2kernel/wsl_update_x64.msi).

3.  **Đặt WSL2 làm phiên bản mặc định:**
    Mở PowerShell và chạy:
    ```bash
    wsl --set-default-version 2
    ```

4.  **Cài đặt bản phân phối Linux (Ubuntu):**
    Mở Microsoft Store, tìm kiếm và cài đặt `Ubuntu` (phiên bản LTS khuyến nghị, ví dụ Ubuntu 22.04 LTS). Sau khi cài đặt, mở Ubuntu và tạo tên người dùng, mật khẩu.

## 3. Cài đặt Podman

Podman là một công cụ quản lý container mạnh mẽ, an toàn và không yêu cầu quyền root. Chúng ta sẽ dùng Podman để chạy PostgreSQL database.

### Trên Ubuntu (WSL2):

```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt Podman
sudo apt install podman -y

# Khởi tạo cấu hình Podman rootless (không cần quyền root)
podman system migrate
podman system reset
```

### Trên Fedora:

Podman thường đã được cài đặt sẵn trên Fedora. Nếu chưa, bạn có thể cài đặt bằng lệnh:

```bash
sudo dnf install podman -y
```

## 4. Khởi tạo PostgreSQL Database với Podman

Chúng ta sẽ chạy PostgreSQL trong một container Podman để đảm bảo môi trường database sạch sẽ và dễ quản lý.

1.  **Tạo Volume cho dữ liệu:**
    Volume giúp dữ liệu database của bạn được lưu trữ bền vững, không bị mất khi container bị xóa.
    ```bash
    podman volume create news_agg_data
    ```

2.  **Chạy Container PostgreSQL:**
    Chạy lệnh sau để khởi động một container PostgreSQL. Thay thế `your_db_user`, `your_db_password`, `your_db_name` bằng thông tin bạn muốn.
    ```bash
    podman run -d --name news_agg_postgres \
      -e POSTGRES_USER=your_db_user \
      -e POSTGRES_PASSWORD=your_db_password \
      -e POSTGRES_DB=your_db_name \
      -p 5432:5432 \
      -v news_agg_data:/var/lib/postgresql/data \
      postgres:16
    ```
    *   `-d`: Chạy container ở chế độ nền (detached).
    *   `--name news_agg_postgres`: Đặt tên cho container.
    *   `-e`: Đặt biến môi trường cho PostgreSQL (tên người dùng, mật khẩu, tên DB).
    *   `-p 5432:5432`: Ánh xạ cổng 5432 của container ra cổng 5432 của máy host.
    *   `-v news_agg_data:/var/lib/postgresql/data`: Gắn volume `news_agg_data` vào thư mục lưu trữ dữ liệu của PostgreSQL trong container.
    *   `postgres:16`: Sử dụng image PostgreSQL phiên bản 16.

3.  **Kiểm tra trạng thái Container:**
    ```bash
    podman ps
    ```
    Bạn sẽ thấy container `news_agg_postgres` đang chạy.

## 5. Cài đặt Python và Dependencies

1.  **Cài đặt Python 3.12 và pip:**
    ```bash
    sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip -y
    ```

2.  **Tạo và kích hoạt Virtual Environment:**
    Điều hướng đến thư mục gốc của dự án của bạn (nơi chứa `manage.py`).
    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    ```
    (Để thoát virtual environment, dùng lệnh `deactivate`)

3.  **Cài đặt các thư viện Python:**
    ```bash
    pip install -r requirements.txt
    ```
    (Nếu chưa có file `requirements.txt`, bạn có thể tạo nó sau khi clone repo và chạy `pip freeze > requirements.txt`)

## 6. Cấu hình Dự án Django

1.  **Clone Repository:**
    ```bash
    git clone <URL_TO_YOUR_REPO>
    cd news-aggregator-python # Hoặc tên thư mục dự án của bạn
    ```

2.  **Tạo file `.env`:**
    Trong thư mục gốc của dự án (cùng cấp với `manage.py`), tạo một file tên `.env` và điền thông tin database bạn đã dùng khi tạo container PostgreSQL.
    ```ini
    # .env
    DATABASE_NAME=your_db_name
    DATABASE_USER=your_db_user
    DATABASE_PASSWORD=your_db_password
    DATABASE_HOST=localhost
    DATABASE_PORT=5432
    SECRET_KEY=your_django_secret_key_here # Tạo một key ngẫu nhiên và mạnh
    DEBUG=True
    ```
    *Lưu ý:* `SECRET_KEY` phải là một chuỗi ký tự ngẫu nhiên và mạnh. Bạn có thể tạo bằng cách mở Python shell và chạy:
    ```python
    import os
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())
    ```

3.  **Chạy Migrations và tạo Superuser:**
    Đảm bảo bạn đang ở trong virtual environment và trong thư mục gốc của dự án.
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```
    Làm theo hướng dẫn để tạo tài khoản admin.

## 7. Chạy ứng dụng

```bash
python manage.py runserver
```

Ứng dụng sẽ chạy tại `http://127.0.0.1:8000/`. Bạn có thể truy cập trang admin tại `http://127.0.0.1:8000/admin/` với tài khoản superuser vừa tạo.

Chúc mừng! Bạn đã thiết lập thành công môi trường phát triển cho dự án Website Tin tức Tự động.

---

**Tác giả:** Manus AI
**Ngày:** 07/10/2025
