from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.http import HttpResponse, Http404, JsonResponse
from django.core.paginator import Paginator
from .models import Article, Category
from .services.tts_service import text_to_audio_bytes


def index(request):
    """
    Optimized homepage view that displays latest articles.
    Uses select_related for efficient database queries.
    """
    # Optimized query with select_related to prevent N+1 queries
    # Load more articles initially for smoother TikTok-style scrolling
    latest_articles = (
        Article.objects
        .select_related('category', 'source')  # Efficient JOINs
        .order_by('-publication_date', '-created_at')[:15]  # Recently crawled first
    )
    
    # Categories query (consider caching this in production)
    categories = Category.objects.all()

    context = {
        'articles': latest_articles,
        'categories': categories,
    }
    return render(request, 'news_app/index.html', context)


def article_api_view(request):
    """
    Optimized API endpoint that returns paginated articles as JSON.
    Includes summary_audio URL and uses select_related for performance.
    """
    page_number = request.GET.get('page', 1)
    
    # Optimized queryset with select_related to prevent N+1 queries
    qs = (
        Article.objects
        .select_related('source', 'category')  # Efficient JOIN for foreign keys
        .order_by('-publication_date', '-created_at')  # Recently crawled first
    )
    
    # Smaller pagination for smoother infinite scroll experience
    paginator = Paginator(qs, 3)  # 3 articles per page for better UX
    page_obj = paginator.get_page(page_number)

    # Build optimized response data
    articles_data = []
    for article in page_obj.object_list:
        article_data = {
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'image_url': article.image_url,
            'source__name': article.source.name,  # Already loaded via select_related
            'category__name': article.category.name if article.category else None,  # Handle null categories
            'summary_audio_url': article.summary_audio.url if article.summary_audio else None,  # TTS audio URL
        }
        articles_data.append(article_data)

    data = {
        'articles': articles_data,
        'has_next': page_obj.has_next(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'count': paginator.count,
    }
    return JsonResponse(data)


class ArticleListView(ListView):
    """Generic view for listing articles with pagination."""
    model = Article
    template_name = 'news_app/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    ordering = ['-publication_date']

    def get_queryset(self):
        """
        Optimized queryset with select_related for performance.
        Prevents N+1 queries by loading related objects efficiently.
        """
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


def article_speak_view(request, article_id):
    """
    API endpoint that returns MP3 audio for an article.
    Prefers pre-generated summary_audio file; falls back to dynamic generation.
    Optimized to use FileField when available for better performance.
    """
    try:
        article = Article.objects.get(pk=article_id)

        # First, try to serve pre-generated audio file (much faster)
        if article.summary_audio:
            try:
                # Serve the pre-generated audio file
                with open(article.summary_audio.path, 'rb') as audio_file:
                    return HttpResponse(
                        audio_file.read(), 
                        content_type='audio/mpeg',
                        headers={'Cache-Control': 'public, max-age=3600'}  # Cache for 1 hour
                    )
            except FileNotFoundError:
                # File missing, fall back to dynamic generation
                pass

        # Fallback: Dynamic audio generation (slower)
        body = (article.summary or "") if getattr(article, "summary", None) else ""
        if not body:
            raw = getattr(article, "cleaned_content", "") or ""
            body = raw[:500]

        if not body:
            raise Http404("Article has no content to speak.")

        audio_bytes_io = text_to_audio_bytes(body)
        if not audio_bytes_io:
            raise Exception("Failed to generate audio.")

        return HttpResponse(
            audio_bytes_io.read(), 
            content_type='audio/mpeg',
            headers={'Cache-Control': 'public, max-age=300'}  # Cache for 5 minutes
        )

    except Article.DoesNotExist:
        raise Http404("Article not found.")
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)