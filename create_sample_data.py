#!/usr/bin/env python
"""
Create sample data for the news aggregator to test the UI
"""
import os
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_agg_project.settings')
django.setup()

from news_app.models import Article, Category, Source

def create_sample_data():
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
            print(f"Created category: {category.name}")
    
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
            print(f"Created source: {source.name}")
    
    # Sample article data
    sample_articles = [
        {
            'title': 'Revolutionary AI Technology Changes Everything in Tech Industry',
            'summary': 'A groundbreaking artificial intelligence technology has been unveiled that promises to revolutionize the way we interact with computers. This new development could change the entire landscape of technology. Industry experts are calling it the most significant breakthrough in decades.',
            'image_url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800',
            'category': 'technology'
        },
        {
            'title': 'Global Climate Summit Reaches Historic Agreement on Carbon Reduction',
            'summary': 'World leaders have reached a landmark agreement on carbon emission reduction targets at the global climate summit. The accord represents the most ambitious environmental commitment ever made by participating nations. Environmental groups are praising the comprehensive nature of the agreement.',
            'image_url': 'https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3?w=800',
            'category': 'politics'
        },
        {
            'title': 'Championship Finals Break All-Time Viewership Records',
            'summary': 'The championship finals have shattered all previous television viewership records with over 100 million viewers worldwide. The thrilling match kept audiences on the edge of their seats for the entire duration. Sports analysts are calling it one of the greatest games ever played.',
            'image_url': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800',
            'category': 'sports'
        },
        {
            'title': 'Hollywood Blockbuster Breaks Box Office Records in Opening Weekend',
            'summary': 'The latest Hollywood blockbuster has broken all box office records in its opening weekend, earning over $200 million globally. Audiences and critics alike are praising the film for its innovative storytelling and spectacular visual effects. The movie is being hailed as a cinematic masterpiece.',
            'image_url': 'https://images.unsplash.com/photo-1489599316546-1c617e65ce23?w=800',
            'category': 'entertainment'
        },
        {
            'title': 'Major Tech Company Announces Trillion-Dollar Market Valuation',
            'summary': 'A leading technology company has reached a historic milestone by achieving a trillion-dollar market valuation for the first time. This achievement reflects strong investor confidence in the company\'s future growth prospects. Market analysts predict continued growth in the tech sector.',
            'image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
            'category': 'business'
        },
        {
            'title': 'Breakthrough Medical Research Offers Hope for Rare Disease Treatment',
            'summary': 'Scientists have made a significant breakthrough in medical research that could lead to new treatments for rare diseases. The research team has identified a novel therapeutic approach that shows promising results in early trials. Patients and families affected by these conditions are expressing cautious optimism.',
            'image_url': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800',
            'category': 'technology'
        },
        {
            'title': 'International Trade Agreement Signed Between Major Economic Powers',
            'summary': 'A comprehensive trade agreement has been signed between several major economic powers, promising to boost global commerce and economic growth. The deal includes provisions for reduced tariffs and improved market access. Economists predict significant positive impacts on international trade.',
            'image_url': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800',
            'category': 'business'
        },
        {
            'title': 'Olympic Games Preparation Enters Final Phase with Spectacular Ceremonies Planned',
            'summary': 'Preparations for the upcoming Olympic Games have entered their final phase with organizers announcing spectacular opening and closing ceremonies. Athletes from around the world are arriving for final training sessions. The games promise to be one of the most memorable Olympic events in history.',
            'image_url': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800',
            'category': 'sports'
        }
    ]
    
    # Create articles
    for i, article_data in enumerate(sample_articles):
        category = Category.objects.get(slug=article_data['category'])
        source = random.choice(Source.objects.all())
        
        # Create unique URL and content hash
        original_url = f"https://example.com/article-{i+1}"
        content_hash = f"hash_{i+1}_{random.randint(1000, 9999)}"
        
        publication_date = datetime.now() - timedelta(hours=random.randint(1, 72))
        
        article, created = Article.objects.get_or_create(
            original_url=original_url,
            defaults={
                'title': article_data['title'],
                'content_hash': content_hash,
                'cleaned_content': article_data['summary'] * 3,  # Make it longer
                'summary': article_data['summary'],
                'image_url': article_data['image_url'],
                'publication_date': publication_date,
                'category': category,
                'source': source
            }
        )
        
        if created:
            print(f"Created article: {article.title[:50]}...")
    
    print(f"\nSample data creation completed!")
    print(f"Total articles: {Article.objects.count()}")
    print(f"Total categories: {Category.objects.count()}")
    print(f"Total sources: {Source.objects.count()}")

if __name__ == "__main__":
    create_sample_data()
