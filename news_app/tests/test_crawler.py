from django.test import TestCase
from datetime import datetime
from bs4 import BeautifulSoup
import hashlib
from unittest.mock import patch, MagicMock
from io import StringIO
from django.core.management import call_command
from django.utils.timezone import make_aware
import requests

from news_app.management.commands.crawl_vnexpress import parse_publication_date
from news_app.models import Article, Category, Source

class CrawlerCommandTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category, _ = Category.objects.get_or_create(name="Công nghệ", defaults={'slug': 'cong-nghe'})
        cls.source, _ = Source.objects.get_or_create(name="VnExpress", defaults={'base_url': 'https://vnexpress.net'})

    @patch('news_app.management.commands.crawl_vnexpress.requests.get')
    def test_crawl_vnexpress_command_success(self, mock_get):
        """
        Integration test: Kiểm tra toàn bộ command crawl_vnexpress chạy thành công.
        """
        mock_category_html = """
        <html>
        <body>
            <article class="item-news">
                <h3 class="title-news">
                    <a href="/test-article-url">Test Article Title</a>
                </h3>
            </article>
        </body>
        </html>
        """

        mock_detail_html = """
        <html>
        <body>
            <h1 class="title-detail">Test Article Title</h1>
            <span class="date">Thứ sáu, 26/09/2025, 14:51 (GMT+7)</span>
            <article class="fck_detail">
                <p>Đây là nội dung chính của bài báo test.</p>
                <p>Nội dung này được sử dụng để test integration test.</p>
            </article>
        </body>
        </html>
        """

        category_response = MagicMock(spec=requests.Response)
        category_response.status_code = 200
        category_response.text = mock_category_html
        category_response.raise_for_status = MagicMock()

        detail_response = MagicMock(spec=requests.Response)
        detail_response.status_code = 200
        detail_response.text = mock_detail_html
        detail_response.raise_for_status = MagicMock()

        mock_get.side_effect = [category_response, detail_response]

        out = StringIO()
        call_command('crawl_vnexpress', 'cong-nghe', limit=1, stdout=out)

        self.assertEqual(Article.objects.count(), 1)

        created_article = Article.objects.first()
        self.assertEqual(created_article.title, "Test Article Title")
        self.assertEqual(created_article.cleaned_content, "Đây là nội dung chính của bài báo test.\nNội dung này được sử dụng để test integration test.")
        self.assertEqual(created_article.category, self.category)
        self.assertEqual(created_article.source, self.source)

    @patch('news_app.management.commands.crawl_vnexpress.requests.get')
    def test_crawl_vnexpress_command_with_duplicate(self, mock_get):
        """
        Test khi có bài báo duplicate (cùng URL).
        """
        Article.objects.create(
            title="Existing Article",
            original_url="https://vnexpress.net/test-article-url",
            content_hash="dummy_hash",
            cleaned_content="Existing content",
            publication_date=make_aware(datetime.now()),
            category=self.category,
            source=self.source
        )

        mock_category_html = """
        <html>
        <body>
            <article class="item-news">
                <h3 class="title-news">
                    <a href="/test-article-url">Existing Article</a>
                </h3>
            </article>
        </body>
        </html>
        """

        category_response = MagicMock(spec=requests.Response)
        category_response.status_code = 200
        category_response.text = mock_category_html
        category_response.raise_for_status = MagicMock()

        mock_get.return_value = category_response

        call_command('crawl_vnexpress', 'cong-nghe', limit=1)

        self.assertEqual(Article.objects.count(), 1)

    @patch('news_app.management.commands.crawl_vnexpress.requests.get')
    def test_crawl_vnexpress_command_request_error(self, mock_get):
        """
        Test khi requests.get gặp lỗi.
        """
        mock_get.side_effect = requests.RequestException("Connection error")

        call_command('crawl_vnexpress', 'cong-nghe', limit=1)

        self.assertEqual(Article.objects.count(), 0)
