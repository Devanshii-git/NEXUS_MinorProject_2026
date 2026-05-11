import json
import os
from collections import defaultdict

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_checks(splits_dir):
    files = ["requirements_ner_train.json", "requirements_ner_dev.json", "requirements_ner_test.json"]
    
    label_counts = defaultdict(int)
    overlap_errors = 0
    boundary_errors = 0
    # To check label confusion: track (lowercase_entity_text) -> set(labels)
    text_to_labels = defaultdict(set)

    for filename in files:
        path = os.path.join(splits_dir, filename)
        if not os.path.exists(path):
            continue
            
        data = load_data(path)
        
        for text, annotations in data:
            entities = annotations.get("entities", [])
            last_end = -1
            
            # Sort entities by start offset to check overlaps
            entities_sorted = sorted(entities, key=lambda x: x[0])
            
            for start, end, label in entities_sorted:
                label_counts[label] += 1
                
                # Check bounds
                if start >= end or end > len(text) or start < 0:
                    boundary_errors += 1
                    
                # Check overlap
                if start < last_end:
                    overlap_errors += 1
                last_end = max(last_end, end)
                
                # For label confusion check, extract text span
                if 0 <= start < end <= len(text):
                    span_text = text[start:end].lower().strip()
                    if span_text:
                        text_to_labels[span_text].add(label)

    # Calculate confusing spans
    confusing_spans = {k: list(v) for k, v in text_to_labels.items() if len(v) > 1}
    
    report = {
        "label_distribution": dict(label_counts),
        "errors": {
            "overlap_errors": overlap_errors,
            "boundary_errors": boundary_errors
        },
        "ambiguous_spans_count": len(confusing_spans)
    }

    with open(os.path.join(splits_dir, "annotation_consistency_report_2.json"), "w") as f:
        json.dump(report, f, indent=2)
        
    print(json.dumps(report, indent=2))
    print(f"\nExample ambiguous spans: {list(confusing_spans.items())[:5]}")

if __name__ == "__main__":
    splits_dir = os.path.join(os.path.dirname(__file__), "output")
    run_checks(splits_dir)
