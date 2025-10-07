from django.urls import path
from . import views

app_name = 'news_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('category/<slug:category_slug>/', views.ArticleListView.as_view(), name='category_articles'),
]
