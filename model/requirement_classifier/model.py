from transformers import DistilBertForSequenceClassification

# Constants
MODEL_NAME = "distilbert-base-uncased"
NUM_LABELS = 2  # binary: 0 = Not Requirement, 1 = Requirement

# Human-readable label mapping
LABEL_MAP = {0: "Not Requirement", 1: "Requirement"}


def create_model(
    model_name: str = MODEL_NAME,
    num_labels: int = NUM_LABELS,
) -> DistilBertForSequenceClassification:
    model = DistilBertForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
    )
    return model


def save_model(model, tokenizer, output_dir: str) -> None:
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Model and tokenizer saved to {output_dir}")


def load_model(
    model_dir: str,
) -> DistilBertForSequenceClassification:
    model = DistilBertForSequenceClassification.from_pretrained(model_dir)
    return model
