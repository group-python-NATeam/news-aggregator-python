import hashlib
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

# Import các model của bạn
from news_app.models import Article, Category, Source

class Command(BaseCommand):
    help = 'Crawl articles from VnExpress'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu crawl VnExpress...'))

        # Lấy hoặc tạo Source và Category mặc định
        # Trong thực tế, bạn sẽ có logic để xác định Category chính xác hơn
        source, _ = Source.objects.get_or_create(name='VnExpress', defaults={'base_url': 'https://vnexpress.net'})
        default_category, _ = Category.objects.get_or_create(name='Chưa phân loại', defaults={'slug': 'chua-phan-loai'})

        url_to_crawl = 'https://vnexpress.net'

        try:
            response = requests.get(url_to_crawl, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Lỗi khi tải trang chủ: {e}'))
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='item-news')
        self.stdout.write(f'Tìm thấy {len(articles)} bài báo tiềm năng trên trang chủ.')

        created_count = 0
        for article_tag in articles:
            title_tag = article_tag.find('h3', class_='title-news')
            if not title_tag or not title_tag.find('a'):
                continue

            link_tag = title_tag.find('a')
            relative_link = link_tag['href']
            absolute_link = urljoin(url_to_crawl, relative_link)

            # --- BƯỚC 1: KIỂM TRA TRÙNG LẶP URL ---
            if Article.objects.filter(original_url=absolute_link).exists():
                self.stdout.write(self.style.WARNING(f'Bài báo đã tồn tại (URL): {absolute_link}'))
                continue

            try:
                # --- BƯỚC 2: TRUY CẬP LINK CHI TIẾT ---
                self.stdout.write(f'Đang crawl trang chi tiết: {absolute_link}')
                detail_response = requests.get(absolute_link, timeout=10)
                detail_response.raise_for_status()
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                # --- BƯỚC 3: BÓC TÁCH NỘI DUNG CHI TIẾT ---
                title = detail_soup.find('h1', class_='title-detail').get_text(strip=True)
                
                # === THAY THẾ ĐOẠN CODE CŨ BẰNG ĐOẠN NÀY ===

                time_tag = detail_soup.find('span', class_='date')
                if not time_tag:
                    self.stderr.write(self.style.ERROR(f'Không tìm thấy thẻ thời gian cho bài báo: {absolute_link}'))
                    continue # Bỏ qua bài này

                date_text = time_tag.get_text(strip=True) # Ví dụ: "Thứ hai, 15/9/2025, 20:30 (GMT+7)" hoặc "Thứ hai, 15/9/2025"

                # Tách lấy phần ngày tháng, bỏ qua thứ và (GMT+7)
                date_str_part = date_text.split(', ')[1].replace(' (GMT+7)', '')

                publication_date = None
                # Thử khớp với định dạng có cả giờ và phút
                try:
                    publication_date = datetime.strptime(date_str_part, '%d/%m/%Y, %H:%M')
                except ValueError:
                    # Nếu thất bại, thử khớp với định dạng chỉ có ngày
                    try:
                        publication_date = datetime.strptime(date_str_part, '%d/%m/%Y')
                    except ValueError:
                        self.stderr.write(self.style.ERROR(f'Không thể xử lý định dạng ngày tháng: "{date_text}"'))
                        continue # Bỏ qua bài báo nếu không xử lý được ngày

                # Chuyển thành timezone-aware datetime
                aware_publication_date = make_aware(publication_date)

                # === KẾT THÚC PHẦN THAY THẾ ===

                article_content_tag = detail_soup.find('article', class_='fck_detail')
                
                # --- BƯỚC 4: LÀM SẠCH ---
                # Xóa các thành phần không mong muốn (quảng cáo, box liên quan...)
                for tag in article_content_tag.find_all(['figure', 'div', 'table']):
                    tag.decompose()
                cleaned_content = article_content_tag.get_text(separator='\n', strip=True)

                # --- BƯỚC 5: TẠO HASH ---
                content_hash = hashlib.sha256(cleaned_content.encode('utf-8')).hexdigest()

                # Kiểm tra trùng lặp hash
                if Article.objects.filter(content_hash=content_hash).exists():
                    self.stdout.write(self.style.WARNING(f'Bài báo đã tồn tại (hash): {absolute_link}'))
                    continue

                # --- BƯỚC 6: LƯU VÀO DATABASE ---
                Article.objects.create(
                    title=title,
                    original_url=absolute_link,
                    content_hash=content_hash,
                    cleaned_content=cleaned_content,
                    summary='',  # Sẽ được tạo ở Sprint sau
                    publication_date=aware_publication_date,
                    category=default_category,
                    source=source
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Đã lưu bài báo: {title}'))

            except requests.RequestException as e:
                self.stderr.write(self.style.ERROR(f'Lỗi khi crawl trang chi tiết {absolute_link}: {e}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Lỗi không xác định khi xử lý {absolute_link}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Hoàn thành! Đã tạo mới {created_count} bài báo.'))
