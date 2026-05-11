"""
Safe augmentation pipeline for NER training data.
ONLY applies transformations that preserve entity span offsets:
  1. Typo injection (character-level noise)
  2. Casing variation (lowercase, capitalize, random)

Does NOT modify sentence structure or break entity boundaries.
"""

import json
import os
import random

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def inject_typos(text: str, entities: list, rate: float = 0.03) -> tuple:
    """
    Inject character-level typos OUTSIDE entity spans only.
    This guarantees entity text and offsets remain valid.
    """
    # Build set of protected character positions
    protected = set()
    for start, end, _ in entities:
        for i in range(start, end):
            protected.add(i)

    chars = list(text)
    offset_shift = 0
    new_entities = [list(e) for e in entities]
    result = []

    for i, ch in enumerate(chars):
        if i in protected or not ch.isalpha():
            result.append(ch)
            continue

        if random.random() < rate:
            op = random.choice(["swap", "double", "drop"])
            if op == "swap" and i + 1 < len(chars) and (i + 1) not in protected:
                # Swap with next char (no length change)
                result.append(chars[i + 1])
                chars[i + 1] = ch  # will be appended next iteration
            elif op == "double":
                result.append(ch)
                result.append(ch)
                # Shift all entity offsets after this position
                for ent in new_entities:
                    if ent[0] > i + offset_shift:
                        ent[0] += 1
                    if ent[1] > i + offset_shift:
                        ent[1] += 1
                offset_shift += 1
            elif op == "drop":
                # Shift all entity offsets after this position
                for ent in new_entities:
                    if ent[0] > i + offset_shift:
                        ent[0] -= 1
                    if ent[1] > i + offset_shift:
                        ent[1] -= 1
                offset_shift -= 1
                continue
            else:
                result.append(ch)
        else:
            result.append(ch)

    new_text = "".join(result)

    # Validate all entities still align
    valid = True
    for start, end, label in new_entities:
        if start < 0 or end > len(new_text) or start >= end:
            valid = False
            break

    if not valid:
        return text, entities  # Return original if alignment broke

    return new_text, [tuple(e) for e in new_entities]


def vary_casing(text: str, entities: list) -> tuple:
    """
    Apply casing variation. Since casing doesn't change character
    positions, entity offsets are always preserved.
    """
    strategy = random.choice(["lower", "original", "capitalize"])

    if strategy == "lower":
        return text.lower(), entities
    elif strategy == "capitalize":
        return text.capitalize(), entities
    return text, entities


def augment_sample(text: str, entities: list) -> list:
    """Generate 1-2 augmented variants of a single sample."""
    variants = []

    # Variant 1: casing change
    new_text, new_ents = vary_casing(text, entities)
    if new_text != text:
        variants.append([new_text, {"entities": [list(e) for e in new_ents]}])

    # Variant 2: typo injection
    new_text, new_ents = inject_typos(text, entities, rate=0.03)
    if new_text != text:
        variants.append([new_text, {"entities": [list(e) for e in new_ents]}])

    return variants


def main():
    train_path = os.path.join(BASE_DIR, "requirements_ner_train.json")

    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)

    print(f"Original training samples: {len(train_data)}")

    augmented = []
    for text, ann in train_data:
        entities = [tuple(e) for e in ann.get("entities", [])]
        variants = augment_sample(text, entities)
        augmented.extend(variants)

    # Save augmented samples separately (can be merged later)
    out_path = os.path.join(BASE_DIR, "augmented_samples.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(augmented, f, ensure_ascii=False, indent=2)

    print(f"Augmented variants generated: {len(augmented)}")
    print(f"Saved to: {out_path}")
    print(f"NOTE: These are NOT yet merged into train.spacy.")
    print(f"      Merge them if needed after Phase 1 evaluation.")


if __name__ == "__main__":
    main()
