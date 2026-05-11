# Requirements NER Dataset Builder

This folder contains a reproducible pipeline that merges the available requirements sources in this workspace into one cleaned, deduplicated, spaCy-ready NER dataset.

## Inputs

- `C:\Users\Devanshi\Desktop\dataset\requirements_ner_dataset_5000_v3.json`
- `C:\Users\Devanshi\Desktop\dataset\FR_NFR_dataset\FR_NFR_Dataset.xlsx`
- `C:\Users\Devanshi\Desktop\dataset\se-requirements-classification-master\1-exploratory-analysis\data\PROMISE_exp.csv`
- `C:\Users\Devanshi\Desktop\dataset\se-requirements-classification-master\1-exploratory-analysis\data\nfr.csv`

## Outputs

- `output\unified_text_dataset.jsonl`
- `output\requirements_ner_spacy.json`
- `output\requirements_ner_records.jsonl`
- `output\dataset_stats.json`
- `output\annotation_consistency_report.json`
- `output\annotation_audit_samples.jsonl`
- `output\dataset_summary.md`

## Run

```powershell
python .\requirements_ner_dataset\build_dataset.py
```
