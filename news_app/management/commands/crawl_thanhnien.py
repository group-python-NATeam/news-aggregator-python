import time
import re
import hashlib
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime

from news_app.crawler_config import CRAWLER_CONFIGS
from news_app.models import Article, Category, Source
from news_app.tasks import classify_article_task

logger = logging.getLogger('crawler')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Crawler; +https://example.local) Django-requests",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class Command(BaseCommand):
    help = "Crawl Thanh Niên by category slug and store articles."

    def add_arguments(self, parser):
        parser.add_argument("category_slug", type=str, help="e.g., cong-nghe")
        parser.add_argument("--limit", type=int, default=10, help="number of articles to fetch")

    def handle(self, *args, **opts):
        src_key = "thanhnien"
        category_slug = opts["category_slug"]
        limit = int(opts["limit"])

        cfg = CRAWLER_CONFIGS.get(src_key)
        if not cfg:
            raise CommandError("Missing 'thanhnien' config in crawler_config.py")

        cat_url = cfg["categories"].get(category_slug)
        if not cat_url:
            raise CommandError(f"Unknown category slug '{category_slug}'. Check crawler_config.py.")

        logger.info(f'Bắt đầu crawl {src_key} chuyên mục "{category_slug}" (URL: {cat_url}) với giới hạn {limit} bài...')
        list_urls = self._collect_article_links(cat_url, limit)
        logger.info(f'Tìm thấy {len(list_urls)} bài báo tiềm năng trên trang chuyên mục.')

        source_obj, _ = Source.objects.get_or_create(name="Thanh Niên", defaults={"base_url": cfg["base_url"]})
        # Remove manual category lookup - will use AI prediction instead

        created_count = 0
        for url in list_urls[:limit]:
            try:
                data = self._parse_detail(url)
                if not data:
                    continue

                # Check for duplicate content by content_hash
                content_hash = data["content_hash"]
                if Article.objects.filter(original_url=url).exists():
                    logger.warning(f'Bài báo đã tồn tại (URL): {url}')
                    time.sleep(0.5)
                    continue
                
                if Article.objects.filter(content_hash=content_hash).exists():
                    existing_article = Article.objects.get(content_hash=content_hash)
                    logger.warning(f"DUPLICATE content detected, skipping: {data['title'][:50]}... (original: {existing_article.original_url})")
                    time.sleep(0.5)
                    continue


                article, created = Article.objects.update_or_create(
                    original_url=url,
                    defaults={
                        'title': data["title"],
                        'publication_date': data["publication_date"],
                        'cleaned_content': data["content"],
                        'content_hash': content_hash,
                        'image_url': data.get("image_url"),
                        'source': source_obj,
                        'category': None,  # IMPORTANT: leave None; classification is async
                    }
                )
                if created:
                    created_count += 1
                    logger.info(f"CREATED: {data['title'][:80]}")
                else:
                    logger.info(f"UPDATED: {data['title'][:80]}")

                # Dispatch the main async pipeline (classify -> then summarize via chaining)
                classify_article_task.delay(article.id)
                logger.info(f'✅ Dispatched main processing task for Article ID {article.id}.')

                # be polite
                time.sleep(0.6)
            except Exception as e:
                logger.error(f'Lỗi khi xử lý {url}: {e}', exc_info=True)

        logger.info(f'Hoàn thành! Đã tạo mới {created_count} bài báo.')

    def _collect_article_links(self, category_url, limit):
        """Collect article links from a category page."""
        try:
            resp = requests.get(category_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            links = []
            for a in soup.select("a.box-category-link-with-avatar"):
                href = a.get("href")
                if not href:
                    continue
                abs_url = urljoin(category_url, href)
                if abs_url not in links:
                    links.append(abs_url)
                if len(links) >= max(limit * 2, limit):
                    break
            return links
        except requests.RequestException as e:
            logger.error(f'Lỗi khi tải trang chuyên mục {category_url}: {e}', exc_info=True)
            return []

    def _parse_detail(self, url):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Title
            title_tag = soup.select_one("h1.detail-title")
            if not title_tag:
                logger.warning(f'Không tìm thấy tiêu đề cho bài báo: {url}')
                return None
            title = title_tag.get_text(strip=True)

            # Publish date
            pub_tag = soup.select_one('div[data-role="publishdate"]')
            pub_dt = self._parse_publish_date(pub_tag.get_text(" ", strip=True) if pub_tag else "")

            # Content
            content_div = soup.select_one("div.detail-content")
            content_text = ""
            if content_div:
                for tag in content_div.select("script, style, .ads, .advertisement"):
                    tag.decompose()
                paragraphs = [p.get_text(" ", strip=True) for p in content_div.find_all(["p", "li"]) if p.get_text(strip=True)]
                content_text = "\n".join(paragraphs).strip()
            else:
                logger.warning(f'Không tìm thấy nội dung cho bài báo: {url}')

            # Image URL
            image_url = None
            og = soup.find("meta", property="og:image")
            if og and og.get("content"):
                image_url = og["content"]
            if not image_url and content_div:
                img = content_div.find("img")
                if img and img.get("src"):
                    image_url = img["src"]

            content_hash = hashlib.sha256(content_text.encode('utf-8')).hexdigest()

            return {
                "title": title,
                "publication_date": pub_dt,
                "content": content_text,
                "content_hash": content_hash,
                "image_url": image_url,
            }
        except requests.RequestException as e:
            logger.error(f'Lỗi khi tải trang chi tiết {url}: {e}', exc_info=True)
            return None

    def _parse_publish_date(self, s):
        s = (s or "").strip()
        if not s:
            return timezone.now()

        try:
            # Try 'HH:MM DD/MM/YYYY'
            m = re.search(r"(?P<h>\d{1,2}):(?P<m>\d{2})\s+(?P<d>\d{1,2})/(?P<mo>\d{1,2})/(?P<y>\d{4})", s)
            if m:
                dt = datetime(
                    int(m.group("y")),
                    int(m.group("mo")),
                    int(m.group("d")),
                    int(m.group("h")),
                    int(m.group("m")),
                )
                return timezone.make_aware(dt) if timezone.is_naive(dt) else dt

            # Try 'DD/MM/YYYY'
            m = re.search(r"(?P<d>\d{1,2})/(?P<mo>\d{1,2})/(?P<y>\d{4})", s)
            if m:
                dt = datetime(int(m.group("y")), int(m.group("mo")), int(m.group("d")), 0, 0, 0)
                return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        except Exception as e:
            logger.error(f'Không thể parse ngày tháng "{s}": {e}')

        # Fallback: now
        return timezone.now()
