"""
Generate 250 noisy real-world NER samples simulating Jira/Slack/email inputs.
Outputs to data/ner/noisy_samples.json in spaCy training format.
"""

import json
import random
import os

random.seed(42)

# ── Building blocks ────────────────────────────────────────────

ACTORS = [
    "user", "users", "admin", "the system", "customer", "developer",
    "QA team", "backend service", "the API", "mobile app", "operator",
    "support team", "the platform", "frontend", "the database",
]

ACTIONS = [
    "login", "authenticate", "export", "upload", "download", "sync",
    "process", "validate", "encrypt", "generate", "delete", "update",
    "create", "search", "filter", "display", "send", "notify",
    "deploy", "monitor", "cache", "log", "register", "reset",
    "submit", "save", "load", "render", "fetch", "track",
]

FEATURES = [
    "dashboard", "reports", "payment gateway", "audit logs", "user settings",
    "passwords", "notifications", "PDF files", "profile pictures",
    "search results", "checkout flow", "database records", "API endpoints",
    "session tokens", "error messages", "file uploads", "user accounts",
    "email templates", "access control", "billing module", "analytics page",
    "login page", "admin panel", "data export", "webhook config",
]

CONSTRAINTS = [
    "within 2 seconds", "under 1 second", "during peak hours",
    "under heavy load", "before next release", "in real-time",
    "within 500ms", "after login", "every 24 hours", "on mobile",
]

QUALITIES = [
    "secure", "fast", "reliable", "responsive", "scalable",
    "stable", "accessible", "efficient", "robust", "usable",
]

PRIORITIES = [
    "urgent", "critical", "asap", "p0", "p1", "blocker", "high priority",
]

# ── Template definitions ───────────────────────────────────────
# Each template is (format_string, slot_names)
# Slots: A=ACTOR, V=ACTION, F=FEATURE, C=CONSTRAINT, Q=QUALITY, P=PRIORITY

JIRA_TEMPLATES = [
    ("JIRA-{ticket}: {A} cannot {V} {F}", ["A", "V", "F"]),
    ("[BUG] {F} broken - {A} unable to {V}", ["F", "A", "V"]),
    ("[FEATURE] {A} should be able to {V} {F} {C}", ["A", "V", "F", "C"]),
    ("{P} - {F} not working after latest deploy", ["P", "F"]),
    ("fix {F} {V} issue - affects all {A}", ["F", "V", "A"]),
    ("{A} reports {F} is not {Q}", ["A", "F", "Q"]),
    ("[{P}] {V} {F} failing {C}", ["P", "V", "F", "C"]),
    ("JIRA-{ticket}: need to {V} {F} for {A}", ["V", "F", "A"]),
    ("{F} - {A} can't {V}, {P}", ["F", "A", "V", "P"]),
    ("regression: {A} {V} {F} returns error {C}", ["A", "V", "F", "C"]),
]

SLACK_TEMPLATES = [
    ("hey can someone look at the {V} {F}? its broken again", ["V", "F"]),
    ("@team {F} is down, {A} can't {V}", ["F", "A", "V"]),
    ("fyi {F} needs to be more {Q}", ["F", "Q"]),
    ("{P} - {A} needs to {V} {F} {C}", ["P", "A", "V", "F", "C"]),
    ("just noticed {F} {V} is super slow {C}", ["F", "V", "C"]),
    ("anyone working on the {F}? {A} keeps complaining", ["F", "A"]),
    ("we need {V} for {F} {P}", ["V", "F", "P"]),
    ("@here {F} not {Q} enough, {A} flagged it", ["F", "Q", "A"]),
    ("quick question - can {A} {V} {F}?", ["A", "V", "F"]),
    ("heads up: {V} {F} broken on mobile for {A}", ["V", "F", "A"]),
]

