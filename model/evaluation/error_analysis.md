# NER Error Analysis Report

Based on evaluation set of ~592 testing samples.

## Top Misclassifications & Boundary Errors:

- **167 occurrences**: Expected FEATURE, got ACTOR
- **78 occurrences**: Boundary Misalignment: True:PRIORITY Predicted:FEATURE
- **37 occurrences**: Boundary Misalignment: True:FEATURE Predicted:ACTOR
- **16 occurrences**: Boundary Misalignment: True:CONSTRAINT Predicted:CONSTRAINT
- **13 occurrences**: Missed Entity (FEATURE)
- **12 occurrences**: Boundary Misalignment: True:FEATURE Predicted:FEATURE
- **11 occurrences**: Missed Entity (ACTOR)
- **9 occurrences**: Missed Entity (ACTION)
- **2 occurrences**: Expected ACTOR, got FEATURE
- **2 occurrences**: Boundary Misalignment: True:ACTION Predicted:ACTOR
- **1 occurrences**: Missed Entity (CONSTRAINT)
- **1 occurrences**: Missed Entity (QUALITY)
- **1 occurrences**: Boundary Misalignment: True:FEATURE Predicted:PRIORITY
- **1 occurrences**: Boundary Misalignment: True:ACTION Predicted:ACTION

## Confusion Matrix

| True \ Pred | ACTION | ACTOR | CONSTRAINT | FEATURE | PRIORITY | QUALITY | O (Missed) |
|---|---|---|---|---|---|---|---|
| ACTION | 581 | 2 | 0 | 0 | 0 | 0 | 9 |
| ACTOR | 0 | 519 | 0 | 2 | 0 | 0 | 11 |
| CONSTRAINT | 0 | 0 | 517 | 0 | 0 | 0 | 1 |
| FEATURE | 0 | 204 | 0 | 370 | 1 | 0 | 13 |
| PRIORITY | 0 | 0 | 0 | 78 | 422 | 0 | 0 |
| QUALITY | 0 | 0 | 0 | 0 | 0 | 500 | 1 |
| O (False Pos) | 5 | 6 | 7 | 1 | 1 | 0 | - |
