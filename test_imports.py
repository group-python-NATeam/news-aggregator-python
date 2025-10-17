#!/usr/bin/env python3

print("Testing imports...")

try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
except ImportError as e:
    print(f"❌ PyTorch: {e}")

try:
    import transformers
    print(f"✅ Transformers: {transformers.__version__}")
except ImportError as e:
    print(f"❌ Transformers: {e}")

try:
    import django
    print(f"✅ Django: {django.__version__}")
except ImportError as e:
    print(f"❌ Django: {e}")

print("Testing Django setup...")
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_agg_project.settings')

try:
    import django
    django.setup()
    print("✅ Django setup complete")
except Exception as e:
    print(f"❌ Django setup failed: {e}")

try:
    from news_app.services.ai_classifier import classifier
    print("✅ AI Classifier imported successfully")
except Exception as e:
    print(f"❌ AI Classifier import failed: {e}")
