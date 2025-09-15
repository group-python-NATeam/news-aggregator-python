# Placeholder for Tuổi Trẻ crawler
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Crawl articles from Tuổi Trẻ'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Tuổi Trẻ crawler is not implemented yet.'))
