# Cơ chế Thu thập Dữ liệu (CRAWLER.md)

Phần này mô tả chi tiết về cách hệ thống thu thập dữ liệu từ các nguồn báo. Đây là một trong những thành phần cốt lõi của dự án, đảm bảo nguồn dữ liệu đầu vào luôn mới và chất lượng.

## 1. Tổng quan về Crawler

Crawler là một **Django Management Command**, cho phép chúng ta chạy các script thu thập dữ liệu trực tiếp từ dòng lệnh. Mỗi nguồn báo (VnExpress, Dân Trí, v.v.) sẽ có một command riêng, ví dụ: `crawl_vnexpress`, `crawl_dantri`.

### Luồng hoạt động chính của một Crawler:

1.  **Nhận lệnh:** Người dùng hoặc hệ thống tự động (GitHub Actions) gọi command với các tham số (ví dụ: chuyên mục, số lượng bài cần crawl).
2.  **Lấy cấu hình:** Crawler đọc file `news_app/crawler_config.py` để ánh xạ slug chuyên mục chuẩn của hệ thống (ví dụ: `cong-nghe`) sang slug thực tế của nguồn báo (ví dụ: `so-hoa` của VnExpress).
3.  **Crawl trang chuyên mục:** Tải HTML của trang chuyên mục tương ứng.
4.  **Phân tích danh sách bài viết:** Bóc tách các URL bài viết từ HTML của trang chuyên mục.
5.  **Crawl chi tiết từng bài viết:** Với mỗi URL, crawler sẽ:
    *   Kiểm tra trùng lặp URL trong database.
    *   Tải HTML của trang chi tiết bài viết.
    *   Bóc tách các thông tin cần thiết: tiêu đề, ngày xuất bản, nội dung, URL hình ảnh chính.
    *   Làm sạch nội dung HTML.
    *   Tạo hash từ nội dung đã làm sạch để kiểm tra trùng lặp nội dung.
    *   Lưu bài viết vào database.
6.  **Ghi log:** Toàn bộ quá trình được ghi lại trong file `logs/crawler.log` để dễ dàng theo dõi và gỡ lỗi.

## 2. Cấu trúc Code

### `news_app/management/commands/crawl_vnexpress.py`

Đây là file crawler mẫu, đã được hoàn thiện cho VnExpress. Các crawler khác sẽ được xây dựng dựa trên cấu trúc này.

```python
# news_app/management/commands/crawl_vnexpress.py

import hashlib
import logging
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from news_app.crawler_config import CRAWLER_CONFIGS
from news_app.models import Article, Category, Source

logger = logging.getLogger('crawler')

class Command(BaseCommand):
    help = 'Crawl articles from VnExpress for a specific category'

    def add_arguments(self, parser):
        parser.add_argument('category_slug', type=str, help='The slug of the category to crawl')
        parser.add_argument('--limit', type=int, default=10, help='The maximum number of articles to crawl')

    def handle(self, *args, **options):
        category_slug = options['category_slug']
        limit = options['limit']

        # ... (logic xử lý chi tiết)
```

**Các thành phần chính:**

*   **`add_arguments()`:** Định nghĩa các tham số dòng lệnh mà command có thể nhận (`category_slug`, `limit`).
*   **`handle()`:** Hàm chính thực thi logic của crawler.
*   **Logging:** Sử dụng `logging.getLogger('crawler')` để ghi log vào file đã được cấu hình trong `settings.py`.
*   **Retry Logic:** Sử dụng vòng lặp `for _ in range(3)` và `time.sleep()` để thử lại khi gặp lỗi mạng, giúp crawler hoạt động bền bỉ hơn.
*   **Làm sạch HTML:** Sử dụng `BeautifulSoup` để loại bỏ các thẻ không cần thiết (figure, div, table) khỏi nội dung bài viết.
*   **Kiểm tra trùng lặp:**
    *   **URL:** Dùng `Article.objects.filter(original_url=article_url).exists()`.
    *   **Nội dung:** Tạo hash SHA-256 từ nội dung đã làm sạch và kiểm tra `Article.objects.filter(content_hash=content_hash).exists()`.

