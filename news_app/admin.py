from django.contrib import admin
from .models import Category, Source, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url')
    search_fields = ('name',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'category', 'publication_date', 'created_at')
    list_filter = ('source', 'category', 'publication_date')
    search_fields = ('title', 'cleaned_content')
    date_hierarchy = 'publication_date'
    ordering = ('-publication_date',)
