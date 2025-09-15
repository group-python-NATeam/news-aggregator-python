from django.contrib import admin
from .models import Category, Source, Article

# Register your models here.
admin.site.register(Category)
admin.site.register(Source)
admin.site.register(Article)