### `news_app/crawler_config.py`

File này chứa dictionary `CRAWLER_CONFIGS` để ánh xạ các chuyên mục. Đây là một phần rất quan trọng để crawler có thể hoạt động linh hoạt với nhiều nguồn báo khác nhau.

```python
# news_app/crawler_config.py

CRAWLER_CONFIGS = {
    'vnexpress': {
        'base_url': 'https://vnexpress.net',
        'categories': {
            'cong-nghe': 'so-hoa',
            'kinh-te': 'kinh-doanh',
            # ... các chuyên mục khác
        }
    },
    'dantri': {
        'base_url': 'https://dantri.com.vn',
        'categories': {
            'cong-nghe': 'suc-manh-so',
            # ... các chuyên mục khác
        }
    },
    # ... các nguồn báo khác
}
```

## 3. Hướng dẫn Phát triển Crawler cho Nguồn báo mới

Khi phát triển crawler cho một nguồn báo mới (ví dụ: `crawl_dantri.py`), bạn cần thực hiện các bước sau:

1.  **Tạo file command mới:**
    Copy file `crawl_vnexpress.py` thành `crawl_dantri.py` và đổi tên class `Command`.

2.  **Cập nhật `crawler_config.py`:**
    Thêm cấu hình cho `dantri` vào `CRAWLER_CONFIGS`, bao gồm `base_url` và ánh xạ các chuyên mục.

3.  **Phân tích cấu trúc HTML của nguồn báo mới:**
    Đây là bước quan trọng nhất. Bạn cần dùng trình duyệt (Developer Tools) để kiểm tra cấu trúc HTML của trang chuyên mục và trang chi tiết bài viết của Dân Trí để xác định các CSS selector chính xác cho:
    *   Danh sách các thẻ `<a>` chứa link bài viết trên trang chuyên mục.
    *   Thẻ chứa tiêu đề bài viết.
    *   Thẻ chứa ngày xuất bản.
    *   Thẻ chứa nội dung chính của bài viết.
    *   Thẻ chứa URL hình ảnh chính.

4.  **Cập nhật các CSS selector trong code:**
    Thay thế các CSS selector của VnExpress bằng các selector mới bạn vừa tìm được cho Dân Trí.

5.  **Xử lý định dạng ngày tháng (nếu cần):**
    Mỗi báo có thể có định dạng ngày tháng khác nhau. Bạn có thể cần viết một hàm `parse_publication_date()` riêng để xử lý định dạng của Dân Trí.

6.  **Kiểm tra và gỡ lỗi:**
    Chạy command với một `limit` nhỏ để kiểm tra:
    ```bash
    python manage.py crawl_dantri cong-nghe --limit=1
    ```
    Kiểm tra log và dữ liệu trong database để đảm bảo crawler hoạt động chính xác.

## 4. Tự động hóa Crawler với GitHub Actions

Để dữ liệu luôn mới, chúng ta sẽ sử dụng GitHub Actions để tự động chạy các crawler theo lịch trình (ví dụ: mỗi 3 giờ).

Một file workflow `.github/workflows/crawler.yml` sẽ được tạo để thực hiện việc này. File này sẽ định nghĩa các công việc (jobs) để chạy các command crawler trên một server ảo.

```yaml
# .github/workflows/crawler.yml (ví dụ)

name: Scheduled Crawlers

on:
  schedule:
    - cron: '0 */3 * * *' # Chạy mỗi 3 giờ

jobs:
  crawl:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run VnExpress Crawler
      run: |
        python manage.py crawl_vnexpress cong-nghe --limit=20
        python manage.py crawl_vnexpress kinh-te --limit=20
        # ... các chuyên mục khác

    - name: Run DanTri Crawler
      run: |
        python manage.py crawl_dantri cong-nghe --limit=20
        # ... các chuyên mục khác
```

---

**Tác giả:** Manus AI
**Ngày:** 07/10/2025
