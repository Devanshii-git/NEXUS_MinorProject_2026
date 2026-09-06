import os
import json
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from openai import OpenAI
import time

def run_llm_baseline(
    test_csv="data/requirement_classification/test.csv",
    output_file="gpt_baseline_results.json"
):
    print("Starting LLM Baseline Evaluation...")
    
    if not os.path.exists(test_csv):
        print(f"Error: Could not find {test_csv}")
        return
        
    df = pd.read_csv(test_csv)
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it before running this script.")
        return
        
    client = OpenAI(api_key=api_key)
    
    true_labels = []
    pred_labels = []
    
    print(f"Processing {len(df)} sentences using GPT-4o-mini...")
    
    for idx, row in df.iterrows():
        sentence = row["sentence"]
        true_label = int(row["label"])  # Assuming 1 is requirement, 0 is not
        
        prompt = f"""You are an expert software engineer.
Determine if the following sentence describes a software requirement (functional or non-functional).
Answer ONLY with "YES" if it is a requirement, or "NO" if it is not. Do not include any other text.

Sentence: "{sentence}"
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )
            answer = response.choices[0].message.content.strip().upper()
            
            # Parse YES/NO to 1/0
            pred = 1 if "YES" in answer else 0
            
            true_labels.append(true_label)
            pred_labels.append(pred)
            
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(df)} sentences...")
                
        except Exception as e:
            print(f"API Error at index {idx}: {e}")
            true_labels.append(true_label)
            pred_labels.append(0) # Default to 0 on error
            time.sleep(2) # Small backoff
            
    # Calculate Metrics
    acc = accuracy_score(true_labels, pred_labels)
    prec = precision_score(true_labels, pred_labels, zero_division=0)
    rec = recall_score(true_labels, pred_labels, zero_division=0)
    f1 = f1_score(true_labels, pred_labels, zero_division=0)
    
    print("\n--- LLM Baseline Results (GPT-4o-mini) ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    
    # Save results and exact prompt for the paper
    results = {
        "model": "gpt-4o-mini",
        "dataset_size": len(true_labels),
        "prompt_used": prompt,
        "metrics": {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1
        }
    }
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    # Handle paths depending on where it's executed
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "requirement_classification", "test.csv")
    
    # Fallback to current working directory if data not found there
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.getcwd(), "data", "requirement_classification", "test.csv")
        
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpt_baseline_results.json")
    run_llm_baseline(test_csv=csv_path, output_file=out_path)
