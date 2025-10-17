import hashlib
import logging
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from news_app.models import Article, Category, Source
from news_app.crawler_config import CRAWLER_CONFIGS
from news_app.tasks import classify_article_task

logger = logging.getLogger('crawler')

def parse_publication_date(date_string: str) -> datetime:
    """
    Parses the date string from Dân Trí.
    Expected format: "2025-10-10 14:51"
    """
    try:
        # Parse datetime string in format: YYYY-MM-DD HH:MM
        return datetime.strptime(date_string, '%Y-%m-%d %H:%M')
    except ValueError as e:
        logger.error(f'Invalid date format: "{date_string}" - Error: {e}')
        raise

class Command(BaseCommand):
    help = 'Crawl articles from Dân Trí based on a standard category slug'

    def add_arguments(self, parser):
        parser.add_argument('category_slug', type=str, help='The STANDARD category slug (e.g., kinh-te, cong-nghe)')
        parser.add_argument('--limit', type=int, default=10, help='Limits the number of articles to crawl')

    def handle(self, *args, **options):
        standard_slug = options['category_slug']
        limit = options['limit']

        # Get configuration from config
        SOURCE_NAME = "dantri"
        try:
            source_config = CRAWLER_CONFIGS[SOURCE_NAME]
            source_specific_slug = source_config["categories"][standard_slug]
            base_url = source_config["base_url"]
        except KeyError:
            logger.error(f'Không tìm thấy cấu hình cho slug "{standard_slug}" của báo {SOURCE_NAME}.')
            return

        logger.info(f'Bắt đầu crawl {SOURCE_NAME} chuyên mục "{standard_slug}" (slug thực tế: {source_specific_slug}) với giới hạn {limit} bài...')

        # Remove manual category lookup - will use AI prediction instead

        # Use a desktop-like User-Agent to reduce 403/404 due to blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        source, _ = Source.objects.get_or_create(name="Dân Trí", defaults={'base_url': base_url})
        
        # Build URL from actual slug
        url_to_crawl = f'{base_url}/{source_specific_slug}'
        
        # Retry parameters
        MAX_RETRIES = 3
        RETRY_DELAY = 2  # seconds

        try:
            response = requests.get(url_to_crawl, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f'Lỗi khi tải trang chuyên mục {url_to_crawl}: {e}', exc_info=True)
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Use Dân Trí specific selector: div.article-thumb a
        article_links = soup.select('div.article-thumb a')
        logger.info(f'Tìm thấy {len(article_links)} bài báo tiềm năng trên trang chuyên mục.')

        created_count = 0
        crawled_count = 0
        
        for link_tag in article_links:
            # Stop if we've reached the limit
            if crawled_count >= limit:
                logger.info(f'Đã đạt giới hạn {limit} bài. Dừng crawl.')
                break
            
            crawled_count += 1
            
            # Be polite with delays
            time.sleep(0.5)

            relative_link = link_tag.get('href')
            if not relative_link:
                continue
                
            absolute_link = urljoin(base_url, relative_link)

            if Article.objects.filter(original_url=absolute_link).exists():
                logger.warning(f'Bài báo đã tồn tại (URL): {absolute_link}')
                continue
            
            try:
                # Retry logic for detail page
                detail_response = None
                for attempt in range(MAX_RETRIES):
                    try:
                        logger.info(f'Đang crawl trang chi tiết: {absolute_link}')
                        detail_response = requests.get(absolute_link, headers=headers, timeout=10)
                        detail_response.raise_for_status()
                        break
                    except requests.RequestException as e:
                        logger.warning(f'Lỗi khi crawl {absolute_link} (lần {attempt + 1}/{MAX_RETRIES}): {e}')
                        if attempt + 1 < MAX_RETRIES:
                            time.sleep(RETRY_DELAY)
                        else:
                            logger.error(f'Thử lại {MAX_RETRIES} lần thất bại. Bỏ qua bài báo: {absolute_link}')
                            raise

                if not detail_response:
                    continue
                
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                # Extract title using Dân Trí selector: h1.title-page
                title_tag = detail_soup.select_one('h1.title-page')
                if not title_tag:
                    logger.error(f'Không tìm thấy tiêu đề cho bài báo: {absolute_link}')
                    continue
                
                title = title_tag.get_text(strip=True)
                
                # Extract publication date using Dân Trí selector: time.author-time datetime attribute
                time_tag = detail_soup.select_one('time.author-time')
                if not time_tag or not time_tag.get('datetime'):
                    logger.error(f'Không tìm thấy thẻ thời gian cho bài báo: {absolute_link}')
                    continue

                date_text = time_tag.get('datetime')

                try:
                    publication_date = parse_publication_date(date_text)
                except (ValueError, IndexError) as e:
                    logger.error(f'Không thể xử lý định dạng ngày tháng: "{date_text}" - Lỗi: {e}')
                    continue

                aware_publication_date = make_aware(publication_date)

                # Extract content using Dân Trí selector: div.singular-content
                article_content_tag = detail_soup.select_one('div.singular-content')
                if not article_content_tag:
                    logger.error(f'Không tìm thấy nội dung bài báo: {absolute_link}')
                    continue
                
                # Clean content by removing unwanted tags
                for tag in article_content_tag.find_all(['figure', 'div', 'table', 'script', 'style']):
                    tag.decompose()
                
                # Get text using stripped_strings as specified
                cleaned_content = '\n'.join(article_content_tag.stripped_strings)

                content_hash = hashlib.sha256(cleaned_content.encode('utf-8')).hexdigest()

                if Article.objects.filter(content_hash=content_hash).exists():
                    logger.warning(f'Bài báo đã tồn tại (hash): {absolute_link}')
                    continue

                # Extract image URL using Dân Trí selector: figure.image img
                image_url = None
                img_tag = detail_soup.select_one('figure.image img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    logger.info(f'Found figure image: {image_url}')
                else:
                    # Fallback: try og:image meta tag
                    og_image = detail_soup.find('meta', property='og:image')
                    if og_image and og_image.get('content'):
                        image_url = og_image.get('content')
                        logger.info(f'Found og:image: {image_url}')
                
                # Ensure image_url is absolute with urljoin as specified
                if image_url and not image_url.startswith(('http://', 'https://')):
                    image_url = urljoin(base_url, image_url)


                article, created = Article.objects.update_or_create(
                    original_url=absolute_link,
                    defaults={
                        'title': title,
                        'publication_date': aware_publication_date,
                        'cleaned_content': cleaned_content,
                        'content_hash': content_hash,
                        'image_url': image_url,
                        'source': source,
                        'category': None,  # IMPORTANT: leave None; classification is async
                    }
                )
                if created:
                    created_count += 1
                    logger.info(f"CREATED: {title}")
                else:
                    logger.info(f"UPDATED: {title}")

                # Dispatch the main async pipeline (classify -> then summarize via chaining)
                classify_article_task.delay(article.id)
                logger.info(f'✅ Dispatched main processing task for Article ID {article.id}.')

            except Exception as e:
                logger.error(f'Lỗi không xác định khi xử lý {absolute_link}: {e}', exc_info=True)
        
        logger.info(f'Hoàn thành! Đã tạo mới {created_count} bài báo.')
