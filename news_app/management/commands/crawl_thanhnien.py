# Placeholder for Thanh Niên crawler
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Crawl articles from Thanh Niên'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Thanh Niên crawler is not implemented yet.'))
