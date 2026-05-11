import argparse
import os
from typing import Any

import spacy

DEFAULT_MODEL_DIR = os.path.join("ner_model", "output", "model-best")


class NERExtractor:

    def __init__(self, model_dir: str = DEFAULT_MODEL_DIR):
        self.nlp = spacy.load(model_dir)
        print(f"NER model loaded from: {model_dir}")

    def extract(self, text: str) -> list[dict[str, Any]]:
        doc = self.nlp(text)
        return [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]

    def extract_grouped(self, text: str) -> dict[str, list[str]]:
        entities = self.extract(text)
        grouped: dict[str, list[str]] = {}
        for ent in entities:
            label = ent["label"]
            if label == "QUALITY":
                label = "QUALITY_ATTRIBUTE"
            grouped.setdefault(label, []).append(ent["text"])
            
        # Refine extracted entities
        return self._refine_extracted_entities(text, grouped)

    def _refine_extracted_entities(
        self, text: str, grouped: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        """
        Rule-based post-processing layer to fix common NER boundary errors
        and merge multi-token entities properly.
        """
        text_lower = text.lower()
        refined = {k: list(v) for k, v in grouped.items()}  # Deep copy

        # 1. Expand incomplete QUALITY_ATTRIBUTEs (e.g., "more" instead of "more reliable")
        if "QUALITY_ATTRIBUTE" in refined:
            qualities = refined["QUALITY_ATTRIBUTE"]
            for i, quality in enumerate(qualities):
                q_lower = quality.lower()
                if q_lower in ["more", "less", "highly", "very"]:
                    # Find what it modifies in the text
                    pos = text_lower.find(q_lower)
                    if pos != -1:
                        # Grab the word right after (e.g. "more reliable")
                        words_after = text[pos + len(q_lower) :].strip().split()
                        if words_after:
                            qualities[i] = f"{quality} {words_after[0]}"

        # 2. Expand incomplete CONSTRAINTs (e.g., "at all" instead of "at all times")
        if "CONSTRAINT" in refined:
            constraints = refined["CONSTRAINT"]
            for i, constraint in enumerate(constraints):
                c_lower = constraint.lower()
                
                # Fix "at all" -> "at all times"
                if c_lower == "at all" and "at all times" in text_lower:
                    constraints[i] = "at all times"
                
                # Fix trailing prepositions
                elif c_lower.endswith((" in", " on", " at", " under", " within")):
                    pos = text_lower.find(c_lower)
                    if pos != -1:
                        # Grab up to 3 more words to complete the phrase
                        words_after = text[pos + len(c_lower) :].strip().split()[:3]
                        if words_after:
                            # Try to stop at punctuation
                            expanded = constraint
                            for word in words_after:
                                expanded += " " + word
                                if any(p in word for p in ".,;!?"):
                                    expanded = expanded.rstrip(".,;!?")
                                    break
                            constraints[i] = expanded

        return refined

    def extract_batch(self, texts: list[str]) -> list[list[dict[str, Any]]]:
        return [self.extract(t) for t in texts]

# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract NER entities.")
    parser.add_argument("--model_dir", default=DEFAULT_MODEL_DIR)
    parser.add_argument(
        "--sentence",
        type=str,
        required=True,
        help="Sentence to extract entities from.",
    )
    args = parser.parse_args()

    extractor = NERExtractor(args.model_dir)
    entities = extractor.extract(args.sentence)

    print(f"\nInput: {args.sentence}\n")
    if entities:
        print(f"  {'Text':<25s} {'Label':<25s} {'Span'}")
        print(f"  {'-'*25} {'-'*25} {'-'*10}")
        for ent in entities:
            span = f"[{ent['start']}:{ent['end']}]"
            print(f"  {ent['text']:<25s} {ent['label']:<25s} {span}")
    else:
        print("  No entities found.")