INFORMAL_TEMPLATES = [
    ("{A} should {V} {F} {Q}ly", ["A", "V", "F", "Q"]),
    ("need to make {F} more {Q} for {A}", ["F", "Q", "A"]),
    ("{V} {F} is way too slow {C}", ["V", "F", "C"]),
    ("the {F} needs {V} support, {P}", ["F", "V", "P"]),
    ("can we {V} {F} {C}? {A} is waiting", ["V", "F", "C", "A"]),
    ("{A} wants to {V} {F} but it crashes", ["A", "V", "F"]),
    ("{P}!! {A} can't {V} {F}", ["P", "A", "V", "F"]),
    ("make {F} {Q} - {A} complained", ["F", "Q", "A"]),
    ("{V} {F} broken since last update", ["V", "F"]),
    ("todo: {V} {F} for {A} {C}", ["V", "F", "A", "C"]),
]

EMAIL_TEMPLATES = [
    ("RE: {F} issue - {A} unable to {V} {C}", ["F", "A", "V", "C"]),
    ("Update: {F} needs to be {Q}, {P}", ["F", "Q", "P"]),
    ("FYI - {A} reported {F} {V} failure", ["A", "F", "V"]),
    ("Action needed: {V} {F} for {A}", ["V", "F", "A"]),
    ("follow up on {F} - still not {Q} {C}", ["F", "Q", "C"]),
]

SLOT_POOLS = {
    "A": ACTORS,
    "V": ACTIONS,
    "F": FEATURES,
    "C": CONSTRAINTS,
    "Q": QUALITIES,
    "P": PRIORITIES,
}

SLOT_LABELS = {
    "A": "ACTOR",
    "V": "ACTION",
    "F": "FEATURE",
    "C": "CONSTRAINT",
    "Q": "QUALITY",
    "P": "PRIORITY",
}


def generate_sample(template_str, slots):
    """Generate one annotated sample from a template."""
    picks = {}
    for slot in slots:
        picks[slot] = random.choice(SLOT_POOLS[slot])

    # Fill non-entity placeholders
    text = template_str.replace("{ticket}", str(random.randint(100, 9999)))

    # Build text and track entity positions
    entities = []
    for slot in slots:
        placeholder = "{" + slot + "}"
        value = picks[slot]
        idx = text.find(placeholder)
        if idx == -1:
            continue
        text = text[:idx] + value + text[idx + len(placeholder):]
        entities.append([idx, idx + len(value), SLOT_LABELS[slot]])

    # Re-sort entities by start position
    entities.sort(key=lambda e: e[0])

    # Validate no overlaps
    for i in range(len(entities) - 1):
        if entities[i][1] > entities[i + 1][0]:
            return None

    return [text, {"entities": entities}]


def add_noise(sample):
    """Apply light noise to a sample (casing, typos) without breaking spans."""
    text, ann = sample
    entities = ann["entities"]

    # 30% chance: lowercase everything
    if random.random() < 0.3:
        new_text = text.lower()
        # Offsets stay the same since lowercasing doesn't change length
        return [new_text, {"entities": entities}]

    # 20% chance: add trailing noise
    suffixes = [" (edited)", " - thoughts?", "...", " !!!", " /cc @pm"]
    if random.random() < 0.2:
        return [text + random.choice(suffixes), {"entities": entities}]

    return sample


def main():
    all_templates = (
        [(t, s, "jira") for t, s in JIRA_TEMPLATES]
        + [(t, s, "slack") for t, s in SLACK_TEMPLATES]
        + [(t, s, "informal") for t, s in INFORMAL_TEMPLATES]
        + [(t, s, "email") for t, s in EMAIL_TEMPLATES]
    )

    samples = []
    attempts = 0
    seen = set()

    while len(samples) < 250 and attempts < 2000:
        attempts += 1
        tmpl_str, slots, _ = random.choice(all_templates)
        result = generate_sample(tmpl_str, slots)
        if result is None:
            continue

        text = result[0]
        if text in seen:
            continue
        seen.add(text)

        # Apply noise to ~40% of samples
        if random.random() < 0.4:
            result = add_noise(result)

        samples.append(result)

    # Write output
    out_path = os.path.join(os.path.dirname(__file__), "noisy_samples.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"[OK] Generated {len(samples)} noisy samples -> {out_path}")

    # Print stats
    from collections import Counter
    label_counts = Counter()
    for _, ann in samples:
        for s, e, label in ann["entities"]:
            label_counts[label] += 1
    print(f"  Label distribution: {dict(label_counts)}")


if __name__ == "__main__":
    main()
