import argparse
import os

import spacy
from spacy.scorer import Scorer
from spacy.tokens import DocBin
from spacy.training import Example


# Defaults
DEFAULT_MODEL_DIR = os.path.join("ner_model", "output", "model-best")
DEFAULT_TRAIN_DATA = os.path.join("data", "ner", "train.spacy")
DEFAULT_DEV_DATA = os.path.join("data", "ner", "dev.spacy")
DEFAULT_TEST_DATA = os.path.join("data", "ner", "test.spacy")


def _score_split(nlp, data_path: str) -> dict:
    """Score a single data split and return the scores dict."""
    doc_bin = DocBin().from_disk(data_path)
    gold_docs = list(doc_bin.get_docs(nlp.vocab))

    examples = []
    for gold_doc in gold_docs:
        pred_doc = nlp(gold_doc.text)
        example = Example(pred_doc, gold_doc)
        examples.append(example)

    scorer = Scorer()
    return scorer.score(examples)


def _print_scores(label: str, scores: dict) -> None:
    """Pretty-print P / R / F1 for one split."""
    ents_p = scores.get("ents_p", 0)
    ents_r = scores.get("ents_r", 0)
    ents_f = scores.get("ents_f", 0)
    print(f"  {label + ' Precision':>25s} : {ents_p:.4f}")
    print(f"  {label + ' Recall':>25s} : {ents_r:.4f}")
    print(f"  {label + ' F1':>25s} : {ents_f:.4f}")


def _print_per_type(scores: dict) -> None:
    """Print per-entity-type breakdown."""
    per_type = scores.get("ents_per_type", {})
    if per_type:
        print(f"\n  {'Entity Type':<25s} {'P':>8s} {'R':>8s} {'F1':>8s}")
        print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*8}")
        for ent_type, type_scores in sorted(per_type.items()):
            p = type_scores.get("p", 0)
            r = type_scores.get("r", 0)
            f = type_scores.get("f", 0)
            print(f"  {ent_type:<25s} {p:>8.4f} {r:>8.4f} {f:>8.4f}")


def evaluate_ner(
    model_dir: str = DEFAULT_MODEL_DIR,
    train_data: str = DEFAULT_TRAIN_DATA,
    dev_data: str = DEFAULT_DEV_DATA,
    test_data: str = DEFAULT_TEST_DATA,
) -> dict:
    """
    Evaluate the NER model on Train, Dev, and Test splits.

    Returns a dict with keys 'train', 'dev', 'test', each containing
    the full spaCy scores dict for that split.
    """
    nlp = spacy.load(model_dir)
    print(f"Loaded model from: {model_dir}")
    print(f"Pipeline components: {nlp.pipe_names}")

    results = {}

    # ── Train split ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  NER MODEL — EVALUATION REPORT")
    print("=" * 60)

    if os.path.exists(train_data):
        print("\n  ── TRAIN SET ──")
        results["train"] = _score_split(nlp, train_data)
        _print_scores("Train", results["train"])
    else:
        print(f"\n  ⚠ Train data not found: {train_data}")

    # ── Dev split ──────────────────────────────────────────────
    if os.path.exists(dev_data):
        print("\n  ── DEV SET ──")
        results["dev"] = _score_split(nlp, dev_data)
        _print_scores("Dev", results["dev"])
    else:
        print(f"\n  ⚠ Dev data not found: {dev_data}")

    # ── Test split (the TRUE held-out evaluation) ──────────────
    if os.path.exists(test_data):
        print("\n  ── TEST SET (held-out) ──")
        results["test"] = _score_split(nlp, test_data)
        _print_scores("Test", results["test"])
    else:
        print(f"\n  ⚠ Test data not found: {test_data}")

    # ── Generalization gap ─────────────────────────────────────
    print("\n" + "-" * 60)
    train_f1 = results.get("train", {}).get("ents_f", 0)
    dev_f1 = results.get("dev", {}).get("ents_f", 0)
    test_f1 = results.get("test", {}).get("ents_f", 0)

    if train_f1 and test_f1:
        gap = train_f1 - test_f1
        status = "✓ Healthy" if gap < 5.0 else "✗ Overfitting"
        print(f"  Generalization Gap (Train-Test): {gap:.2f} pp  [{status}]")
    if train_f1 and dev_f1:
        gap = train_f1 - dev_f1
        print(f"  Train-Dev Gap:                   {gap:.2f} pp")

    # ── Per-type breakdown (from test set) ─────────────────────
    if "test" in results:
        print("\n  ── Per-Entity-Type Breakdown (Test Set) ──")
        _print_per_type(results["test"])
    elif "dev" in results:
        print("\n  ── Per-Entity-Type Breakdown (Dev Set) ──")
        _print_per_type(results["dev"])

    print()
    return results


# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate spaCy NER model on Train / Dev / Test splits."
    )
    parser.add_argument("--model_dir", default=DEFAULT_MODEL_DIR)
    parser.add_argument("--train_data", default=DEFAULT_TRAIN_DATA)
    parser.add_argument("--dev_data", default=DEFAULT_DEV_DATA)
    parser.add_argument("--test_data", default=DEFAULT_TEST_DATA)
    args = parser.parse_args()

    evaluate_ner(
        model_dir=args.model_dir,
        train_data=args.train_data,
        dev_data=args.dev_data,
        test_data=args.test_data,
    )
