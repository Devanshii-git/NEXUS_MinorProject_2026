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

    # Check for API key (Gemini)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Please set it before running this script.")
        return

    # Gemini's OpenAI-compatible endpoint
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    model_name = "gemini-3.1-flash-lite"

    true_labels = []
    pred_labels = []
    print(f"Processing {len(df)} sentences using {model_name}...")

    for idx, row in df.iterrows():
        sentence = row["sentence"]
        true_label = int(row["label"])  # Assuming 1 is requirement, 0 is not
        prompt = f"""You are an expert software engineer.
Determine if the following sentence describes a software requirement (functional or non-functional).
Answer ONLY with "YES" if it is a requirement, or "NO" if it is not. Do not include any other text.
Sentence: "{sentence}"
"""

        max_retries = 5
        retry_delay = 5  # Start with 5 seconds backoff

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=200
                )
                answer = response.choices[0].message.content.strip().upper()

                # Parse YES/NO to 1/0
                pred = 1 if "YES" in answer else 0
                true_labels.append(true_label)
                pred_labels.append(pred)

                if (idx + 1) % 10 == 0:
                    print(f"Processed {idx + 1}/{len(df)} sentences...")

                # MANDATORY DELAY: Free tier limit is 15 RPM. 60s / 15 = 4s.
                # Sleep 4.1s to guarantee we stay under the limit.
                time.sleep(4.1)
                break  # Success! Break out of the retry loop

            except Exception as e:
                error_msg = str(e)
                # If we get a rate limit (429), quota, or Too Many Requests error
                if "429" in error_msg or "Too Many Requests" in error_msg or "quota" in error_msg.lower():
                    print(f"Rate limited at index {idx}. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff (5s, 10s, 20s...)
                else:
                    # For other types of errors, just log it, assign 0, and move on
                    print(f"API Error at index {idx}: {e}")
                    true_labels.append(true_label)
                    pred_labels.append(0)
                    time.sleep(4.1)
                    break

    # Calculate Metrics
    acc = accuracy_score(true_labels, pred_labels)
    prec = precision_score(true_labels, pred_labels, zero_division=0)
    rec = recall_score(true_labels, pred_labels, zero_division=0)
    f1 = f1_score(true_labels, pred_labels, zero_division=0)

    print("\n--- LLM Baseline Results ---")
    print(f"Model:     {model_name}")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    # Save results and exact prompt for the paper
    results = {
        "model": model_name,
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

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_baseline_results.json")
    run_llm_baseline(test_csv=csv_path, output_file=out_path)
