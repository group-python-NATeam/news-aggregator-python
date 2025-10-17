from celery import shared_task
import logging
from django.db import transaction
from django.core.files.base import ContentFile
from .models import Article, Category
from .services.ai_classifier import classifier
from .services.summarizer import get_summary
from .services import tts_service

logger = logging.getLogger('crawler')  # reuse existing crawler logger if configured, else root

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def classify_article_task(self, article_id: int):
    """
    Asynchronously classify an article by ID and save its Category.
    Retries on transient failures.
    """
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        logger.error(f"Article with ID {article_id} does not exist. Cannot classify.")
        return

    if getattr(article, 'category_id', None):
        logger.info(f"Article ID {article_id} already has a category. Skipping.")
        return

    # Choose content to classify: prefer cleaned content, else title + summary
    content = (article.cleaned_content or "").strip()
    if not content:
        content = f"{article.title}. {article.summary or ''}".strip()

    if not content:
        logger.warning(f"No content available to classify for Article ID {article_id}.")
        return

    try:
        predicted_slug = classifier.predict(content)
        logger.info(f'AI predicted "{predicted_slug}" for Article ID {article_id}')
    except Exception as exc:
        logger.exception(f"Classifier error for Article ID {article_id}: {exc}")
        raise self.retry(exc=exc)

    if not predicted_slug:
        logger.warning(f"No predicted slug for Article ID {article_id}.")
        return

    try:
        category = Category.objects.get(slug=predicted_slug)
    except Category.DoesNotExist:
        logger.error(f"Predicted slug '{predicted_slug}' not found in DB. Article ID {article_id}.")
        return

    try:
        with transaction.atomic():
            article.category = category
            article.save(update_fields=['category'])
        logger.info(f"✅ Successfully classified Article ID {article_id} as '{predicted_slug}'")

        # --- NEW: chain to summarization ---
        summarize_article_task.delay(article_id)
        logger.info(f"🔗 Chaining to summarization task for Article ID {article_id}")
        # -----------------------------------

    except Exception as exc:
        logger.exception(f"DB error while saving category for Article ID {article_id}: {exc}")
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, default_retry_delay=300, rate_limit='3/m')
def summarize_article_task(self, article_id: int):
    """
    Asynchronously summarize an article by ID. Should be called after classification.
    """
    try:
        article = Article.objects.get(id=article_id)
        logger.info(f"Starting summarization for Article ID {article_id}")
    except Article.DoesNotExist:
        logger.error(f"❌ Article with ID {article_id} does not exist. Cannot summarize.")
        return

    if not article.cleaned_content:
        logger.info(f"⏩ Article ID {article_id} has no cleaned content. Skipping summarization.")
        return

    if article.summary:
        logger.info(f"⏩ Article ID {article_id} already has a summary. Skipping.")
        return

    try:
        summary_text = get_summary(article.cleaned_content)
    except Exception as exc:
        logger.error(f"❌ Summarization call failed for Article ID {article_id}: {exc}")
        raise self.retry(exc=exc)

    if summary_text:
        try:
            with transaction.atomic():
                article.summary = summary_text
                article.save(update_fields=['summary'])
            logger.info(f"✅ Successfully summarized Article ID {article_id}")
            
            # --- NEW: chain to TTS generation ---
            generate_tts_task.delay(article_id)
            logger.info(f"🔗 Chaining to TTS generation task for Article ID {article_id}")
            # -----------------------------------
            
        except Exception as exc:
            logger.error(f"❌ DB save failed for Article ID {article_id}: {exc}")
            raise self.retry(exc=exc)
    else:
        logger.warning(f"⚠️ Summarization returned empty for Article ID {article_id}.")

@shared_task(bind=True, max_retries=3, default_retry_delay=300, rate_limit='10/m')
def generate_tts_task(self, article_id: int):
    """
    Build an MP3 from Article.summary and save to Article.summary_audio.
    Should be called AFTER the article has a summary.
    """
    try:
        article = Article.objects.get(id=article_id)
        logger.info(f"Starting TTS generation for Article ID {article_id}")
    except Article.DoesNotExist:
        logger.error(f"❌ Article with ID {article_id} does not exist. Cannot generate TTS.")
        return

    if not article.summary:
        logger.info(f"⏩ Article ID {article_id} has no summary. Skipping TTS.")
        return

    if article.summary_audio:
        logger.info(f"⏩ Article ID {article_id} already has summary audio. Skipping TTS.")
        return

    try:
        audio_bytes = None
        # Prefer a bytes-returning helper if available
        if hasattr(tts_service, 'create_audio_from_text'):
            audio_bytes = tts_service.create_audio_from_text(article.summary)
        else:
            # Fallback: consume BytesIO from text_to_audio_bytes
            if hasattr(tts_service, 'text_to_audio_bytes'):
                buf = tts_service.text_to_audio_bytes(article.summary)
                audio_bytes = buf.getvalue() if buf else None

        if not audio_bytes:
            logger.warning(f"⚠️ TTS service returned no data for Article ID {article_id}")
            return

        file_name = f"summary_{article_id}.mp3"
        with transaction.atomic():
            article.summary_audio.save(file_name, ContentFile(audio_bytes), save=True)
        logger.info(f"✅ Successfully generated TTS for Article ID {article_id}")

    except Exception as exc:
        logger.error(f"❌ TTS generation task failed for Article ID {article_id}: {exc}")
        raise self.retry(exc=exc)
