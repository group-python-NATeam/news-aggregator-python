import pandas as pd
from django.core.management.base import BaseCommand
from news_app.models import Article
from news_app.services.ai_classifier import classifier

class Command(BaseCommand):
    help = "Evaluates the AI classifier against a manually labeled dataset."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            default="evaluation_dataset.csv",
            help="Path to the labeled CSV (default: evaluation_dataset.csv)",
        )
        parser.add_argument(
            "--output",
            default="evaluation_results.csv",
            help="Path to save results CSV (default: evaluation_results.csv)",
        )

    def handle(self, *args, **options):
        input_csv_path = options["input"]
        output_csv_path = options["output"]

        try:
            df = pd.read_csv(input_csv_path)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: {input_csv_path} not found. Please create it first."))
            return

        required_cols = {"article_id", "title", "true_category_slug"}
        if not required_cols.issubset(df.columns):
            self.stdout.write(self.style.ERROR(f"CSV must contain columns: {sorted(required_cols)}"))
            return

        results = []
        processed = 0
        for _, row in df.iterrows():
            article_id = row["article_id"]
            true_category = str(row["true_category_slug"]).strip()

            try:
                article = Article.objects.get(id=article_id)
            except Article.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Article with ID {article_id} not found. Skipping."))
                continue

            # Prefer cleaned content; otherwise title + summary
            content = (article.cleaned_content or "").strip()
            if not content:
                content = f"{article.title}. {article.summary or ''}".strip()

            if not content:
                predicted_category = None
            else:
                try:
                    predicted_category = classifier.predict(content)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Prediction error for article {article_id}: {e}"))
                    predicted_category = None

            is_correct = int(bool(predicted_category) and (true_category == predicted_category))

            results.append(
                {
                    "article_id": article.id,
                    "title": article.title,
                    "true_category": true_category,
                    "predicted_category": predicted_category if predicted_category else "",
                    "is_correct": is_correct,
                }
            )

            processed += 1
            self.stdout.write(f"Processed article {article_id}: True='{true_category}', Predicted='{predicted_category}'")

        if not results:
            self.stdout.write(self.style.ERROR("No results to save. Did the CSV contain valid article IDs?"))
            return

        result_df = pd.DataFrame(results)
        result_df.to_csv(output_csv_path, index=False, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"\nEvaluation complete. Results saved to {output_csv_path}"))

        accuracy = result_df["is_correct"].mean() * 100
        self.stdout.write(self.style.SUCCESS(f"Overall Model Accuracy: {accuracy:.2f}%"))


