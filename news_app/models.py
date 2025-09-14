from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Source(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_url = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.TextField()
    original_url = models.TextField(unique=True)
    content_hash = models.CharField(max_length=64, unique=True)
    cleaned_content = models.TextField()
    summary = models.TextField(blank=True)
    publication_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='articles')

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['-publication_date']),
            models.Index(fields=['source', '-publication_date']),
        ]
        ordering = ['-publication_date']
