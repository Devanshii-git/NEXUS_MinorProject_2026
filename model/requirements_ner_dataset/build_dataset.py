from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(r"C:\Users\Devanshi\Desktop\dataset")
OUTPUT_DIR = ROOT / "requirements_ner_dataset" / "output"
CUSTOM_PATH = ROOT / "requirements_ner_dataset_5000_v3.json"
FR_NFR_PATH = ROOT / "FR_NFR_dataset" / "FR_NFR_Dataset.xlsx"
PROMISE_PATH = ROOT / "se-requirements-classification-master" / "1-exploratory-analysis" / "data" / "PROMISE_exp.csv"
NFR_PATH = ROOT / "se-requirements-classification-master" / "1-exploratory-analysis" / "data" / "nfr.csv"
PURE_PATH = ROOT / "Pure_Annotate_Dataset.csv"

RANDOM_SEED = 17
TARGET_SIZE = 8000
FORMAL_TARGET = 200
AUDIT_SAMPLE_SIZE = 500
LABELS = ["ACTOR", "ACTION", "FEATURE", "CONSTRAINT", "QUALITY", "PRIORITY"]
SOURCE_GROUP_TARGETS = {
    "formal_fr": 100,
    "formal_nfr": 100,
    "pure_fr": 1200,
    "pure_nfr": 600,
}

QUALITY_TERMS = [
    "secure",
    "reliable",
    "fast",
    "responsive",
    "scalable",
    "robust",
    "efficient",
    "available",
    "readable",
    "understandable",
    "usable",
    "portable",
    "maintainable",
    "fault tolerant",
    "user-friendly",
    "accessible",
    "stable",
]

PRIORITY_TERMS = [
    "urgent",
    "critical",
    "asap",
    "high priority",
    "top priority",
    "p0",
    "p1",
    "blocker",
]

ACTION_VERBS = [
    "accept",
    "access",
    "add",
    "allow",
    "archive",
    "authenticate",
    "authorize",
    "backup",
    "cache",
    "calculate",
    "capture",
    "create",
    "delete",
    "deploy",
    "display",
    "edit",
    "email",
    "encrypt",
    "export",
    "fetch",
    "filter",
    "generate",
    "handle",
    "import",
    "index",
    "install",
    "load",
    "log",
    "log in",
    "login",
    "map",
    "match",
    "measure",
    "migrate",
    "monitor",
    "notify",
    "optimize",
    "parse",
    "pause",
    "process",
    "provide",
    "publish",
    "record",
    "refresh",
    "register",
    "render",
    "report",
    "reset",
    "retry",
    "run",
    "save",
    "schedule",
    "search",
    "send",
    "sign in",
    "sign up",
    "store",
    "submit",
    "support",
    "sync",
    "track",
    "update",
    "upload",
    "use",
    "validate",
    "verify",
    "view",
    "experience",
    "include",
    "continue",
]

