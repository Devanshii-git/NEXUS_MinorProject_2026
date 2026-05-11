import argparse
import os
import sys

import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch.utils.data import DataLoader
from transformers import DistilBertTokenizer, get_linear_schedule_with_warmup

# Local imports
from requirement_classifier.dataset import RequirementDataset
from requirement_classifier.model import (
    MODEL_NAME,
    create_model,
    save_model,
)

# Defaults (can be overridden via CLI)

DEFAULT_TRAIN_CSV = os.path.join("data", "requirement_classification", "train.csv")
DEFAULT_TEST_CSV = os.path.join("data", "requirement_classification", "test.csv")
DEFAULT_OUTPUT_DIR = os.path.join("requirement_classifier", "saved_model")
DEFAULT_EPOCHS = 5
DEFAULT_BATCH_SIZE = 16
DEFAULT_LR = 2e-5
DEFAULT_MAX_LEN = 128


# Training loop
def train(
    train_csv: str,
    test_csv: str,
    output_dir: str,
    epochs: int,
    batch_size: int,
    lr: float,
    max_length: int,
) -> None:
    """
    Fine-tune DistilBERT on the requirement-classification task.

    Steps
    -----
    1. Load tokenizer and datasets.
    2. Build DataLoaders.
    3. Create the model and move to device (GPU if available).
    4. Set up optimizer and learning-rate scheduler.
    5. Run the training loop with evaluation after each epoch.
    6. Save the best model (by F1 score).
    """

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = RequirementDataset(train_csv, tokenizer, max_length)
    test_dataset = RequirementDataset(test_csv, tokenizer, max_length)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    model = create_model()
    model.to(device)


    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps), 
        num_training_steps=total_steps,
    )

    best_f1 = 0.0
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0

        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
            )
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)

        metrics = evaluate_model(model, test_loader, device)
        print(
            f"Epoch {epoch}/{epochs}  "
            f"Loss: {avg_loss:.4f}  "
            f"Acc: {metrics['accuracy']:.4f}  "
            f"P: {metrics['precision']:.4f}  "
            f"R: {metrics['recall']:.4f}  "
            f"F1: {metrics['f1']:.4f}"
        )

        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            os.makedirs(output_dir, exist_ok=True)
            save_model(model, tokenizer, output_dir)
            print(f"  ↳ New best F1 = {best_f1:.4f} — model saved.")

    print("\n✓ Training complete.")


# Evaluation helper
def evaluate_model(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: torch.device,
) -> dict:
    model.eval()
    all_preds, all_labels = [], []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"]

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits                         # (batch, 2)
            preds = torch.argmax(logits, dim=1).cpu()       # (batch,)

            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())

    return {
        "accuracy": accuracy_score(all_labels, all_preds),
        "precision": precision_score(all_labels, all_preds, zero_division=0),
        "recall": recall_score(all_labels, all_preds, zero_division=0),
        "f1": f1_score(all_labels, all_preds, zero_division=0),
    }


# CLI entry-point
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-tune DistilBERT for requirement detection."
    )
    parser.add_argument("--train_csv", default=DEFAULT_TRAIN_CSV)
    parser.add_argument("--test_csv", default=DEFAULT_TEST_CSV)
    parser.add_argument("--output_dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--batch_size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=DEFAULT_LR)
    parser.add_argument("--max_length", type=int, default=DEFAULT_MAX_LEN)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(
        train_csv=args.train_csv,
        test_csv=args.test_csv,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        max_length=args.max_length,
    )
