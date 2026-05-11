import json
import os
import spacy
from spacy.scorer import Scorer
from spacy.training import Example

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def evaluate_dataset(nlp, json_path, dataset_name, generate_visuals=False, output_dir=None):
    print(f"\nLoading {dataset_name} dataset from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    scorer = Scorer()
    examples = []
    skipped = 0
    
    confusions = {}
    labels_set = set()
    label_confusion = {}
    
    total_strict = 0
    total_partial = 0
    total_missed = 0
    total_gold_count = 0
    
    for text, annotations in data:
        doc_pred = nlp(text)
        doc_gold = nlp.make_doc(text)
        spans = []
        for start, end, label in annotations.get("entities", []):
            span = doc_gold.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                span = doc_gold.char_span(start, end, label=label, alignment_mode="expand")
            if span:
                spans.append(span)
        
        try:
            doc_gold.ents = spans
            example = Example(doc_pred, doc_gold)
            examples.append(example)
            
            if generate_visuals:
                pred_ents = {(e.start_char, e.end_char): e.label_ for e in doc_pred.ents}
                gold_ents = {(e.start_char, e.end_char): e.label_ for e in doc_gold.ents}
                
                total_gold_count += len(gold_ents)
                
                for lbl in gold_ents.values(): labels_set.add(lbl)
                for lbl in pred_ents.values(): labels_set.add(lbl)
                
                matched_pred = set()
                
                for g_bounds, g_lbl in gold_ents.items():
                    if g_lbl not in label_confusion: label_confusion[g_lbl] = {}
                    
                    if g_bounds in pred_ents:
                        p_lbl = pred_ents[g_bounds]
                        label_confusion[g_lbl][p_lbl] = label_confusion[g_lbl].get(p_lbl, 0) + 1
                        matched_pred.add(g_bounds)
                        if p_lbl != g_lbl:
                            combo = f"Expected {g_lbl}, got {p_lbl}"
                            confusions[combo] = confusions.get(combo, 0) + 1
                        else:
                            total_strict += 1
                    else:
                        matched = False
                        for p_bounds, p_lbl in pred_ents.items():
                            if not (p_bounds[1] <= g_bounds[0] or p_bounds[0] >= g_bounds[1]):
                                combo = f"Boundary Misalignment: True:{g_lbl} Predicted:{p_lbl}"
                                confusions[combo] = confusions.get(combo, 0) + 1
                                label_confusion[g_lbl][p_lbl] = label_confusion[g_lbl].get(p_lbl, 0) + 1
                                matched_pred.add(p_bounds)
                                matched = True
                                total_partial += 1
                                break
                        if not matched:
                            combo = f"Missed Entity ({g_lbl})"
                            confusions[combo] = confusions.get(combo, 0) + 1
                            label_confusion[g_lbl]['O (Missed)'] = label_confusion[g_lbl].get('O (Missed)', 0) + 1
                            total_missed += 1
                            
                for p_bounds, p_lbl in pred_ents.items():
                    if p_bounds not in matched_pred:
                        if 'O (False Pos)' not in label_confusion: label_confusion['O (False Pos)'] = {}
                        label_confusion['O (False Pos)'][p_lbl] = label_confusion['O (False Pos)'].get(p_lbl, 0) + 1
                
        except Exception as e:
            skipped += 1
            
    metrics = scorer.score(examples)
    f1 = metrics.get('ents_f', 0) * 100
    
    print(f"--- {dataset_name.upper()} RESULTS ---")
    print(f"Samples: {len(examples)} | F1-Score: {f1:.2f}%")
    if generate_visuals and total_gold_count > 0:
        strict_rate = (total_strict / total_gold_count) * 100
        partial_rate = (total_partial / total_gold_count) * 100
        missed_rate = (total_missed / total_gold_count) * 100
        print(f"  Strict Match Rate : {strict_rate:.2f}%")
        print(f"  Partial Match Rate: {partial_rate:.2f}%")
        print(f"  Missed Rate       : {missed_rate:.2f}%")
    
    if generate_visuals and output_dir:
        print(f"\n================ NER TEST METRICS ================")
        print(f"Overall Precision   : {metrics.get('ents_p', 0)*100:.2f}%")
        print(f"Overall Recall      : {metrics.get('ents_r', 0)*100:.2f}%")
        print(f"Overall F1-Score    : {f1:.2f}%")
        
        print("\n--- PER LABEL STATS ---")
        ents_per_type = metrics.get('ents_per_type', {})
        for ent_type, stats in ents_per_type.items():
            print(f"{ent_type.ljust(15)}: P={stats['p']*100:5.2f}% | R={stats['r']*100:5.2f}% | F1={stats['f']*100:5.2f}%")

        error_md = os.path.join(os.path.dirname(output_dir), "evaluation", "error_analysis.md")
        top_errors = sorted(confusions.items(), key=lambda x: x[1], reverse=True)[:15]
        
        md_content = "# NER Error Analysis Report\n\n"
        md_content += f"Based on evaluation set of ~{len(examples)} testing samples.\n\n"
        md_content += "## Top Misclassifications & Boundary Errors:\n\n"
        
        if len(top_errors) == 0:
            md_content += "No prominent errors detected! Model matches test set accurately.\n"
        else:
            for err_type, count in top_errors:
                md_content += f"- **{count} occurrences**: {err_type}\n"
        
        all_labels = sorted(list(labels_set))
        md_content += "\n## Confusion Matrix\n\n"
        cols = ["True \\ Pred"] + all_labels + ["O (Missed)"]
        md_content += "| " + " | ".join(cols) + " |\n"
        md_content += "|" + "|".join(["---"] * len(cols)) + "|\n"
        
        for t_lbl in all_labels + ["O (False Pos)"]:
            row = [t_lbl]
            for p_lbl in all_labels + ["O (Missed)"]:
                if t_lbl == "O (False Pos)" and p_lbl == "O (Missed)":
                    row.append("-")
                else:
                    count = label_confusion.get(t_lbl, {}).get(p_lbl, 0)
                    row.append(str(count))
            md_content += "| " + " | ".join(row) + " |\n"
        
        os.makedirs(os.path.dirname(error_md), exist_ok=True)
        with open(error_md, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        print(f"\nWritten Error Analysis artifact to: {error_md}")

        # VISUALIZATIONS
        os.makedirs(output_dir, exist_ok=True)
        
        all_t_labels = all_labels + ["O (False Pos)"]
        all_p_labels = all_labels + ["O (Missed)"]
        
        cm_data = []
        for t_lbl in all_t_labels:
            row = []
            for p_lbl in all_p_labels:
                if t_lbl == "O (False Pos)" and p_lbl == "O (Missed)":
                    row.append(0)
                else:
                    row.append(label_confusion.get(t_lbl, {}).get(p_lbl, 0))
            cm_data.append(row)
            
        df_cm = pd.DataFrame(cm_data, index=all_t_labels, columns=all_p_labels)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(df_cm, annot=True, fmt='d', cmap='Blues')
        plt.title("NER Confusion Matrix")
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.tight_layout()
        cm_path = os.path.join(output_dir, "confusion_matrix_ner.png")
        plt.savefig(cm_path, dpi=150)
        plt.close()
        
        perf_path = ""
        if ents_per_type:
            labels = list(ents_per_type.keys())
            p_scores = [ents_per_type[lbl]['p'] * 100 for lbl in labels]
            r_scores = [ents_per_type[lbl]['r'] * 100 for lbl in labels]
            f1_scores = [ents_per_type[lbl]['f'] * 100 for lbl in labels]
            
            x = np.arange(len(labels))
            width = 0.25
            
            fig, ax = plt.subplots(figsize=(10, 6))
            rects1 = ax.bar(x - width, p_scores, width, label='Precision', color='#3498db')
            rects2 = ax.bar(x, r_scores, width, label='Recall', color='#2ecc71')
            rects3 = ax.bar(x + width, f1_scores, width, label='F1-Score', color='#f39c12')
            
            ax.set_ylabel('Scores (%)')
            ax.set_title('NER Performance per Entity Type')
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.legend()
            ax.set_ylim([0, 105])
            
            plt.tight_layout()
            perf_path = os.path.join(output_dir, "ner_performance_metrics.png")
            plt.savefig(perf_path, dpi=150)
            plt.close()
            
        print(f"Saved confusion matrix to: {cm_path}")
        if perf_path:
            print(f"Saved performance metrics to: {perf_path}")
            
    return f1

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(base_dir)
    
    model_dir = os.path.join(project_dir, "ner_model", "output", "model-best")
    train_json = os.path.join(project_dir, "data", "ner", "requirements_ner_train.json")
    dev_json = os.path.join(project_dir, "data", "ner", "requirements_ner_dev.json")
    test_json = os.path.join(project_dir, "data", "ner", "requirements_ner_test.json")
    output_dir = os.path.join(project_dir, "output")
    
    if not os.path.exists(model_dir):
        print(f"Waiting for model to complete training (not found: {model_dir})")
        return
        
    print(f"Loading trained model from {model_dir}...")
    nlp = spacy.load(model_dir)
    
    print("\n" + "="*50)
    print("NER MODEL GENERALIZATION EVALUATION")
    print("="*50)
    
    train_f1 = evaluate_dataset(nlp, train_json, "Train")
    dev_f1 = evaluate_dataset(nlp, dev_json, "Dev")
    test_f1 = evaluate_dataset(nlp, test_json, "Test", generate_visuals=True, output_dir=output_dir)
    
    print("\n" + "="*50)
    print("GENERALIZATION GAP SUMMARY")
    print("="*50)
    print(f"Train F1 : {train_f1:.2f}%")
    print(f"Dev F1   : {dev_f1:.2f}%")
    print(f"Test F1  : {test_f1:.2f}%")
    
    train_test_gap = train_f1 - test_f1
    print(f"\nTrain-Test Gap: {train_test_gap:.2f}%")
    if train_test_gap > 5.0:
        print("WARNING: Gap > 5%. The model is likely still overfitting.")
    else:
        print("GOOD: Gap <= 5%. The model is generalizing well!")

if __name__ == "__main__":
    main()