ACTOR_PATTERN = re.compile(
    r"\b("
    r"the system|system|application|app|product|platform|software|service|server|database|api|"
    r"user|users|admin|administrator|administrators|operator|operators|client|customer|customers|"
    r"qa team|backend service|frontend app|support team|developer|developers|manager|managers|"
    r"browser|mobile app|device|devices|interface|interfaces"
    r")\b",
    re.IGNORECASE,
)
MODAL_PATTERN = re.compile(
    r"\b(?:shall|must|should|will|can|needs to|need to|is required to|are required to)\b",
    re.IGNORECASE,
)
CONSTRAINT_PATTERNS = [
    re.compile(r"\bwithin\s+\d+(?:\.\d+)?\s+\w+(?:\s+\w+)?(?:\s+of\s+\w+ing)?", re.IGNORECASE),
    re.compile(r"\bin\s+less\s+than\s+\d+(?:\.\d+)?\s+\w+(?:\s+\w+)?", re.IGNORECASE),
    re.compile(r"\bno\s+more\s+than\s+\d+(?:\.\d+)?\s+\w+(?:\s+\w+)?", re.IGNORECASE),
    re.compile(r"\bduring\s+[^.,;]+", re.IGNORECASE),
    re.compile(r"\bunder\s+[^.,;]+", re.IGNORECASE),
    re.compile(r"\bbefore\s+[^.,;]+", re.IGNORECASE),
    re.compile(r"\bafter\s+[^.,;]+", re.IGNORECASE),
    re.compile(r"\bevery\s+\d+\s+\w+(?:\s+\w+)?", re.IGNORECASE),
    re.compile(r"\bevery\s+(?:day|week|month|hour|request|login)", re.IGNORECASE),
    re.compile(r"\bat\s+least\s+[^.,;]+", re.IGNORECASE),
    re.compile(r"\bas\s+long\s+as\s+[^.,;]+", re.IGNORECASE),
    re.compile(r"\bif\s+[^.]+", re.IGNORECASE),
    re.compile(r"\bwhen\s+[^.,;]+", re.IGNORECASE),
    re.compile(r"\bunless\s+[^.,;]+", re.IGNORECASE),
    re.compile(r"\bbefore\s+next\s+\w+", re.IGNORECASE),
    re.compile(r"\bafter\s+login\b", re.IGNORECASE),
    re.compile(r"\bduring\s+peak\s+hours\b", re.IGNORECASE),
    re.compile(r"\bunder\s+heavy\s+load\b", re.IGNORECASE),
]
QUALITY_WORD_SET = {term.lower() for term in QUALITY_TERMS}
GENERIC_FEATURES = {
    "user",
    "users",
    "system",
    "product",
    "application",
    "software",
    "service",
    "time",
    "availability",
    "performance",
}
RELIABLE_FORMAL_ACTIONS = {
    "access",
    "allow",
    "authenticate",
    "backup",
    "calculate",
    "capture",
    "create",
    "delete",
    "deploy",
    "display",
    "edit",
    "encrypt",
    "export",
    "generate",
    "handle",
    "import",
    "index",
    "load",
    "log",
    "login",
    "monitor",
    "notify",
    "optimize",
    "parse",
    "pause",
    "process",
    "provide",
    "refresh",
    "register",
    "render",
    "report",
    "reset",
    "retry",
    "run",
    "save",
    "schedule",
    "search",
    "send",
    "store",
    "submit",
    "support",
    "sync",
    "track",
    "update",
    "upload",
    "use",
    "validate",
    "verify",
    "view",
}
BOUNDARY_WORDS = {
    "within",
    "during",
    "before",
    "after",
    "under",
    "every",
    "if",
    "when",
    "unless",
    "while",
    "as",
    "at",
    "by",
    "because",
    "so",
    "also",
    "this",
    "that",
    "to",
}
ARTICLE_WORDS = {"the", "a", "an"}
CLASS_TO_QUALITY_HINTS = {
    "PE": ["fast", "responsive", "efficient"],
    "SE": ["secure", "authorized", "authenticated", "encrypted"],
    "US": ["usable", "readable", "understandable", "easy", "accessible"],
    "A": ["available", "availability"],
    "FT": ["fault tolerant", "reliable", "robust"],
    "SC": ["scalable", "scale"],
    "PO": ["portable", "compatible"],
    "MN": ["maintainable", "maintainability", "modular"],
    "O": ["operable", "configurable", "monitorable"],
}
PASSIVE_ACTION_MAP = {
    "recorded": "record",
    "stored": "store",
    "captured": "capture",
    "displayed": "display",
    "provided": "provide",
    "submitted": "submit",
    "sent": "send",
    "retrieved": "retrieve",
    "configured": "configure",
    "accessed": "access",
    "identified": "identify",
    "reviewed": "review",
    "finalized": "finalize",
    "merged": "merge",
    "linked": "link",
}


@dataclass
class Record:
    text: str
    entities: list[tuple[int, int, str]]
    source: str
    source_group: str
    metadata: dict[str, str] = field(default_factory=dict)


def clean_text(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([:])\s*\.", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", clean_text(text).lower())).strip()


def token_set(text: str) -> set[str]:
    return set(normalized_text(text).split())


def spans_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def add_entity(entities: list[tuple[int, int, str]], start: int, end: int, label: str) -> None:
    if start < 0 or end <= start:
        return
    candidate = (start, end)
    for s, e, _ in entities:
        if spans_overlap(candidate, (s, e)):
            return
    entities.append((start, end, label))


