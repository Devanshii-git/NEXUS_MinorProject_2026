"""
Audit and fix dataset boundaries to correct overlapping or bleeding entities
in the original training JSON, especially for FEATURE tags.
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_PATH = os.path.join(BASE_DIR, "requirements_ner_train.json")

def clean_span(text: str, start: int, end: int, label: str):
    span_text = text[start:end]
    new_start = start
    new_end = end
    
    if label == "FEATURE":
        # Trim leading articles
        match = re.search(r"^(the|a|an)\s+", span_text, re.IGNORECASE)
        if match:
            new_start += len(match.group(0))
            span_text = text[new_start:new_end]
            
        # Trim trailing prepositions/connectors
        # e.g., "dashboard within", "payment gateway under"
        match = re.search(r"\s+(within|under|before|after|in|on|at|for|to|with|by|from|into|as|such that|so that)$", span_text, re.IGNORECASE)
        if match:
            new_end -= len(match.group(0))
            span_text = text[new_start:new_end]
            
        # Trim trailing punctuation
        match = re.search(r"[.,;:!?\s]+$", span_text)
        if match:
            new_end -= len(match.group(0))
            span_text = text[new_start:new_end]
            
    return new_start, new_end, label

def main():
    if not os.path.exists(TRAIN_PATH):
        print(f"File not found: {TRAIN_PATH}")
        return
        
    with open(TRAIN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    fixed_count = 0
    
    for item in data:
        text, annotations = item
        entities = annotations.get("entities", [])
        new_entities = []
        
        for start, end, label in entities:
            n_s, n_e, n_l = clean_span(text, start, end, label)
            if n_s != start or n_e != end:
                fixed_count += 1
            if n_e > n_s:
                new_entities.append([n_s, n_e, n_l])
                
        # Handle overlaps by keeping the shorter one or the higher priority one
        new_entities.sort(key=lambda x: (x[0], -x[1]))
        final_entities = []
        for e in new_entities:
            # Check overlap
            overlap = False
            for fe in final_entities:
                # If e starts before fe ends and e ends after fe starts
                if e[0] < fe[1] and e[1] > fe[0]:
                    overlap = True
                    break
            if not overlap:
                final_entities.append(e)
                
        annotations["entities"] = final_entities

    with open(TRAIN_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Audited {len(data)} samples. Fixed {fixed_count} bleeding boundary spans.")

if __name__ == "__main__":
    main()
