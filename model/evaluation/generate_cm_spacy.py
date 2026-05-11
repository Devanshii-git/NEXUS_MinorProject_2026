import os
import spacy
from spacy.tokens import DocBin
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "ner_model", "output", "model-best")
    test_spacy_path = os.path.join(base_dir, "data", "ner", "test.spacy")
    output_dir = os.path.join(base_dir, "output")
    output_img = os.path.join(output_dir, "confusion_matrix_ner.png")

    print(f"Loading NER model from: {model_path} ...")
    nlp = spacy.load(model_path)

    print(f"Loading test data from: {test_spacy_path} ...")
    doc_bin = DocBin().from_disk(test_spacy_path)
    docs_gold = list(doc_bin.get_docs(nlp.vocab))

    labels_set = set()
    label_confusion = {}

    print("Comparing predictions against gold standard...")
    for doc_gold in docs_gold:
        text = doc_gold.text
        doc_pred = nlp(text)

        gold_ents = {(e.start_char, e.end_char): e.label_ for e in doc_gold.ents}
        pred_ents = {(e.start_char, e.end_char): e.label_ for e in doc_pred.ents}

        for lbl in gold_ents.values(): labels_set.add(lbl)
        for lbl in pred_ents.values(): labels_set.add(lbl)

        matched_pred = set()

        for g_bounds, g_lbl in gold_ents.items():
            if g_lbl not in label_confusion: label_confusion[g_lbl] = {}
            
            if g_bounds in pred_ents:
                p_lbl = pred_ents[g_bounds]
                label_confusion[g_lbl][p_lbl] = label_confusion[g_lbl].get(p_lbl, 0) + 1
                matched_pred.add(g_bounds)
            else:
                # Check for partial matches or misses
                matched = False
                for p_bounds, p_lbl in pred_ents.items():
                    if not (p_bounds[1] <= g_bounds[0] or p_bounds[0] >= g_bounds[1]):
                        label_confusion[g_lbl][p_lbl] = label_confusion[g_lbl].get(p_lbl, 0) + 1
                        matched_pred.add(p_bounds)
                        matched = True
                        break
                if not matched:
                    label_confusion[g_lbl]['O (Missed)'] = label_confusion[g_lbl].get('O (Missed)', 0) + 1

        for p_bounds, p_lbl in pred_ents.items():
            if p_bounds not in matched_pred:
                if 'O (False Pos)' not in label_confusion: label_confusion['O (False Pos)'] = {}
                label_confusion['O (False Pos)'][p_lbl] = label_confusion['O (False Pos)'].get(p_lbl, 0) + 1

    all_labels = sorted(list(labels_set))
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

    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(df_cm, annot=True, fmt='d', cmap='Blues')
    plt.title("NER Confusion Matrix (from test.spacy)")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    plt.savefig(output_img, dpi=150)
    plt.close()

    print(f"Confusion matrix saved successfully to: {output_img}")

if __name__ == "__main__":
    main()
