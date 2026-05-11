import os
import random
import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans

# Ensure reproducibility
random.seed(42)

# Entities vocabulary
ACTORS = [
    "Users", "The system", "Admins", "Customers", "Guests", 
    "Managers", "The API", "The mobile app", "The desktop client", "Stakeholders"
]

PRIORITIES = [
    "must", "should", "shall", "will", "is urgently required to", 
    "critically needs to", "is expected to", "has to"
]

ACTIONS = [
    "login", "authenticate", "export", "download", "process", 
    "configure", "sync", "generate", "load", "render", "encrypt", "validate"
]

FEATURES = [
    "dashboard", "reports", "payment gateway", "audit logs", "user settings",
    "passwords", "credit card data", "PDF files", "profile pictures",
    "search functionality", "checkout flow", "database records"
]

CONSTRAINTS = [
    "within 2 seconds", "under 1 second", "at all times", "during peak hours",
    "without data loss", "on mobile devices", "offline", "in real-time",
    "within 500 milliseconds", "concurrently for 1000 users", "over HTTPS"
]

QUALITIES = [
    "securely", "reliably", "scalably", "with high availability", 
    "seamlessly", "fast", "safely", "smoothly"
]

# Random templates with exactly trackable boundaries
TEMPLATES = [
    # Basic functional: [ACTOR] [PRIORITY] [ACTION] [FEATURE].
    ([ACTORS, PRIORITIES, ACTIONS, FEATURES],
     "{0} {1} be able to {2} {3}."),
    
    # Non-functional with constraint: [ACTOR] [PRIORITY] [ACTION] [FEATURE] [CONSTRAINT].
    ([ACTORS, PRIORITIES, ACTIONS, FEATURES, CONSTRAINTS],
     "{0} {1} {2} {3} {4}."),
    
    # Non-functional with quality and constraint
    ([ACTORS, PRIORITIES, ACTIONS, FEATURES, QUALITIES, CONSTRAINTS],
     "{0} {1} {2} {3} {4} {5}."),
     
    # Passive structure: [FEATURE] [PRIORITY] be [ACTION]ed by [ACTOR]
    ([FEATURES, PRIORITIES, ACTIONS, ACTORS, CONSTRAINTS],
     "The {0} {1} be {2}ed by {3} {4}."),
     
    # Urgent prefix
    ([PRIORITIES, ACTORS, ACTIONS, FEATURES, CONSTRAINTS],
     "Urgent: {1} {2} {3} {4}."),
]

LABEL_MAP = {
    id(ACTORS): "ACTOR",
    id(PRIORITIES): "PRIORITY_INDICATOR",
    id(ACTIONS): "ACTION",
    id(FEATURES): "FEATURE",
    id(CONSTRAINTS): "CONSTRAINT",
    id(QUALITIES): "QUALITY_ATTRIBUTE"
}

def generate_sample(nlp):
    # Select random template
    pools, template_str = random.choice(TEMPLATES)
    
    # Pick random items and track their strings
    selections = []
    labels = []
    
    for pool in pools:
        sel = random.choice(pool)
        selections.append(sel)
        labels.append(LABEL_MAP[id(pool)])
        
    # Render sentence
    sentence = template_str.format(*selections)
    
    # Create spaCy Doc
    doc = nlp.make_doc(sentence)
    
    # Find spans manually
    spans = []
    for sel_text, label in zip(selections, labels):
        # search string
        start = sentence.find(sel_text)
        if start != -1:
            end = start + len(sel_text)
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span:
                spans.append(span)
                
    # Add manual urgent marker if exists
    if sentence.startswith("Urgent:"):
        urgent_span = doc.char_span(0, 6, label="PRIORITY_INDICATOR", alignment_mode="contract")
        if urgent_span:
            spans.append(urgent_span)
            
    # Remove overlaps
    doc.ents = filter_spans(spans)
    return doc

def build_dataset(output_path, num_samples, nlp):
    db = DocBin()
    docs_created = 0
    # Generate until we hit target (some might fail char_span alignment due to tokenization edges)
    while docs_created < num_samples:
        doc = generate_sample(nlp)
        if len(doc.ents) > 1: # ensure at least 2 entities
            db.add(doc)
            docs_created += 1
            
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    db.to_disk(output_path)
    print(f"Generated {docs_created} labeled sentences -> {output_path}")

if __name__ == "__main__":
    nlp = spacy.blank("en")
    build_dataset("data/ner/train.spacy", 350, nlp)
    build_dataset("data/ner/dev.spacy", 60, nlp)
