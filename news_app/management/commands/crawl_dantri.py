import hashlib
import logging
import time # ### THAY ĐỔI 1: IMPORT THƯ VIỆN TIME ###
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from news_app.models import Article, Category, Source
from news_app.crawler_config import CRAWLER_CONFIGS # ### THAY ĐỔI 1: Import config ###

logger = logging.getLogger('crawler')

def parse_publication_date(date_string: str) -> datetime:
    """
    Parses the date string from VnExpress.
    Example inputs: 
    - "Thứ sáu, 26/09/2025, 14:51"
    - "Thứ hai, 29/9/2025, 16:36 (GMT+7)"
    """
    # Tách chuỗi bằng dấu phẩy
    parts = date_string.split(',')

    # Kiểm tra xem có đủ 3 phần không (Thứ, Ngày, Giờ)
    if len(parts) < 3:
        raise ValueError(f"Date string '{date_string}' is not in the expected format.")

    # Nối phần ngày (index 1) và phần giờ (index 2) lại với nhau
    # .strip() để loại bỏ các khoảng trắng thừa
    datetime_part = f"{parts[1].strip()}, {parts[2].strip()}"
    
    # Xử lý múi giờ nếu có (ví dụ: +0700 hoặc (GMT+7))
    if '+' in datetime_part:
        # Xử lý trường hợp (GMT+7)
        if '(GMT' in datetime_part:
            datetime_part = datetime_part.split('(GMT')[0].strip()
        else:
            # Xử lý trường hợp +0700
            datetime_part = datetime_part.split('+')[0].strip()
    
    # Định dạng mong muốn bây giờ là "DD/MM/YYYY, HH:MM"
    expected_format = '%d/%m/%Y, %H:%M'
    
    # Parse chuỗi đã được định dạng đúng
    return datetime.strptime(datetime_part, expected_format)