def realign_annotated_text(text: str, entities: list[list[int | str]]) -> tuple[str, list[tuple[int, int, str]]]:
    cleaned = clean_text(text)
    captured = []
    for start, end, label in entities:
        phrase = clean_text(text[int(start):int(end)])
        if phrase:
            captured.append((int(start), phrase, str(label)))

    new_entities: list[tuple[int, int, str]] = []
    search_from = 0
    for _, phrase, label in captured:
        idx = cleaned.lower().find(phrase.lower(), search_from)
        if idx < 0:
            idx = cleaned.lower().find(phrase.lower())
        if idx < 0:
            return text, [(int(s), int(e), str(label)) for s, e, label in entities]
        add_entity(new_entities, idx, idx + len(phrase), label)
        search_from = idx + len(phrase)
    return cleaned, sorted(new_entities, key=lambda item: (item[0], item[1], item[2]))


def parse_xlsx_rows(path: Path) -> Iterable[list[str]]:
    ns = {
        "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relmap = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        sheet = next(iter(workbook.find("a:sheets", ns)))
        target = "xl/" + relmap[sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]

        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in shared:
                text = "".join(node.text or "" for node in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
                shared_strings.append(text)

        root = ET.fromstring(archive.read(target))
        rows = root.findall(".//a:sheetData/a:row", ns)
        for row in rows:
            values: list[str] = []
            for cell in row.findall("a:c", ns):
                cell_type = cell.attrib.get("t")
                value_node = cell.find("a:v", ns)
                value = value_node.text if value_node is not None else ""
                if cell_type == "s" and value:
                    value = shared_strings[int(value)]
                elif cell_type == "inlineStr":
                    is_node = cell.find("a:is/a:t", ns)
                    value = is_node.text if is_node is not None else ""
                values.append(value)
            yield values


def load_custom_records() -> list[Record]:
    data = json.loads(CUSTOM_PATH.read_text(encoding="utf-8"))
    records: list[Record] = []
    for text, ann in data:
        cleaned_text, entities = realign_annotated_text(text, ann.get("entities", []))
        records.append(
            Record(
                text=cleaned_text,
                entities=entities,
                source="custom_generated",
                source_group="custom_generated",
                metadata={"origin": "requirements_ner_dataset_5000_v3.json"},
            )
        )
    return records


def load_fr_nfr_records() -> list[dict[str, str]]:
    rows = list(parse_xlsx_rows(FR_NFR_PATH))
    headers = rows[0]
    records: list[dict[str, str]] = []
    for row in rows[1:]:
        if not row:
            continue
        text = clean_text(row[0] if len(row) > 0 else "")
        if not text:
            continue
        requirement_type = (row[1] if len(row) > 1 else "").strip() or "UNKNOWN"
        if requirement_type == "#NAME?":
            continue
        records.append({"text": text, "requirement_type": requirement_type, "source": "fr_nfr"})
    return records


def load_csv_records(path: Path, source: str, class_column: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            text = clean_text(row.get("RequirementText", ""))
            if text:
                records.append(
                    {
                        "text": text,
                        "requirement_type": row.get(class_column, ""),
                        "source": source,
                    }
                )
    return records


def load_pure_records(path: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    with path.open(encoding="latin1") as handle:
        for row in csv.DictReader(handle):
            text = clean_text(row.get("sentence", ""))
            if not text:
                continue
            if "parsed.json_" in text or re.search(r",\d,\d,\d\b", text):
                continue
            if len(text) > 450:
                continue
            requirement_type = "PURE_NFR" if row.get("NFR_boolean", "0") == "1" else "PURE_FR"
            records.append(
                {
                    "text": text,
                    "requirement_type": requirement_type,
                    "source": "pure_dataset",
                    "id": row.get("id", ""),
                    "security": row.get("security", "0"),
                    "reliability": row.get("reliability", "0"),
                }
            )
    return records


def find_phrase(text: str, phrase: str, taken: list[tuple[int, int, str]]) -> tuple[int, int] | None:
    idx = text.lower().find(phrase.lower())
    while idx >= 0:
        candidate = (idx, idx + len(phrase))
        if all(not spans_overlap(candidate, (s, e)) for s, e, _ in taken):
            return candidate
        idx = text.lower().find(phrase.lower(), idx + 1)
    return None


def detect_actor(text: str, entities: list[tuple[int, int, str]], source: str = "") -> None:
    modal = MODAL_PATTERN.search(text)
    search_end = modal.start() if modal else min(len(text), 80)
    match = ACTOR_PATTERN.search(text[:search_end])
    if match:
        add_entity(entities, match.start(), match.end(), "ACTOR")
        return
    if source == "pure_dataset":
        if text.lower().startswith("system shall"):
            add_entity(entities, 0, len("System"), "ACTOR")
        elif text.lower().startswith("the system shall"):
            add_entity(entities, 0, len("The system"), "ACTOR")


def detect_action(text: str, entities: list[tuple[int, int, str]], source: str = "") -> tuple[int, int] | None:
    modal = MODAL_PATTERN.search(text)
    start_search = modal.end() if modal else 0
    tail = text[start_search:]
    patterns = [
        r"^\s*provide\s+the\s+ability\s+to\s+([A-Za-z]+(?:\s+(?:in|out|up|off)\b)?)",
        r"^\s*ability\s+to\s+([A-Za-z]+(?:\s+(?:in|out|up|off)\b)?)",
        r"^\s*be able to\s+([A-Za-z]+(?:\s+(?:in|out|up|off)\b)?)",
        r"^\s*be\s+([A-Za-z]+(?:\s+(?:in|out|up|off)\b)?)",
        r"^\s*have\s+([A-Za-z]+(?:\s+(?:in|out|up|off)\b)?)",
        r"^\s*([A-Za-z]+(?:\s+(?:in|out|up|off)\b)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, tail, flags=re.IGNORECASE)
        if not match:
            continue
        phrase = match.group(1)
        token = phrase.lower().split()[0]
        if token in {"able", "to", "be"}:
            continue
        if token not in {verb.split()[0] for verb in ACTION_VERBS} and len(token) <= 2:
            continue
        candidate = (start_search + match.start(1), start_search + match.end(1))
        if all(not spans_overlap(candidate, (s, e)) for s, e, _ in entities):
            add_entity(entities, candidate[0], candidate[1], "ACTION")
            return candidate
    passive = re.search(r"\b(?:shall|must|should|will)\s+be\s+([A-Za-z]+ed)\b", text, flags=re.IGNORECASE)
    if passive:
        surface = passive.group(1)
        lemma = PASSIVE_ACTION_MAP.get(surface.lower())
        if lemma:
            candidate = (passive.start(1), passive.end(1))
            if all(not spans_overlap(candidate, (s, e)) for s, e, _ in entities):
                add_entity(entities, candidate[0], candidate[1], "ACTION")
                return candidate
    return None


def detect_feature(text: str, action_span: tuple[int, int] | None, entities: list[tuple[int, int, str]], source: str = "") -> None:
    if not action_span:
        return
    tail = text[action_span[1]:]
    offset = action_span[1]
    special = re.search(r"^\s+the\s+ability\s+to\s+[A-Za-z]+(?:\s+(?:in|out|up|off)\b)?\s+(.+)", tail, flags=re.IGNORECASE)
    if special:
        feature = special.group(1)
        feature = re.split(r"\b(?:if|when|within|during|before|after|as|such that|so that|while|unless)\b", feature, maxsplit=1, flags=re.IGNORECASE)[0]
        feature = re.sub(r"[.,;:!?]+$", "", feature).strip()
        feature = re.sub(r"^(?:the|a|an)\s+", "", feature, flags=re.IGNORECASE)
        feature = re.sub(r"\s+(?:in|on|with|from|by|into|as)\s+.+$", "", feature, flags=re.IGNORECASE)
        if feature:
            span = find_phrase(text[offset:], feature, [])
            if span is not None:
                absolute = (offset + span[0], offset + span[1])
                add_entity(entities, absolute[0], absolute[1], "FEATURE")
                return
    tokens = re.findall(r"\S+", tail)
    if not tokens:
        return

    selected: list[str] = []
    started = False
    for token in tokens:
        plain = token.strip(".,;:!?").lower()
        if not plain:
            continue
        if not started and plain in ARTICLE_WORDS:
            selected.append(token)
            continue
        if plain in BOUNDARY_WORDS or plain in {"shall", "must", "should", "will", "which", "where", "while"}:
            break
        if source in {"pure_dataset", "promise_exp", "tera_promise_nfr", "fr_nfr"} and plain in {"in", "on", "with", "from", "by", "into", "as", "such", "that"} and started:
            break
        started = True
        selected.append(token)
        if token.endswith(","):
            break
        if len(selected) >= 6:
            break
    feature = " ".join(selected).strip()
    feature = re.sub(r"[.,;:!?]+$", "", feature)
    feature = re.sub(r"^(?:the|a|an)\s+", "", feature, flags=re.IGNORECASE)
    if not feature:
        return
    span = find_phrase(text[offset:], feature, [])
    if span is None:
        span = find_phrase(text, feature, entities)
        if span is None:
            return
        add_entity(entities, span[0], span[1], "FEATURE")
        return
    absolute = (offset + span[0], offset + span[1])
    add_entity(entities, absolute[0], absolute[1], "FEATURE")


def detect_constraints(text: str, entities: list[tuple[int, int, str]]) -> None:
    for pattern in CONSTRAINT_PATTERNS:
        for match in pattern.finditer(text):
            phrase = match.group(0).rstrip(" ,;:")
            phrase = re.sub(r"\b(?:for|in|of|the)$", "", phrase, flags=re.IGNORECASE).rstrip()
            start = match.start()
            end = start + len(phrase)
            add_entity(entities, start, end, "CONSTRAINT")


def detect_quality(text: str, entities: list[tuple[int, int, str]], requirement_type: str) -> None:
    terms = list(QUALITY_TERMS)
    terms.extend(CLASS_TO_QUALITY_HINTS.get(requirement_type, []))
    seen = set()
    for term in sorted(terms, key=len, reverse=True):
        if term.lower() in seen:
            continue
        seen.add(term.lower())
        span = find_phrase(text, term, entities)
        if span is not None:
            add_entity(entities, span[0], span[1], "QUALITY")


def detect_priority(text: str, entities: list[tuple[int, int, str]]) -> None:
    for term in sorted(PRIORITY_TERMS, key=len, reverse=True):
        span = find_phrase(text, term, entities)
        if span is not None:
            add_entity(entities, span[0], span[1], "PRIORITY")


def annotate_formal_record(item: dict[str, str]) -> Record | None:
    text = clean_text(item["text"])
    entities: list[tuple[int, int, str]] = []
    detect_actor(text, entities, item["source"])
    action_span = detect_action(text, entities, item["source"])
    detect_feature(text, action_span, entities, item["source"])
    detect_constraints(text, entities)
    detect_quality(text, entities, item["requirement_type"])
    detect_priority(text, entities)
    entities = sorted(entities, key=lambda entity: (entity[0], entity[1], entity[2]))
    if not entities:
        return None
    if item["source"] == "pure_dataset":
        source_group = "pure_nfr" if item["requirement_type"] == "PURE_NFR" else "pure_fr"
    else:
        source_group = "formal_fr" if item["requirement_type"] in {"FR", "F"} else "formal_nfr"
    return Record(
        text=text,
        entities=entities,
        source=item["source"],
        source_group=source_group,
        metadata={
            "requirement_type": item["requirement_type"],
            "id": item.get("id", ""),
            "security": item.get("security", ""),
            "reliability": item.get("reliability", ""),
        },
    )


def is_high_quality_formal(record: Record) -> bool:
    labels = Counter(label for _, _, label in record.entities)
    if labels["ACTION"] == 0:
        return False
    if not record.source_group.startswith("pure") and labels["ACTOR"] == 0:
        return False
    if record.source_group.startswith("pure") and labels["ACTOR"] == 0 and labels["FEATURE"] == 0:
        return False
    if len(record.entities) < 2:
        return False
    for start, end, label in record.entities:
        phrase = record.text[start:end]
        words = phrase.split()
        lower_phrase = phrase.lower().strip()
        if label == "FEATURE":
            if len(words) == 0 or len(words) > 5:
                return False
            if any(word.lower() in {"shall", "must", "should", "will"} for word in words):
                return False
            if lower_phrase.startswith(("of ", "to ", "and ", "for ")):
                return False
            if lower_phrase in GENERIC_FEATURES:
                return False
            if lower_phrase in {"only", "each player", "their game in", "their streaming movies in"}:
                return False
            if lower_phrase.endswith((" in", " on", " of", " for", " to", " with", " based on")):
                return False
            if any(token.lower() in RELIABLE_FORMAL_ACTIONS for token in words[1:]):
                return False
            if any(ch in phrase for ch in ['"', ".", ":"]):
                return False
        if label == "ACTION" and len(words) > 2:
            return False
        if label == "ACTION":
            root = words[0].lower()
            if root not in RELIABLE_FORMAL_ACTIONS and root not in PASSIVE_ACTION_MAP:
                return False
            if root in QUALITY_WORD_SET or root in {"high", "easy", "available"}:
                return False
        if label == "PRIORITY" and record.source_group.startswith("formal"):
            return False
    return True


def is_near_duplicate(text: str, seen_buckets: dict[tuple[str, str, int], list[str]]) -> bool:
    norm = normalized_text(text)
    tokens = norm.split()
    if not tokens:
        return True
    bucket = (tokens[0], tokens[-1], len(tokens) // 5)
    for existing in seen_buckets[bucket]:
        ratio = SequenceMatcher(None, norm, existing).ratio()
        overlap = len(set(tokens) & set(existing.split())) / max(1, len(set(tokens) | set(existing.split())))
        if ratio >= 0.97 or overlap >= 0.93:
            return True
    seen_buckets[bucket].append(norm)
    return False


def validate_record(record: Record) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    previous_end = -1
    for start, end, label in record.entities:
        if label not in LABELS:
            errors.append(f"unknown-label:{label}")
        if start < previous_end:
            errors.append("overlap")
        if start < 0 or end > len(record.text) or start >= end:
            errors.append("invalid-span")
        if record.text[start:end] != record.text[start:end].strip():
            warnings.append("whitespace-boundary")
        previous_end = max(previous_end, end)
    return {"errors": errors, "warnings": warnings}


def record_sort_key(record: Record) -> tuple[int, int, str]:
    label_score = len({label for _, _, label in record.entities})
    source_bonus = 1 if record.source_group.startswith("formal") else 0
    return (label_score, source_bonus, record.text.lower())


def formal_quality_score(record: Record) -> tuple[int, int, int, str]:
    labels = {label for _, _, label in record.entities}
    feature_len = 99
    for start, end, label in record.entities:
        if label == "FEATURE":
            feature_len = len(record.text[start:end].split())
            break
    return (len(labels), -feature_len, -len(record.text), record.text.lower())


def build_dataset() -> None:
    random.seed(RANDOM_SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    custom_records = load_custom_records()
    formal_items = load_fr_nfr_records()
    formal_items.extend(load_csv_records(PROMISE_PATH, "promise_exp", "_class_"))
    formal_items.extend(load_csv_records(NFR_PATH, "tera_promise_nfr", "class"))
    pure_items = load_pure_records(PURE_PATH)
    formal_items.extend(pure_items)

    formal_records = []
    pure_review_candidates = []
    for item in formal_items:
        record = annotate_formal_record(item)
        if record is not None and is_high_quality_formal(record):
            formal_records.append(record)
        elif item["source"] == "pure_dataset":
            pure_review_candidates.append(
                {
                    "text": clean_text(item["text"]),
                    "requirement_type": item["requirement_type"],
                    "id": item.get("id", ""),
                    "security": item.get("security", ""),
                    "reliability": item.get("reliability", ""),
                    "proposed_entities": [] if record is None else [
                        {"start": s, "end": e, "label": l, "text": clean_text(record.text[s:e])}
                        for s, e, l in record.entities
                    ],
                }
            )

    formal_records.sort(key=formal_quality_score, reverse=True)

    seen_exact: set[str] = set()
    seen_buckets: dict[tuple[str, str, int], list[str]] = defaultdict(list)
    final_records: list[Record] = []

    for record in custom_records:
        signature = normalized_text(record.text)
        if not signature or signature in seen_exact or is_near_duplicate(record.text, seen_buckets):
            continue
        seen_exact.add(signature)
        final_records.append(record)

    formal_selected = 0
    group_counts = Counter()

    for record in formal_records:
        if formal_selected >= sum(SOURCE_GROUP_TARGETS.values()):
            break
        signature = normalized_text(record.text)
        if not signature or signature in seen_exact or is_near_duplicate(record.text, seen_buckets):
            continue
        if group_counts[record.source_group] >= SOURCE_GROUP_TARGETS.get(record.source_group, 0):
            continue
        seen_exact.add(signature)
        final_records.append(record)
        formal_selected += 1
        group_counts[record.source_group] += 1

    if len(final_records) > TARGET_SIZE:
        final_records = final_records[:TARGET_SIZE]

    validation = [validate_record(record) for record in final_records]
    invalid_records = [
        {"text": record.text, "issues": issues}
        for record, issues in zip(final_records, validation)
        if issues["errors"]
    ]
    if invalid_records:
        raise ValueError(f"Found invalid records: {invalid_records[:3]}")

    label_counts = Counter()
    source_counts = Counter()
    phrase_labels: dict[str, set[str]] = defaultdict(set)
    for record in final_records:
        source_counts[record.source_group] += 1
        for start, end, label in record.entities:
            label_counts[label] += 1
            phrase_labels[record.text[start:end].lower()].add(label)

    grouped_indices: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(final_records):
        grouped_indices[record.source_group].append(index)

    train_indices: list[int] = []
    dev_indices: list[int] = []
    test_indices: list[int] = []
    rng = random.Random(RANDOM_SEED)
    for indices in grouped_indices.values():
        shuffled = indices[:]
        rng.shuffle(shuffled)
        total = len(shuffled)
        train_cutoff = int(total * 0.8)
        dev_cutoff = int(total * 0.9)
        train_indices.extend(shuffled[:train_cutoff])
        dev_indices.extend(shuffled[train_cutoff:dev_cutoff])
        test_indices.extend(shuffled[dev_cutoff:])

    conflicting_phrases = {
        phrase: sorted(labels)
        for phrase, labels in phrase_labels.items()
        if len(labels) > 1 and len(phrase) >= 3
    }

    spacy_data = [[record.text, {"entities": [[start, end, label] for start, end, label in record.entities]}] for record in final_records]
    unified_text = [{"text": record.text, "source": record.source, "source_group": record.source_group} for record in final_records]
    detailed_records = [
        {
            "text": record.text,
            "entities": [{"start": start, "end": end, "label": label, "text": record.text[start:end]} for start, end, label in record.entities],
            "source": record.source,
            "source_group": record.source_group,
            "metadata": record.metadata,
        }
        for record in final_records
    ]

    train_data = [spacy_data[index] for index in sorted(train_indices)]
    dev_data = [spacy_data[index] for index in sorted(dev_indices)]
    test_data = [spacy_data[index] for index in sorted(test_indices)]

    audit_indices = sorted(random.sample(range(len(final_records)), min(AUDIT_SAMPLE_SIZE, len(final_records))))
    audit_records = [detailed_records[index] for index in audit_indices]

    stats = {
        "total_samples": len(final_records),
        "source_group_distribution": dict(source_counts),
        "label_distribution": dict(label_counts),
        "avg_entities_per_sample": round(sum(len(record.entities) for record in final_records) / max(1, len(final_records)), 3),
        "samples_with_multiple_entities": sum(1 for record in final_records if len(record.entities) >= 3),
        "samples_with_priority": sum(1 for record in final_records if any(label == "PRIORITY" for _, _, label in record.entities)),
        "conflicting_phrase_count": len(conflicting_phrases),
        "split_sizes": {
            "train": len(train_data),
            "dev": len(dev_data),
            "test": len(test_data),
        },
    }

    summary_lines = [
        "# Dataset Summary",
        "",
        f"- Total samples: {stats['total_samples']}",
        f"- Source groups: {stats['source_group_distribution']}",
        f"- Label distribution: {stats['label_distribution']}",
        f"- Average entities per sample: {stats['avg_entities_per_sample']}",
        f"- Samples with 3+ entities: {stats['samples_with_multiple_entities']}",
        f"- Samples with PRIORITY labels: {stats['samples_with_priority']}",
        f"- Cross-label phrase conflicts: {stats['conflicting_phrase_count']}",
        "",
        "## Example Samples",
        "",
    ]
    for sample in detailed_records[:10]:
        summary_lines.append(f"- Text: {sample['text']}")
        summary_lines.append(f"  Entities: {[(ent['text'], ent['label']) for ent in sample['entities']]}")

    (OUTPUT_DIR / "requirements_ner_spacy.json").write_text(json.dumps(spacy_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "requirements_ner_train.json").write_text(json.dumps(train_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "requirements_ner_dev.json").write_text(json.dumps(dev_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "requirements_ner_test.json").write_text(json.dumps(test_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "unified_text_dataset.jsonl").write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in unified_text),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "requirements_ner_records.jsonl").write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in detailed_records),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "dataset_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "annotation_consistency_report.json").write_text(
        json.dumps(
            {
                "conflicting_phrases": conflicting_phrases,
                "invalid_record_count": len(invalid_records),
                "manual_audit_sample_size": len(audit_records),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "annotation_audit_samples.jsonl").write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in audit_records),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "pure_review_candidates.jsonl").write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in pure_review_candidates[:1000]),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "dataset_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    print(json.dumps(stats, indent=2))
    print(f"Wrote outputs to {OUTPUT_DIR}")


if __name__ == "__main__":
    build_dataset()
