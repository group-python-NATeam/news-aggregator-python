import os
import logging
from pathlib import Path
from typing import Union, List

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class AIClassifier:
    """
    Singleton AI classifier for Vietnamese news categorization.
    Loads a fine-tuned PhoBERT model once and provides prediction API.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._load_model()
            self.__class__._initialized = True

    def _find_model_path(self) -> Path:
        """Find the model directory using fallback strategy."""
        # Primary: environment variable
        env_path = os.getenv('AI_MODEL_DIR')
        if env_path and Path(env_path).is_dir():
            return Path(env_path)
        
        # Fallback paths relative to BASE_DIR
        base_dir = Path(settings.BASE_DIR)
        fallback_paths = [
            base_dir / 'news_app' / 'ml_models' / 'my-finetuned-phobert',
            base_dir / 'news_app' / 'ml_models' / 'my_phobert_classifier'
        ]
        
        for path in fallback_paths:
            if path.is_dir():
                return path
        
        # None found - prepare error message
        checked_paths = [env_path] + [str(p) for p in fallback_paths]
        expected_files = ['config.json', 'tokenizer_config.json', 'model.safetensors or pytorch_model.bin']
        
        raise RuntimeError(
            f"No valid model directory found. Checked paths: {checked_paths}. "
            f"Expected files in model directory: {expected_files}"
        )

    def _get_label_mapping(self, config) -> dict:
        """Extract label mapping from model config or use fallback."""
        # Try to get meaningful labels from config
        if hasattr(config, 'id2label') and config.id2label:
            labels = config.id2label
            # Check if labels are meaningful (not generic LABEL_X)
            if not all(label.startswith('LABEL_') for label in labels.values()):
                return {int(k): v for k, v in labels.items()}
        
        # Fallback to Vietnamese category slugs
        fallback_mapping = {
            0: 'cong-nghe',
            1: 'kinh-te', 
            2: 'giao-duc',
            3: 'giai-tri',
            4: 'suc-khoe',
            5: 'the-thao',
            6: 'phap-luat',
            7: 'xa-hoi'
        }
        
        logger.info("Using fallback Vietnamese category mapping")
        return fallback_mapping

    def _load_model(self):
        """Load the model, tokenizer and configure settings."""
        try:
            # Find model path
            self.model_path = self._find_model_path()
            
            # Device selection
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            
            # Max length from environment or default
            self.max_length = int(os.getenv('AI_MAX_LEN', '256'))
            
            # Load model components
            self.config = AutoConfig.from_pretrained(self.model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path,
                config=self.config
            )
            
            # Setup model for inference
            self.model.to(self.device)
            self.model.eval()
            
            # Get label mapping
            self.id2label = self._get_label_mapping(self.config)
            
            # Log successful initialization
            logger.info(
                f"AI Classifier loaded - Path: {self.model_path}, "
                f"Device: {self.device}, Max Length: {self.max_length}"
            )
            
        except Exception as e:
            logger.error(f"Failed to load AI classifier: {e}")
            raise

    def predict(self, text_or_list: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Predict category for text input(s).
        
        Args:
            text_or_list: Single text string or list of strings
            
        Returns:
            Single category slug or list of category slugs
        """
        # Handle single string input
        is_single = isinstance(text_or_list, str)
        texts = [text_or_list] if is_single else text_or_list
        
        if not texts:
            return [] if not is_single else ""
        
        try:
            # Tokenize inputs
            inputs = self.tokenizer(
                texts,
                truncation=True,
                padding=True,
                max_length=self.max_length,
                return_tensors='pt'
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_classes = torch.argmax(predictions, dim=-1)
            
            # Convert to category slugs
            results = []
            for pred_class in predicted_classes.cpu().numpy():
                category_slug = self.id2label.get(int(pred_class), 'xa-hoi')  # default fallback
                results.append(category_slug)
            
            # Return appropriate format
            return results[0] if is_single else results
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # Return safe fallback
            fallback = 'xa-hoi'
            return fallback if is_single else [fallback] * len(texts)


# Module-level singleton instance
classifier = AIClassifier()
