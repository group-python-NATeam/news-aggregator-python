# news_app/migrations/0002_seed_initial_data.py
from django.db import migrations
from django.utils.text import slugify

# Danh sách dữ liệu ban đầu ĐÚNG THEO SPEC
CATEGORIES = ["Công nghệ", "Kinh tế", "Giáo dục", "Giải trí", "Sức khỏe", "Thể thao", "Pháp luật", "Xã hội"]
SOURCES = [
    {"name": "VnExpress", "base_url": "https://vnexpress.net"},
    {"name": "Dân Trí", "base_url": "https://dantri.com.vn"},
    {"name": "Tuổi Trẻ", "base_url": "https://tuoitre.vn"},
    {"name": "Thanh Niên", "base_url": "https://thanhnien.vn"}
]

def seed_data(apps, schema_editor):
    Category = apps.get_model('news_app', 'Category')
    Source = apps.get_model('news_app', 'Source')

    for category_name in CATEGORIES:
        Category.objects.get_or_create(name=category_name, defaults={'slug': slugify(category_name)})

    for source_info in SOURCES:
        Source.objects.get_or_create(name=source_info["name"], defaults={'base_url': source_info["base_url"]})

def reverse_seed_data(apps, schema_editor):
    Category = apps.get_model('news_app', 'Category')
    Source = apps.get_model('news_app', 'Source')
    
    Category.objects.filter(name__in=CATEGORIES).delete()
    Source.objects.filter(name__in=[s['name'] for s in SOURCES]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('news_app', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_data, reverse_code=reverse_seed_data),
    ]
