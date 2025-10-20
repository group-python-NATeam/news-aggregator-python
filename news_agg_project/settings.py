from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Lấy SECRET_KEY từ biến môi trường
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-default-dev-key-replace-me')

# SECURITY WARNING: don't run with debug turned on in production!
# Lấy DEBUG từ biến môi trường (mặc định là False)
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Cấu hình ALLOWED_HOSTS từ biến môi trường
ALLOWED_HOSTS = ['news-agg-app.onrender.com', 'localhost', '127.0.0.1']

# (Nếu ông dùng Biến Môi trường RENDER_APP_NAME đã set ở image_30f9de.png)
# Cách xịn hơn:
# ALLOWED_HOSTS = [
#     os.environ.get('RENDER_APP_NAME', 'localhost') + '.onrender.com',
#     'localhost',
#     '127.0.0.1',
# ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # My apps
    'news_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <-- THÊM DÒNG NÀY
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'news_agg_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'news_agg_project.wsgi.application'


# Cấu hình Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Thư mục mà 'collectstatic' sẽ gom tất cả file tĩnh vào
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Chỉ định thư mục chứa file tĩnh ở local dev (nơi bạn để file css)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Cấu hình storage cho WhiteNoise để nén file và tạo cache
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- MEDIA FILES ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# LOGGING CONFIGURATION
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'crawler.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'crawler': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

# --- CELERY SETTINGS ---
# Prefer env overrides; default to local Redis.
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# ==============================================================================
# 💡 PRODUCTION LOGGING CONFIGURATION
# ==============================================================================
#
# Khi DEBUG=False (chạy trên production), chúng ta KHÔNG ghi ra file nữa.
# Thay vào đó, chúng ta bắt tất cả log phải đi ra 'console'.
# Nền tảng Render sẽ tự động bắt (capture) luồng console này.

if not DEBUG:
    # 1. Vô hiệu hóa 'file' handler bằng cách xóa nó
    if 'file' in LOGGING['handlers']:
        del LOGGING['handlers']['file']

    # 2. Bắt tất cả 'loggers' chỉ sử dụng 'console'
    for logger_config in LOGGING['loggers'].values():
        if 'file' in logger_config.get('handlers', []):
            # Loại bỏ 'file' ra khỏi danh sách handlers
            logger_config['handlers'] = [h for h in logger_config['handlers'] if h != 'file']

            # Đảm bảo 'console' vẫn còn đó (nếu nó chưa có)
            if 'console' not in logger_config['handlers']:
                logger_config['handlers'].append('console')