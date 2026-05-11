from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
CLEAN_DIR = OUTPUT_DIR / "cleaned"

RECORDS_PATH = OUTPUT_DIR / "requirements_ner_records.jsonl"
FULL_SPACY_JSON_PATH = OUTPUT_DIR / "requirements_ner_spacy.json"
SPLIT_PATHS = {
    "train": OUTPUT_DIR / "requirements_ner_train.json",
    "dev": OUTPUT_DIR / "requirements_ner_dev.json",
    "test": OUTPUT_DIR / "requirements_ner_test.json",
}


@dataclass
class RepairStats:
    total_samples: int = 0
    total_entities: int = 0
    invalid_entities_before: int = 0
    corrected_entities: int = 0
    removed_entities: int = 0
    removed_samples: int = 0


def classify_invalid_span(text: str, start: int, end: int, expected: str) -> str:
    if start < 0 or end < start or end > len(text):
        return "out_of_bounds"

    actual = text[start:end]
    if actual == expected:
        return "valid"
    if start > 0 and text[start - 1 : end - 1] == expected:
        return "off_by_one_left"
    if end < len(text) and text[start + 1 : end + 1] == expected:
        return "off_by_one_right"
    if actual.strip() == expected.strip() and actual != expected:
        return "extra_whitespace"
    if actual and (actual in expected or expected in actual):
        return "truncated_or_extended"
    return "mismatch"


def find_candidate_positions(text: str, entity_text: str) -> list[tuple[int, int]]:
    candidates: list[tuple[int, int]] = []
    start = 0
    while True:
        idx = text.find(entity_text, start)
        if idx == -1:
            break
        candidates.append((idx, idx + len(entity_text)))
        start = idx + 1

    if candidates:
        return candidates

    lowered_text = text.lower()
    lowered_entity = entity_text.lower()
    start = 0
    while True:
        idx = lowered_text.find(lowered_entity, start)
        if idx == -1:
            break
        candidates.append((idx, idx + len(entity_text)))
        start = idx + 1

    if candidates:
        return candidates

    stripped = entity_text.strip()
    if stripped and stripped != entity_text:
        return find_candidate_positions(text, stripped)

    return []


def choose_best_candidate(
    text: str,
    expected: str,
    original_start: int,
    original_end: int,
    used_ranges: list[tuple[int, int]],
) -> tuple[int, int] | None:
    candidates = find_candidate_positions(text, expected)
    if not candidates:
        return None

    def overlaps(candidate: tuple[int, int]) -> bool:
        start, end = candidate
        return any(not (end <= left or start >= right) for left, right in used_ranges)

    available = [candidate for candidate in candidates if not overlaps(candidate)]
    if not available:
        return None

    def sort_key(candidate: tuple[int, int]) -> tuple[int, int, int]:
        start, end = candidate
        return (abs(start - original_start), abs(end - original_end), start)

    return min(available, key=sort_key)


def sanitize_entities(text: str, entities: list[dict[str, Any]], stats: RepairStats) -> tuple[list[dict[str, Any]], Counter[str]]:
    cleaned: list[dict[str, Any]] = []
    used_ranges: list[tuple[int, int]] = []
    error_patterns: Counter[str] = Counter()

    for entity in sorted(entities, key=lambda item: (item["start"], item["end"], item["label"])):
        stats.total_entities += 1
        start = int(entity["start"])
        end = int(entity["end"])
        label = entity["label"]
        expected = entity["text"]

        pattern = classify_invalid_span(text, start, end, expected)
        if pattern != "valid":
            stats.invalid_entities_before += 1
            error_patterns[pattern] += 1
            corrected = choose_best_candidate(text, expected, start, end, used_ranges)
            if corrected is None:
                stats.removed_entities += 1
                continue
            start, end = corrected
            stats.corrected_entities += 1

        actual = text[start:end]
        if not actual or actual != expected:
            stats.removed_entities += 1
            error_patterns["unfixable_mismatch"] += 1
            continue

        if any(not (end <= left or start >= right) for left, right in used_ranges):
            stats.removed_entities += 1
            error_patterns["overlap_after_fix"] += 1
            continue

        used_ranges.append((start, end))
        cleaned.append({"start": start, "end": end, "label": label, "text": actual})

    return cleaned, error_patterns


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            records.append(json.loads(line))
    return records


def export_spacy_json(records: list[dict[str, Any]], output_path: Path) -> None:
    payload = []
    for record in records:
        payload.append(
            [
                record["text"],
                {
                    "entities": [
                        [entity["start"], entity["end"], entity["label"]]
                        for entity in record["entities"]
                    ]
                },
            ]
        )
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as file_obj:
        for record in records:
            file_obj.write(json.dumps(record, ensure_ascii=False) + "\n")


