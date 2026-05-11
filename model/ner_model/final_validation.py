import time
import spacy
import os

DEFAULT_MODEL_DIR = os.path.join("ner_model", "output", "model-best")

EDGE_CASES = [
    # Extremely short
    "login",
    "admin dashboard",
    "user access",
    
    # Highly noisy / informal
    "plz fix the db real quick under 1 sec",
    "bruh the payment gateway is ded during peak hours",
    "add dark mode to profile tbh",
    
    # Ambiguous verbs/nouns
    "monitor the monitor",
    "report the report to the manager",
    "log the audit log",
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, DEFAULT_MODEL_DIR)

    print(f"Loading NER model from: {model_path} ...\n")
    try:
        nlp = spacy.load(model_path)
    except Exception as e:
        print(f"Could not load model. Error: {e}")
        return

    print("=" * 60)
    print("1. EDGE-CASE & NOISY INPUT TESTING")
    print("=" * 60)
    
    for text in EDGE_CASES:
        doc = nlp(text)
        print(f"\nInput: '{text}'")
        if not doc.ents:
            print("  -> [No entities detected]")
        for ent in doc.ents:
            print(f"  -> [{ent.label_:>10}] : {ent.text}")
            
    print("\n" + "=" * 60)
    print("2. STABILITY CHECK (Consistency over multiple runs)")
    print("=" * 60)
    test_str = "The admin must update the payment gateway within 2 seconds"
    first_run_ents = [(e.text, e.label_) for e in nlp(test_str).ents]
    stable = True
    for _ in range(50):
        doc = nlp(test_str)
        ents = [(e.text, e.label_) for e in doc.ents]
        if ents != first_run_ents:
            stable = False
            break
            
    if stable:
        print(f"[OK] Model is completely deterministic and stable across 50 iterations.")
    else:
        print(f"[FAIL] Model produced inconsistent predictions across iterations.")

    print("\n" + "=" * 60)
    print("3. LATENCY CHECK")
    print("=" * 60)
    
    warmup_str = "This is a warmup string."
    for _ in range(10):
        _ = nlp(warmup_str)
        
    start_time = time.time()
    iters = 100
    for _ in range(iters):
        _ = nlp(test_str)
    end_time = time.time()
    
    avg_latency = (end_time - start_time) / iters * 1000  # in ms
    print(f"Average Inference Latency (CPU/GPU): {avg_latency:.2f} ms per sentence")
    
    if avg_latency < 50:
        print("[OK] Latency is excellent (< 50ms), ready for real-time processing.")
    elif avg_latency < 200:
        print("[OK] Latency is acceptable (< 200ms).")
    else:
        print("[WARNING] Latency is high (> 200ms). Consider ONNX export or quantization for production.")
        
    print("\nValidation Complete.")

if __name__ == "__main__":
    main()
