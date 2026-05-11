import argparse
import os
import spacy

DEFAULT_MODEL_DIR = os.path.join("ner_model", "output", "model-best")

REAL_WORLD_SAMPLES = [
    # 1. Slack message with typos and informal boundary words
    "hey, admin panel is completely broken for mobile users under heavy load, we need to fix it within 2 hours.",
    
    # 2. Jira ticket summary
    "As a premium user I want the payment gateway to load securely so that I don't get double charged after authentication.",
    
    # 3. Quick ping
    "the developers can't access the audit log during peak hours, is it down?",
    
    # 4. Feature request
    "Can we add a dark mode to the profile settings for the support team?",
    
    # 5. Urgent bug
    "System throws 500 when operator tries to download the user list in real-time.",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, args.model_dir)

    print(f"Loading NER model from: {model_path} ...\n")
    try:
        nlp = spacy.load(model_path)
    except Exception as e:
        print(f"Could not load model. Error: {e}")
        return

    print("=" * 60)
    print("REAL WORLD VALIDATION (SLACK / JIRA SAMPLES)")
    print("=" * 60)

    for i, text in enumerate(REAL_WORLD_SAMPLES):
        doc = nlp(text)
        print(f"\n[{i+1}] Input: {text}")
        if not doc.ents:
            print("  -> No entities detected.")
        else:
            for ent in doc.ents:
                print(f"  -> [{ent.label_:>10}] : {ent.text}")
                
    print("\n" + "=" * 60)
    print("Validation Complete.")

if __name__ == "__main__":
    main()
