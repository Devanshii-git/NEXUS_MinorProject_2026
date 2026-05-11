import json
import os
import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans

# We load the blank English tokenizer
nlp = spacy.blank("en")

def convert(input_path, output_path):
    doc_bin = DocBin()
    skipped = 0
    total = 0
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for text, annotations in data:
        doc = nlp.make_doc(text)
        spans = []
        
        for start, end, label in annotations.get("entities", []):
            total += 1
            # The user dataset offsets are exact character offsets
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                span = doc.char_span(start, end, label=label, alignment_mode="expand")
            if span is not None:
                spans.append(span)
            else:
                skipped += 1
                
        # Filter overlaps (though the dataset is perfectly clean anyway)
        doc.ents = filter_spans(spans)
        doc_bin.add(doc)
        
    doc_bin.to_disk(output_path)
    print(f"[{os.path.basename(input_path)}] Converted {len(data)} docs. Processed {total} entities. Skipped {skipped}.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(base_dir))
    
    # Input paths
    input_train = os.path.join(base_dir, "requirements_ner_train.json")
    input_dev = os.path.join(base_dir, "requirements_ner_dev.json")
    input_test = os.path.join(base_dir, "requirements_ner_test.json")
    
    # Output paths
    output_train = os.path.join(base_dir, "train.spacy")
    output_dev = os.path.join(base_dir, "dev.spacy")
    output_test = os.path.join(base_dir, "test.spacy")
    
    convert(input_train, output_train)
    convert(input_dev, output_dev)
    convert(input_test, output_test)
    
    print("\n✓ Database perfectly vectorized into .spacy")
