from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import random
from news_app.models import Article, Category, Source


class Command(BaseCommand):
    help = 'Create sample data for testing the TikTok-style news aggregator'

    def handle(self, *args, **options):
        # Create categories
        categories = [
            {'name': 'Technology', 'slug': 'technology'},
            {'name': 'Politics', 'slug': 'politics'}, 
            {'name': 'Sports', 'slug': 'sports'},
            {'name': 'Entertainment', 'slug': 'entertainment'},
            {'name': 'Business', 'slug': 'business'}
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created category: {category.name}")
                )
        
        # Create sources
        sources = [
            {'name': 'TechNews', 'base_url': 'https://technews.com'},
            {'name': 'NewsDaily', 'base_url': 'https://newsdaily.com'},
            {'name': 'SportsTimes', 'base_url': 'https://sportstimes.com'},
            {'name': 'BusinessWorld', 'base_url': 'https://businessworld.com'}
        ]
        
        for source_data in sources:
            source, created = Source.objects.get_or_create(
                name=source_data['name'],
                defaults={'base_url': source_data['base_url']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created source: {source.name}")
                )
        
        # Expanded sample article data for smoother scrolling experience
        sample_articles = [
            # Most recent articles (within 24 hours)
            {
                'title': 'Breaking: Revolutionary AI Technology Changes Everything in Tech Industry',
                'summary': 'A groundbreaking artificial intelligence technology has been unveiled that promises to revolutionize the way we interact with computers. This new development could change the entire landscape of technology. Industry experts are calling it the most significant breakthrough in decades.',
                'image_url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800',
                'category': 'technology',
                'hours_ago': 2
            },
            {
                'title': 'Global Climate Summit Reaches Historic Agreement on Carbon Reduction',
                'summary': 'World leaders have reached a landmark agreement on carbon emission reduction targets at the global climate summit. The accord represents the most ambitious environmental commitment ever made by participating nations. Environmental groups are praising the comprehensive nature of the agreement.',
                'image_url': 'https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3?w=800',
                'category': 'politics',
                'hours_ago': 4
            },
            {
                'title': 'Championship Finals Break All-Time Viewership Records',
                'summary': 'The championship finals have shattered all previous television viewership records with over 100 million viewers worldwide. The thrilling match kept audiences on the edge of their seats for the entire duration. Sports analysts are calling it one of the greatest games ever played.',
                'image_url': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800',
                'category': 'sports',
                'hours_ago': 6
            },
            {
                'title': 'Hollywood Blockbuster Breaks Box Office Records in Opening Weekend',
                'summary': 'The latest Hollywood blockbuster has broken all box office records in its opening weekend, earning over $200 million globally. Audiences and critics alike are praising the film for its innovative storytelling and spectacular visual effects. The movie is being hailed as a cinematic masterpiece.',
                'image_url': 'https://images.unsplash.com/photo-1489599316546-1c617e65ce23?w=800',
                'category': 'entertainment',
                'hours_ago': 8
            },
            {
                'title': 'Major Tech Company Announces Trillion-Dollar Market Valuation',
                'summary': 'A leading technology company has reached a historic milestone by achieving a trillion-dollar market valuation for the first time. This achievement reflects strong investor confidence in the company\'s future growth prospects. Market analysts predict continued growth in the tech sector.',
                'image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
                'category': 'business',
                'hours_ago': 10
            },
            {
                'title': 'Breakthrough Medical Research Offers Hope for Rare Disease Treatment',
                'summary': 'Scientists have made a significant breakthrough in medical research that could lead to new treatments for rare diseases. The research team has identified a novel therapeutic approach that shows promising results in early trials. Patients and families affected by these conditions are expressing cautious optimism.',
                'image_url': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800',
                'category': 'technology',
                'hours_ago': 12
            },
            {
                'title': 'International Trade Agreement Signed Between Major Economic Powers',
                'summary': 'A comprehensive trade agreement has been signed between several major economic powers, promising to boost global commerce and economic growth. The deal includes provisions for reduced tariffs and improved market access. Economists predict significant positive impacts on international trade.',
                'image_url': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800',
                'category': 'business',
                'hours_ago': 14
            },
            {
                'title': 'Olympic Games Preparation Enters Final Phase with Spectacular Ceremonies Planned',
                'summary': 'Preparations for the upcoming Olympic Games have entered their final phase with organizers announcing spectacular opening and closing ceremonies. Athletes from around the world are arriving for final training sessions. The games promise to be one of the most memorable Olympic events in history.',
                'image_url': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800',
                'category': 'sports',
                'hours_ago': 16
            },
            # Additional articles for smooth scrolling
            {
                'title': 'Electric Vehicle Sales Surge 300% as Battery Technology Improves',
                'summary': 'Electric vehicle sales have experienced unprecedented growth with a 300% increase over the past year. Advanced battery technology and expanding charging infrastructure are driving consumer adoption. Automotive industry analysts predict electric vehicles will dominate the market within the next decade.',
                'image_url': 'https://images.unsplash.com/photo-1593941707882-a5bac6861d75?w=800',
                'category': 'technology',
                'hours_ago': 18
            },
            {
                'title': 'Space Tourism Company Successfully Completes First Commercial Flight',
                'summary': 'A pioneering space tourism company has completed its first successful commercial flight with civilian passengers. The milestone marks a new era in space exploration and commercial space travel. Industry experts believe this achievement will accelerate the development of the space tourism sector.',
                'image_url': 'https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=800',
                'category': 'technology',
                'hours_ago': 20
            },
            {
                'title': 'Renewable Energy Initiative Powers Entire City for 30 Days Straight',
                'summary': 'A major city has successfully operated entirely on renewable energy for 30 consecutive days, setting a new world record. The achievement demonstrates the viability of sustainable energy solutions for urban environments. Environmental advocates are hailing this as a blueprint for global climate action.',
                'image_url': 'https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=800',
                'category': 'politics',
                'hours_ago': 22
            },
            {
                'title': 'Gaming Championship Prize Pool Reaches Record-Breaking $50 Million',
                'summary': 'The world\'s largest gaming championship has announced a record-breaking prize pool of $50 million for this year\'s tournament. Professional esports athletes from around the globe are preparing for the most lucrative gaming competition in history. The event is expected to attract millions of viewers worldwide.',
                'image_url': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800',
                'category': 'entertainment',
                'hours_ago': 24
            },
            {
                'title': 'New Archaeological Discovery Reveals Ancient Civilization Secrets',
                'summary': 'Archaeologists have uncovered remarkable artifacts that shed new light on an ancient civilization previously unknown to modern science. The discovery includes advanced tools and structures that challenge our understanding of historical technological development. Researchers are calling it one of the most significant archaeological finds of the century.',
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800',
                'category': 'technology',
                'hours_ago': 26
            },
            {
                'title': 'Cryptocurrency Market Experiences Unprecedented Stability Period',
                'summary': 'The volatile cryptocurrency market has entered an unusual period of stability, with major digital currencies maintaining steady values for several weeks. Financial analysts are studying this phenomenon to understand the factors contributing to reduced volatility. Institutional investors are showing renewed confidence in digital asset markets.',
                'image_url': 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800',
                'category': 'business',
                'hours_ago': 28
            },
            {
                'title': 'Revolutionary Food Production Method Could End World Hunger',
                'summary': 'Scientists have developed a revolutionary food production method that could potentially address global hunger issues. The innovative technique produces nutritious food using minimal resources and space. Agricultural experts believe this breakthrough could transform food security worldwide.',
                'image_url': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=800',
                'category': 'technology',
                'hours_ago': 30
            },
            {
                'title': 'International Music Festival Announces Star-Studded Lineup',
                'summary': 'The world\'s most anticipated music festival has revealed its star-studded lineup featuring top artists from multiple genres. The three-day event promises to be the biggest entertainment spectacle of the year. Tickets are expected to sell out within hours of going on sale.',
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800',
                'category': 'entertainment',
                'hours_ago': 32
            },
            {
                'title': 'Professional Athletes Unite for Global Mental Health Campaign',
                'summary': 'Top professional athletes from various sports have joined forces to launch a comprehensive mental health awareness campaign. The initiative aims to destigmatize mental health issues in sports and provide resources for athletes at all levels. The campaign has already received support from major sporting organizations worldwide.',
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800',
                'category': 'sports',
                'hours_ago': 34
            },
            {
                'title': 'Small Business Innovation Program Receives Billion-Dollar Investment',
                'summary': 'A groundbreaking small business innovation program has secured a billion-dollar investment from major corporations and government agencies. The initiative will provide funding and resources to promising startups and entrepreneurs. Economic experts predict this program will create thousands of jobs and drive technological innovation.',
                'image_url': 'https://images.unsplash.com/photo-1556155092-490a1ba16284?w=800',
                'category': 'business',
                'hours_ago': 36
            }
        ]
        
        # Delete existing articles first
        Article.objects.all().delete()
        
        # Create articles with proper time-based ordering
        for i, article_data in enumerate(sample_articles):
            category = Category.objects.get(slug=article_data['category'])
            source = random.choice(Source.objects.all())
            
            # Create unique URL and content hash
            original_url = f'https://example.com/article-{i+1}'
            content_hash = f'hash_{i+1}_{random.randint(1000, 9999)}'
            
            # Use the specified hours_ago for realistic publication dates
            publication_date = datetime.now() - timedelta(hours=article_data['hours_ago'])
            
            article = Article.objects.create(
                title=article_data['title'],
                original_url=original_url,
                content_hash=content_hash,
                cleaned_content=article_data['summary'] * 3,  # Make it longer
                summary=article_data['summary'],
                image_url=article_data['image_url'],
                publication_date=publication_date,
                category=category,
                source=source
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"Created article: {article.title[:50]}...")
            )
        
        self.stdout.write(
            self.style.SUCCESS(f"\nSample data creation completed!")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total articles: {Article.objects.count()}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total categories: {Category.objects.count()}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total sources: {Source.objects.count()}")
        )
