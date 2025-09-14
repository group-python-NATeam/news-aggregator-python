# Placeholder for Dân Trí crawler
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Crawl articles from Dân Trí'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Dân Trí crawler is not implemented yet.'))
