from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Source(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField(max_length=255)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.TextField()
    original_url = models.URLField(max_length=1024, unique=True)
    content_hash = models.CharField(max_length=64, unique=True)
    cleaned_content = models.TextField()
    summary = models.TextField()
    publication_date = models.DateTimeField()
    
    # Timestamps tự động
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Khóa ngoại (Foreign Keys)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='articles')

    def __str__(self):
        return self.title

    class Meta:
        # Sắp xếp bài báo theo ngày xuất bản giảm dần
        ordering = ['-publication_date']
