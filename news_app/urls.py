from django.urls import path
from . import views

app_name = 'news_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('category/<slug:category_slug>/', views.ArticleListView.as_view(), name='category_articles'),
    path('api/article/<int:article_id>/speak/', views.article_speak_view, name='article_speak'),
    path('api/articles/', views.article_api_view, name='article_api'),
]