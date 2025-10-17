# analyze_results.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report

LABELS = [
    "cong-nghe","kinh-te","giao-duc","giai-tri",
    "suc-khoe","the-thao","phap-luat","xa-hoi"
]

def analyze(filepath="evaluation_results.csv"):
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Please run the evaluation first.")
        return

    if not {"true_category", "predicted_category"}.issubset(df.columns):
        print("Error: results CSV must have 'true_category' and 'predicted_category' columns.")
        return

    true_labels = df["true_category"].fillna("")
    predicted_labels = df["predicted_category"].fillna("")

    print("--- Classification Report ---")
    print(classification_report(true_labels, predicted_labels, labels=LABELS, zero_division=0))

    print("\n--- Generating Confusion Matrix ---")
    cm = confusion_matrix(true_labels, predicted_labels, labels=LABELS)

    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=LABELS, yticklabels=LABELS)
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png")
    print("Confusion matrix saved as 'confusion_matrix.png'")
    try:
        plt.show()
    except Exception:
        pass

if __name__ == "__main__":
    analyze()
