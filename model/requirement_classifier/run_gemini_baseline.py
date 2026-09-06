import os
import json
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import time

def run_llm_baseline(
    test_csv="data/requirement_classification/test.csv",
    output_file="requirement_classifier/gemini_baseline_results.json"
):
    print("Starting LLM Baseline Evaluation (Using Gemini-1.5-Flash)...")
    
    if not os.path.exists(test_csv):
        print(f"Error: Could not find {test_csv}")
        return
        
    df = pd.read_csv(test_csv)
    
    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return
        
    try:
        import google.generativeai as genai
    except ImportError:
        print("Error: google-generativeai not installed. Please run: pip install google-generativeai")
        return
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        system_instruction="You are an expert software engineer. Determine if the following sentence describes a software requirement (functional or non-functional). Answer ONLY with 'YES' if it is a requirement, or 'NO' if it is not. Do not include any other text."
    )
    
    true_labels = []
    pred_labels = []
    
    print(f"Processing {len(df)} sentences using Gemini...")
    
    for idx, row in df.iterrows():
        sentence = row["sentence"]
        true_label = int(row["label"])
        
        prompt = f"Sentence: \"{sentence}\""
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.0)
            )
            
            result = response.text.strip().upper()
            result = "".join(c for c in result if c.isalpha())
            
            if "YES" in result:
                pred_label = 1
            else:
                pred_label = 0
                
            pred_labels.append(pred_label)
            true_labels.append(true_label)
            
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(df)} sentences...")
                
            time.sleep(1) # Rate limiting
            
        except Exception as e:
            print(f"Error processing sentence {idx}: {e}")
            pred_labels.append(0)
            true_labels.append(true_label)
            time.sleep(3)
            
    # Calculate metrics
    acc = accuracy_score(true_labels, pred_labels)
    prec = precision_score(true_labels, pred_labels, zero_division=0)
    rec = recall_score(true_labels, pred_labels, zero_division=0)
    f1 = f1_score(true_labels, pred_labels, zero_division=0)
    
    print("\n--- RESULTS ---")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1 Score : {f1:.4f}")
    
    results = {
        "model": "gemini-1.5-flash",
        "dataset_size": len(df),
        "prompt_used": "System: You are an expert software engineer... Prompt: Sentence: \"{sentence}\"",
        "metrics": {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1
        }
    }
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nSaved exact results to {output_file}")

if __name__ == "__main__":
    run_llm_baseline()
