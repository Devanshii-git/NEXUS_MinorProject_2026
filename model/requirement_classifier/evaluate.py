import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
    auc,
)
from torch.utils.data import DataLoader
from transformers import DistilBertTokenizer

from requirement_classifier.dataset import RequirementDataset
from requirement_classifier.model import LABEL_MAP, load_model

# Defaults
DEFAULT_MODEL_DIR = os.path.join("requirement_classifier", "saved_model")
DEFAULT_TEST_CSV = os.path.join("data", "requirement_classification", "test.csv")
DEFAULT_BATCH_SIZE = 16
DEFAULT_MAX_LEN = 128


def evaluate(
    model_dir: str,
    test_csv: str,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_length: int = DEFAULT_MAX_LEN,
) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load model and tokenizer
    model = load_model(model_dir)
    model.to(device)
    model.eval()

    tokenizer = DistilBertTokenizer.from_pretrained(model_dir)
    test_dataset = RequirementDataset(test_csv, tokenizer, max_length)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # Collect predictions and probabilities
    all_preds, all_labels, all_probs = [], [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"]

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            preds = torch.argmax(logits, dim=1).cpu()
            probs = torch.softmax(logits, dim=1).cpu()

            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())
            all_probs.extend(probs.tolist())

    all_probs = np.array(all_probs)

    # Compute metrics
    metrics = {
        "accuracy": accuracy_score(all_labels, all_preds),
        "precision": precision_score(all_labels, all_preds, zero_division=0),
        "recall": recall_score(all_labels, all_preds, zero_division=0),
        "f1": f1_score(all_labels, all_preds, zero_division=0),
    }

    # Pretty-print results
    print("\n" + "=" * 50)
    print("  REQUIREMENT CLASSIFIER — EVALUATION REPORT")
    print("=" * 50)
    for k, v in metrics.items():
        print(f"  {k.capitalize():>12s} : {v:.4f}")
    print("-" * 50)
    print("\nDetailed classification report:\n")
    target_names = [LABEL_MAP[i] for i in sorted(LABEL_MAP)]
    print(classification_report(all_labels, all_preds, target_names=target_names))

    # ── Output directory for plots ────────────────────────────────────
    plot_dir = "output"
    os.makedirs(plot_dir, exist_ok=True)

    # ── Confusion Matrix ──────────────────────────────────────────────
    cm = confusion_matrix(all_labels, all_preds)
    fig_cm, ax_cm = plt.subplots(figsize=(6, 5))
    fig_cm.patch.set_facecolor("#1e1e2e")
    ax_cm.set_facecolor("#1e1e2e")

    disp = ConfusionMatrixDisplay(cm, display_labels=target_names)
    disp.plot(ax=ax_cm, cmap="Blues", colorbar=True)
    ax_cm.set_title(
        "Confusion Matrix — Requirement Classifier",
        color="white", fontsize=13, fontweight="bold", pad=12,
    )
    ax_cm.set_xlabel("Predicted Label", color="white", fontsize=11)
    ax_cm.set_ylabel("True Label", color="white", fontsize=11)
    ax_cm.tick_params(colors="white")
    plt.setp(ax_cm.get_xticklabels(), color="white")
    plt.setp(ax_cm.get_yticklabels(), color="white")

    cm_path = os.path.join(plot_dir, "confusion_matrix.png")
    fig_cm.savefig(cm_path, dpi=150, bbox_inches="tight", facecolor=fig_cm.get_facecolor())
    plt.close(fig_cm)
    print(f"  Confusion matrix saved to {cm_path}")

    # ── ROC Curve ─────────────────────────────────────────────────────
    # For binary classification, use probability of the positive class (1 = Requirement)
    y_score = all_probs[:, 1]
    fpr, tpr, _ = roc_curve(all_labels, y_score)
    roc_auc = auc(fpr, tpr)

    fig_roc, ax_roc = plt.subplots(figsize=(7, 6))
    fig_roc.patch.set_facecolor("#1e1e2e")
    ax_roc.set_facecolor("#1e1e2e")

    ax_roc.plot(
        fpr, tpr,
        color="#3498db", linewidth=2.5,
        label=f"ROC Curve (AUC = {roc_auc:.2f})",
    )
    ax_roc.plot([0, 1], [0, 1], "--", color="#636e72", linewidth=1)
    ax_roc.fill_between(fpr, tpr, alpha=0.15, color="#3498db")

    ax_roc.set_xlim([0.0, 1.0])
    ax_roc.set_ylim([0.0, 1.05])
    ax_roc.set_xlabel("False Positive Rate", color="white", fontsize=12)
    ax_roc.set_ylabel("True Positive Rate", color="white", fontsize=12)
    ax_roc.set_title(
        "ROC Curve — Requirement Classifier",
        color="white", fontsize=14, fontweight="bold",
    )
    ax_roc.legend(
        loc="lower right", fontsize=11,
        facecolor="#2d2d44", edgecolor="#636e72", labelcolor="white",
    )
    ax_roc.tick_params(colors="white")
    for spine in ax_roc.spines.values():
        spine.set_color("#636e72")

    roc_path = os.path.join(plot_dir, "roc_curve.png")
    fig_roc.savefig(roc_path, dpi=150, bbox_inches="tight", facecolor=fig_roc.get_facecolor())
    plt.close(fig_roc)
    print(f"  ROC curve saved to {roc_path}  (AUC = {roc_auc:.4f})")

    metrics["roc_auc"] = roc_auc
    return metrics


# CLI
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the fine-tuned requirement classifier."
    )
    parser.add_argument("--model_dir", default=DEFAULT_MODEL_DIR)
    parser.add_argument("--test_csv", default=DEFAULT_TEST_CSV)
    parser.add_argument("--batch_size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max_length", type=int, default=DEFAULT_MAX_LEN)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    evaluate(
        model_dir=args.model_dir,
        test_csv=args.test_csv,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