class Command(BaseCommand):
    help = 'Crawl articles from VnExpress based on a standard category slug'

    def add_arguments(self, parser):
        # Tham số đầu vào vẫn là slug CHUẨN của hệ thống
        parser.add_argument('category_slug', type=str, help='The STANDARD category slug (e.g., kinh-te, cong-nghe)')
        parser.add_argument('--limit', type=int, default=10, help='Limits the number of articles to crawl')

    def handle(self, *args, **options):
        standard_slug = options['category_slug']
        limit = options['limit']

        # ### THAY ĐỔI 2: Lấy thông tin từ config ###
        SOURCE_NAME = "VnExpress"
        try:
            source_config = CRAWLER_CONFIGS[SOURCE_NAME]
            source_specific_slug = source_config["categories"][standard_slug]
            base_url = source_config["base_url"]
        except KeyError:
            logger.error(f'Không tìm thấy cấu hình cho slug "{standard_slug}" của báo {SOURCE_NAME}.')
            return

        logger.info(f'Bắt đầu crawl {SOURCE_NAME} chuyên mục "{standard_slug}" (slug thực tế: {source_specific_slug}) với giới hạn {limit} bài...')

        try:
            category = Category.objects.get(slug=standard_slug)
        except Category.DoesNotExist:
            logger.error(f'Category với slug="{standard_slug}" không tồn tại trong database.')
            return

        source, _ = Source.objects.get_or_create(name=SOURCE_NAME, defaults={'base_url': base_url})
        
        # ### THAY ĐỔI 3: Dựng URL từ slug thực tế ###
        url_to_crawl = f'{base_url}/{source_specific_slug}'
        
        # ### THAY ĐỔI 2: ĐỊNH NGHĨA CÁC THAM SỐ CHO RETRY ###
        MAX_RETRIES = 3
        RETRY_DELAY = 2 # Giây

        try:
            response = requests.get(url_to_crawl, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f'Lỗi khi tải trang chuyên mục {url_to_crawl}: {e}', exc_info=True)
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='item-news')
        logger.info(f'Tìm thấy {len(articles)} bài báo tiềm năng trên trang chuyên mục.')

        created_count = 0
        crawled_count = 0 # ### THAY ĐỔI 4: BIẾN ĐẾM ĐỂ SO SÁNH VỚI LIMIT ###
        
        for article_tag in articles:
            # Dừng lại nếu đã crawl đủ số lượng bài theo limit
            if crawled_count >= limit:
                logger.info(f'Đã đạt giới hạn {limit} bài. Dừng crawl.')
                break
            
            crawled_count += 1
            
            # ### THAY ĐỔI 3: THÊM SLEEP ĐỂ "LỊCH SỰ" ###
            time.sleep(0.5) # Dừng 0.5 giây trước mỗi lần crawl trang chi tiết

            title_tag = article_tag.find('h3', class_='title-news')
            if not title_tag or not title_tag.find('a'):
                continue

            link_tag = title_tag.find('a')
            relative_link = link_tag['href']
            absolute_link = urljoin(base_url, relative_link)

            if Article.objects.filter(original_url=absolute_link).exists():
                logger.warning(f'Bài báo đã tồn tại (URL): {absolute_link}')
                continue
            
            try:
                # ### THAY ĐỔI 4: LOGIC RETRY ###
                detail_response = None
                for attempt in range(MAX_RETRIES):
                    try:
                        logger.info(f'Đang crawl trang chi tiết: {absolute_link}')
                        detail_response = requests.get(absolute_link, timeout=10)
                        detail_response.raise_for_status() # Nếu có lỗi HTTP (4xx, 5xx), sẽ raise exception
                        break # Nếu thành công, thoát khỏi vòng lặp retry
                    except requests.RequestException as e:
                        logger.warning(f'Lỗi khi crawl {absolute_link} (lần {attempt + 1}/{MAX_RETRIES}): {e}')
                        if attempt + 1 < MAX_RETRIES:
                            time.sleep(RETRY_DELAY) # Chờ một chút trước khi thử lại
                        else:
                            logger.error(f'Thử lại {MAX_RETRIES} lần thất bại. Bỏ qua bài báo: {absolute_link}')
                            raise # Ném lại lỗi cuối cùng để được bắt bởi khối except bên ngoài

                # Nếu detail_response là None sau vòng lặp, nghĩa là có lỗi logic nào đó
                if not detail_response:
                    continue
                
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                title = detail_soup.find('h1', class_='title-detail').get_text(strip=True)
                
                time_tag = detail_soup.find('span', class_='date')
                if not time_tag:
                    logger.error(f'Không tìm thấy thẻ thời gian cho bài báo: {absolute_link}')
                    continue

                date_text = time_tag.get_text(strip=True)

                try:
                    publication_date = parse_publication_date(date_text)
                except (ValueError, IndexError) as e:
                    logger.error(f'Không thể xử lý định dạng ngày tháng: "{date_text}" - Lỗi: {e}')
                    continue

                aware_publication_date = make_aware(publication_date)

                article_content_tag = detail_soup.find('article', class_='fck_detail')
                
                for tag in article_content_tag.find_all(['figure', 'div', 'table']):
                    tag.decompose()
                cleaned_content = article_content_tag.get_text(separator='\n', strip=True)

                content_hash = hashlib.sha256(cleaned_content.encode('utf-8')).hexdigest()

                if Article.objects.filter(content_hash=content_hash).exists():
                    logger.warning(f'Bài báo đã tồn tại (hash): {absolute_link}')
                    continue

                # Extract image URL - prefer og:image meta tag
                image_url = None
                og_image = detail_soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    image_url = og_image.get('content')
                    logger.info(f'Found og:image: {image_url}')
                else:
                    # Fallback: get the first image in the article content
                    original_content_tag = detail_soup.find('article', class_='fck_detail')
                    if original_content_tag:
                        first_image = original_content_tag.find('img')
                        if first_image and first_image.get('src'):
                            image_url = first_image.get('src')
                            logger.info(f'Found first image: {image_url}')
                
                # Ensure image_url is absolute
                if image_url and not image_url.startswith(('http://', 'https://')):
                    image_url = urljoin(base_url, image_url)

                Article.objects.create(
                    title=title,
                    original_url=absolute_link,
                    content_hash=content_hash,
                    cleaned_content=cleaned_content,
                    summary='',
                    image_url=image_url,
                    publication_date=aware_publication_date,
                    category=category,  # ### THAY ĐỔI 5: GÁN ĐÚNG CATEGORY ĐÃ LẤY TỪ DB ###
                    source=source
                )
                created_count += 1
                logger.info(f'Đã lưu bài báo: {title}')

            except Exception as e:
                # Khối except này bây giờ sẽ bắt lỗi cuối cùng từ vòng lặp retry, hoặc các lỗi parse khác
                logger.error(f'Lỗi không xác định khi xử lý {absolute_link}: {e}', exc_info=True)
        
        logger.info(f'Hoàn thành! Đã tạo mới {created_count} bài báo.')
