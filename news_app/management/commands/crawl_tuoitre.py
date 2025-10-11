from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from datetime import datetime
import logging

from news_app.models import Article, Category, Source
from news_app.crawler_config import CRAWLER_CONFIGS

logger = logging.getLogger('crawler')

# Exact selectors from cheatsheet
TT_LINK_SELECTOR = "a.box-category-link-with-avatar"
TT_TITLE_SELECTOR = "h1.detail-title"  
TT_CONTENT_SELECTOR = "div.detail-content"
TT_IMAGE_SELECTOR_PRIMARY = 'meta[property="og:image"]'
TT_IMAGE_SELECTOR_FALLBACK = "div.detail-content img"
TT_DATE_SELECTOR = 'div[data-role="publishdate"]'  # FIXED by spec

DATE_FMT = "%d/%m/%Y %H:%M GMT%z"  # e.g., '09/10/2025 16:24 GMT+7'

class Command(BaseCommand):
    help = "Crawl Tuoi Tre by category slug (e.g., cong-nghe) and save Articles."

    def add_arguments(self, parser):
        parser.add_argument("category", type=str, help="Generic category slug (e.g. cong-nghe)")
        parser.add_argument("--limit", type=int, default=5, help="Max number of articles to fetch")

    def handle(self, *args, **options):
        category_slug = options["category"]
        limit = options["limit"]

        cfg = CRAWLER_CONFIGS.get("tuoitre")
        if not cfg:
            raise CommandError("Missing 'tuoitre' config in CRAWLER_CONFIGS.")

        base_url = cfg["base_url"].rstrip("/")
        cat_map = cfg.get("categories", {})
        if category_slug not in cat_map:
            raise CommandError(f"Unknown category '{category_slug}'. Known: {', '.join(cat_map.keys())}")

        category_path = cat_map[category_slug].lstrip("/")
        list_url = f"{base_url}/{category_path}"

        logger.info(f'Bắt đầu crawl tuoitre chuyên mục "{category_slug}" (slug thực tế: {category_path}) với giới hạn {limit} bài...')

        # Ensure Source and Category exist
        source_obj, _ = Source.objects.get_or_create(name="Tuổi Trẻ", defaults={'base_url': base_url})
        
        try:
            category_obj = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            logger.error(f'Category với slug="{category_slug}" không tồn tại trong database.')
            return

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (crawler; +https://example.local)"
        })

        # 1) Fetch listing and collect detail links
        try:
            resp = session.get(list_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f'Lỗi khi tải trang chuyên mục {list_url}: {e}', exc_info=True)
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.select(TT_LINK_SELECTOR):
            href = a.get("href")
            if not href:
                continue
            url = urljoin(base_url, href)
            links.append(url)

        # Deduplicate while preserving order
        seen = set()
        detail_links = []
        for u in links:
            if u not in seen:
                seen.add(u)
                detail_links.append(u)

        detail_links = detail_links[:max(0, limit)]
        logger.info(f'Tìm thấy {len(detail_links)} bài báo tiềm năng trên trang chuyên mục.')
        
        if not detail_links:
            logger.warning(f"[TUOITRE] No detail links found with selector {TT_LINK_SELECTOR}")
            return

        created_count = 0
        crawled_count = 0

        # 2) Visit each article detail
        for idx, url in enumerate(detail_links, start=1):
            crawled_count += 1
            
            # Be polite with delays
            if idx > 1:  # Skip delay for first request
                import time
                time.sleep(0.5)
            
            logger.info(f'[{idx}/{len(detail_links)}] Đang crawl trang chi tiết: {url}')
            
            if Article.objects.filter(original_url=url).exists():
                logger.warning(f'Bài báo đã tồn tại (URL): {url}')
                continue
                
            try:
                r = session.get(url, timeout=20)
                r.raise_for_status()
            except Exception as e:
                logger.warning(f"Lỗi khi crawl {url}: {e}")
                continue

            dsoup = BeautifulSoup(r.text, "html.parser")

            # Title using exact selector
            title_tag = dsoup.select_one(TT_TITLE_SELECTOR)
            title = title_tag.get_text(strip=True) if title_tag else None

            # Content using exact selector
            content_div = dsoup.select_one(TT_CONTENT_SELECTOR)
            if content_div:
                # Clean content by removing unwanted tags
                for tag in content_div.find_all(['script', 'style', 'figure', 'div.VCSortableInPreviewMode']):
                    tag.decompose()
                content_text = " ".join(content_div.stripped_strings)
            else:
                content_text = ""

            # Image URL - primary og:image, fallback to content img
            img_url = None
            # Try primary selector first
            og_img = dsoup.select_one(TT_IMAGE_SELECTOR_PRIMARY)
            if og_img and og_img.get("content"):
                img_url = og_img.get("content")
                logger.info(f'Found og:image: {img_url}')
            else:
                # Fallback selector
                img_tag = dsoup.select_one(TT_IMAGE_SELECTOR_FALLBACK)
                if img_tag and img_tag.get("src"):
                    img_url = urljoin(base_url, img_tag.get("src"))
                    logger.info(f'Found fallback image: {img_url}')

            # Ensure image_url is absolute
            if img_url and not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(base_url, img_url)

            # Publication datetime: text "dd/mm/YYYY HH:MM GMT+7"
            publication_date = None
            date_node = dsoup.select_one(TT_DATE_SELECTOR)
            if date_node:
                raw = date_node.get_text(strip=True)
                # Normalize common variants like "GMT+07:00" → "GMT+0700", "GMT+7" → "GMT+0700"
                raw_norm = raw.replace("GMT+07:00", "GMT+0700").replace("GMT+7", "GMT+0700").replace("GMT+08:00", "GMT+0800")
                try:
                    dt = datetime.strptime(raw_norm, DATE_FMT)
                    # dt is already timezone-aware from strptime with %z
                    publication_date = dt
                except Exception as e:
                    logger.warning(f"Failed to parse datetime '{raw}': {e}")

            if not title:
                logger.warning(f"Không tìm thấy tiêu đề cho bài báo: {url}")
                continue

            # Generate content hash for duplicate detection
            import hashlib
            content_hash = hashlib.sha256(content_text.encode('utf-8')).hexdigest()

            if Article.objects.filter(content_hash=content_hash).exists():
                logger.warning(f'Bài báo đã tồn tại (hash): {url}')
                continue

            try:
                Article.objects.create(
                    title=title,
                    original_url=url,
                    content_hash=content_hash,
                    cleaned_content=content_text,
                    summary='',
                    image_url=img_url,
                    publication_date=publication_date,
                    category=category_obj,
                    source=source_obj
                )
                created_count += 1
                logger.info(f'Đã lưu bài báo: {title}')
                
            except Exception as e:
                logger.error(f'Lỗi khi lưu bài báo {url}: {e}', exc_info=True)

        logger.info(f'Hoàn thành! Đã tạo mới {created_count} bài báo.')