def rebuild_split(
    split_name: str,
    split_path: Path,
    record_map: dict[str, dict[str, Any]],
    split_summary: dict[str, Any],
) -> None:
    split_data = json.loads(split_path.read_text(encoding="utf-8"))
    rebuilt = []
    kept_entities = 0
    removed_samples = 0

    for text, _annotations in split_data:
        record = record_map.get(text)
        if record is None:
            removed_samples += 1
            continue
        rebuilt.append(
            [
                text,
                {
                    "entities": [
                        [entity["start"], entity["end"], entity["label"]]
                        for entity in record["entities"]
                    ]
                },
            ]
        )
        kept_entities += len(record["entities"])

    output_path = CLEAN_DIR / f"requirements_ner_{split_name}.json"
    output_path.write_text(json.dumps(rebuilt, indent=2, ensure_ascii=False), encoding="utf-8")
    split_summary[split_name] = {
        "samples": len(rebuilt),
        "entities": kept_entities,
        "removed_samples": removed_samples,
        "output": str(output_path),
    }


def build_report(
    stats: RepairStats,
    pattern_counts: Counter[str],
    label_counts: Counter[str],
    cleaned_records: list[dict[str, Any]],
    split_summary: dict[str, Any],
) -> dict[str, Any]:
    valid_samples = len(cleaned_records)
    samples_with_entities = sum(1 for record in cleaned_records if record["entities"])
    sample_entries = []
    for record in cleaned_records[:5]:
        sample_entries.append(
            {
                "text": record["text"],
                "verified_entities": [
                    {
                        "start": entity["start"],
                        "end": entity["end"],
                        "label": entity["label"],
                        "text": record["text"][entity["start"] : entity["end"]],
                    }
                    for entity in record["entities"][:6]
                ],
            }
        )

    return {
        "summary": {
            "total_samples": stats.total_samples,
            "valid_samples": valid_samples,
            "removed_samples": stats.removed_samples,
            "samples_with_entities": samples_with_entities,
            "total_entities_after_cleaning": sum(len(record["entities"]) for record in cleaned_records),
            "invalid_entities_before_cleaning": stats.invalid_entities_before,
            "invalid_entity_percentage": round(
                (stats.invalid_entities_before / stats.total_entities * 100) if stats.total_entities else 0.0,
                4,
            ),
            "corrected_entities": stats.corrected_entities,
            "removed_entities": stats.removed_entities,
            "label_distribution": dict(label_counts),
        },
        "common_error_patterns": dict(pattern_counts.most_common()),
        "split_summary": split_summary,
        "sample_corrected_entries": sample_entries,
    }


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    stats = RepairStats()
    pattern_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()

    raw_records = load_records(RECORDS_PATH)
    cleaned_records: list[dict[str, Any]] = []

    for record in raw_records:
        stats.total_samples += 1
        cleaned_entities, record_patterns = sanitize_entities(record["text"], record.get("entities", []), stats)
        pattern_counts.update(record_patterns)
        if not cleaned_entities:
            stats.removed_samples += 1
            continue

        cleaned_record = dict(record)
        cleaned_record["entities"] = cleaned_entities
        cleaned_records.append(cleaned_record)
        for entity in cleaned_entities:
            label_counts[entity["label"]] += 1

    record_map = {record["text"]: record for record in cleaned_records}
    split_summary: dict[str, Any] = {}
    for split_name, split_path in SPLIT_PATHS.items():
        rebuild_split(split_name, split_path, record_map, split_summary)

    write_jsonl(cleaned_records, CLEAN_DIR / "requirements_ner_records.cleaned.jsonl")
    export_spacy_json(cleaned_records, CLEAN_DIR / "requirements_ner_spacy.cleaned.json")

    report = build_report(stats, pattern_counts, label_counts, cleaned_records, split_summary)
    report_path = CLEAN_DIR / "offset_repair_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    summary_path = CLEAN_DIR / "offset_repair_summary.md"
    summary_lines = [
        "# Offset Repair Summary",
        "",
        f"- Samples processed: {report['summary']['total_samples']}",
        f"- Valid samples kept: {report['summary']['valid_samples']}",
        f"- Removed samples: {report['summary']['removed_samples']}",
        f"- Total entities after cleaning: {report['summary']['total_entities_after_cleaning']}",
        f"- Invalid entities before cleaning: {report['summary']['invalid_entities_before_cleaning']}",
        f"- Invalid entity percentage: {report['summary']['invalid_entity_percentage']}%",
        f"- Corrected entities: {report['summary']['corrected_entities']}",
        f"- Removed entities: {report['summary']['removed_entities']}",
        "",
        "## Common Error Patterns",
    ]
    if pattern_counts:
        summary_lines.extend(f"- {pattern}: {count}" for pattern, count in pattern_counts.most_common())
    else:
        summary_lines.append("- No invalid span patterns detected.")
    summary_lines.extend(
        [
            "",
            "## Cleaned Outputs",
            f"- Records: {CLEAN_DIR / 'requirements_ner_records.cleaned.jsonl'}",
            f"- Full spaCy-format JSON: {CLEAN_DIR / 'requirements_ner_spacy.cleaned.json'}",
        ]
    )
    for split_name in SPLIT_PATHS:
        summary_lines.append(f"- {split_name.title()} split: {CLEAN_DIR / f'requirements_ner_{split_name}.json'}")
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(json.dumps(report["summary"], indent=2))
    print(f"\nWrote cleaned outputs to: {CLEAN_DIR}")


if __name__ == "__main__":
    main()
