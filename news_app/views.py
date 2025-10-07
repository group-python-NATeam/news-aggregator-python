from django.shortcuts import render
from django.views.generic import ListView
from .models import Article, Category


def index(request):
    """Homepage view that displays latest articles."""
    latest_articles = Article.objects.select_related('category', 'source').order_by('-publication_date')[:20]
    categories = Category.objects.all()

    context = {
        'articles': latest_articles,
        'categories': categories,
    }
    return render(request, 'news_app/index.html', context)


class ArticleListView(ListView):
    """Generic view for listing articles with pagination."""
    model = Article
    template_name = 'news_app/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    ordering = ['-publication_date']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category', 'source')
        
        # Filter by category if provided in URL
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # Add current category to context if filtering by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = Category.objects.get(slug=category_slug)
            
        return context
