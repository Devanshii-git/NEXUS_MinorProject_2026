# AI-based Requirements Engineering using Text Mining and NLP

> Automatically extract and structure software requirements from stakeholder
> communication sources (emails, Slack messages, Jira comments, meeting transcripts).

---

## Pipeline Architecture

```
Raw Text (email / Slack / transcript)
        │
        ▼
  Sentence Segmentation
        │
        ▼
  Requirement Detection          ← DistilBERT binary classifier
  (Requirement / Not Requirement)
        │  keep requirements only
        ▼
  Named Entity Recognition       ← spaCy 3 + BERT transformer NER
  (ACTOR, FEATURE, QUALITY_ATTRIBUTE, CONDITION, PRIORITY_INDICATOR)
        │
        ▼
  Structured Output (JSON)
```

---

## Project Structure

```
project/
├── data/
│   ├── requirement_classification/
│   │   ├── train.csv              # 60 labelled examples
│   │   └── test.csv               # 20 labelled examples
│   └── ner/
│       ├── train.json             # 30 annotated NER examples
│       ├── dev.json               # 10 annotated NER examples
│       └── convert_to_spacy.py    # JSON → .spacy converter
│
├── requirement_classifier/        # Part 1: Requirement Detection
│   ├── dataset.py                 # PyTorch Dataset + tokenization
│   ├── model.py                   # DistilBERT model wrapper
│   ├── train.py                   # Fine-tuning script
│   ├── evaluate.py                # Evaluation metrics
│   └── inference.py               # Single-sentence inference
│
├── ner_model/                     # Part 2: Named Entity Recognition
│   ├── config.cfg                 # spaCy training config (BERT)
│   ├── train_ner.py               # Training launcher
│   ├── evaluate_ner.py            # Entity-level evaluation
│   └── inference_ner.py           # NER inference wrapper
│
├── inference_pipeline/            # End-to-end pipeline
│   ├── pipeline.py                # Full pipeline class
│   └── example_run.py             # Demo on sample text
│
├── evaluation/
│   └── run_all_evaluations.py     # Combined evaluation report
│
├── requirements.txt
└── README.md                      # ← You are here
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
# Download spaCy English tokenizer (used for data conversion)
python -m spacy download en_core_web_sm
```

### 2. Train the Requirement Classifier

```bash
python -m requirement_classifier.train \
    train_csv data/requirement_classification/train.csv \
    test_csv  data/requirement_classification/test.csv \
    output_dir requirement_classifier/saved_model \
    epochs 5 --batch_size 16 --lr 2e-5
```

### 3. Prepare NER data and train

```bash
# Convert JSON annotations to spaCy binary format
python data/ner/convert_to_spacy.py

# Train NER model (CPU)
python -m spacy train ner_model/config.cfg \
    --output ner_model/output \
    --paths.train data/ner/train.spacy \
    --paths.dev   data/ner/dev.spacy

# Or with GPU:
python -m spacy train ner_model/config.cfg \
    --output ner_model/output \
    --paths.train data/ner/train.spacy \
    --paths.dev   data/ner/dev.spacy \
    --gpu-id 0
```

### 4. Run the full pipeline

**For Raw Text:**
```bash
python -m inference_pipeline.example_run
```

**For Structured Production JSON (Jira, Slack, Email):**
We support ingesting structured JSON payloads natively. Try the built-in mock Jira JSON payload:
```bash
python -m inference_pipeline.example_run_json
```

### 5. Evaluate both models

```bash
python -m evaluation.run_all_evaluations
```

---

## Model Details

### Part 1: Requirement Detection (DistilBERT)

| Aspect          | Detail                                     |
| --------------- | ------------------------------------------ |
| Base model      | `distilbert-base-uncased`                  |
| Task            | Binary classification (Req / Not Req)      |
| Input           | Single sentence                            |
| Output          | Label + confidence score                   |
| Optimizer       | AdamW with linear warm-up                  |
| Metrics         | Accuracy, Precision, Recall, F1            |

**How it works:**
1. Each sentence is tokenised into sub-word tokens by the DistilBERT tokenizer.
2. Tokens pass through 6 transformer encoder layers producing contextualised embeddings.
3. The `[CLS]` token embedding is used as the sentence representation.
4. A linear classification head maps this to 2 logits → softmax → predicted class.

### Part 2: Named Entity Recognition (spaCy + BERT)

| Aspect          | Detail                                     |
| --------------- | ------------------------------------------ |
| Framework       | spaCy 3 + spacy-transformers               |
| Base model      | `bert-base-uncased`                        |
| Entity types    | ACTOR, FEATURE, QUALITY_ATTRIBUTE, CONDITION, PRIORITY_INDICATOR |
| Architecture    | Transition-based NER with transformer listener |
| Metrics         | Entity Precision, Recall, F1 (per type)    |

**How it works:**
1. Text is tokenised by spaCy, then sub-tokenised by BERT's WordPiece tokenizer.
2. BERT produces contextualised token embeddings (768-d).
3. A `TransformerListener` pools sub-word representations back to spaCy token level.
4. The transition-based NER parser predicts BIO-tagged entity spans.

---

## Dataset Recommendations & Training on Custom Data

| Model              | Minimum   | Recommended | Notes                            |
| ------------------ | --------- | ----------- | -------------------------------- |
| Req. Classifier    | 300       | 500–1000    | Balanced classes                 |
| NER Model          | 100       | 300–5000+   | ≥30 examples per entity type     |

### 1. Annotation Tools
If you want to transition from our synthetic dataset to your own team's manual real-world annotations, you can use:
- **[Label Studio](https://labelstud.io/)** — Open-source, supports both text classification and NER span labelling.
- **[Doccano](https://github.com/doccano/doccano)** — Lightweight, NER-friendly.
- **[Prodigy](https://prodi.gy/)** — Commercial, integrates with spaCy.

### 2. Converting Custom Data
Once you annotate your custom data, export it via your annotation tool (e.g., as JSONL) and convert it into spaCy's native binary format:
```bash
python -m spacy convert your_custom_data.json ./data/ner
```
Rename the outputs to `train.spacy` and `dev.spacy` to overwrite the default dataset.

### 3. Scaling Your Config Settings
Real-world data is noisy. Open `ner_model/config.cfg` and change the following settings to optimize for production-scale learning:
- **`max_steps`**: Increase to `2000` or `5000+` to allow for multi-epoch learning.
- **`patience`**: Increase to `500` or `1000`.
- **`eval_frequency`**: Reduce to ~`100`.
- **`grad_factor`**: If your dataset is huge (5000+ sentences), change `grad_factor = 0.0` to `grad_factor = 1.0` inside `[components.ner.model.tok2vec]` to unfreeze the BERT layers and fine-tune the core transformer natively for your organization!

---

## Example End-to-End Output

**Input (raw stakeholder text):**
```
Users are complaining that login is too slow during peak hours.
Good morning everyone.
We should improve login speed.
The meeting is scheduled for tomorrow.
```

**Output (after pipeline):**
```
============================================================
Requirement #1
  Sentence   : Users are complaining that login is too slow during peak hours.
  Confidence : 0.9712
  ACTOR                    : Users
  FEATURE                  : login
  QUALITY_ATTRIBUTE        : slow
  CONDITION                : during peak hours
============================================================
Requirement #2
  Sentence   : We should improve login speed.
  Confidence : 0.9534
  FEATURE                  : login speed
  QUALITY_ATTRIBUTE        : improve
============================================================
```

---

## License

Academic research project — for educational purposes.
