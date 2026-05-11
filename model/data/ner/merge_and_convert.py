"""
Merge noisy_samples.json into the training split and reconvert all
splits to .spacy format.
"""

import json
import os
import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans

nlp = spacy.blank("en")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def convert(data, output_path):
    doc_bin = DocBin()
    skipped = 0
    total = 0
    for text, annotations in data:
        doc = nlp.make_doc(text)
        spans = []
        for start, end, label in annotations.get("entities", []):
            total += 1
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                span = doc.char_span(start, end, label=label, alignment_mode="expand")
            if span is not None:
                spans.append(span)
            else:
                skipped += 1
        doc.ents = filter_spans(spans)
        doc_bin.add(doc)
    doc_bin.to_disk(output_path)
    return len(data), total, skipped


def main():
    train_path = os.path.join(BASE_DIR, "requirements_ner_train.json")
    dev_path = os.path.join(BASE_DIR, "requirements_ner_dev.json")
    test_path = os.path.join(BASE_DIR, "requirements_ner_test.json")
    noisy_path = os.path.join(BASE_DIR, "noisy_samples.json")

    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(dev_path, "r", encoding="utf-8") as f:
        dev_data = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    with open(noisy_path, "r", encoding="utf-8") as f:
        noisy_data = json.load(f)
    
    boundary_path = os.path.join(BASE_DIR, "boundary_samples.json")
    if os.path.exists(boundary_path):
        with open(boundary_path, "r", encoding="utf-8") as f:
            boundary_data = json.load(f)
    else:
        boundary_data = []

    print(f"Original train:   {len(train_data)} samples")
    print(f"Noisy samples:    {len(noisy_data)} samples")
    print(f"Boundary samples: {len(boundary_data)} samples")

    # Add samples to training data
    train_data.extend(noisy_data)
    train_data.extend(boundary_data)
    print(f"Merged train:     {len(train_data)} samples")

    # Convert all splits
    for name, data, out_name in [
        ("train", train_data, "train.spacy"),
        ("dev", dev_data, "dev.spacy"),
        ("test", test_data, "test.spacy"),
    ]:
        out_path = os.path.join(BASE_DIR, out_name)
        docs, ents, skip = convert(data, out_path)
        print(f"[{name:5s}] {docs} docs, {ents} entities, {skip} skipped -> {out_name}")

    print("\n[OK] All .spacy files rebuilt successfully.")


if __name__ == "__main__":
    main()
