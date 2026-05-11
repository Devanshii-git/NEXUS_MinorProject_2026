"""
Generate 500 targeted contrastive samples to teach strict boundary separation
between ACTOR, FEATURE, and CONSTRAINT.
"""

import json
import random
import os

random.seed(42)

ACTORS = [
    "user", "admin", "customer", "developer", "system", "platform",
    "API", "operator", "manager", "support team", "client"
]

ACTIONS = [
    "access", "update", "delete", "create", "view", "download",
    "export", "import", "configure", "monitor", "review", "approve"
]

FEATURES = [
    "dashboard", "payment gateway", "profile settings", "audit log",
    "report module", "login page", "billing system", "database records",
    "user list", "admin panel", "notification settings"
]

CONSTRAINTS = [
    "within 2 seconds", "under heavy load", "during peak hours",
    "before next release", "at all times", "in real-time",
    "every 24 hours", "after authentication"
]

# Contrastive templates:
# Type 1: [ACTOR] is part of [FEATURE] naturally.
# e.g., "The admin must view the user list within 2 seconds"
# Here "user list" is FEATURE. "admin" is ACTOR.

# Type 2: [ACTOR] operates on a [FEATURE] that shares no words.
# e.g., "The user must view the dashboard within 2 seconds"

TEMPLATES = [
    ("The {A1} must {V} the {A2} {F_BASE} {C}", ["A1", "V", "A2", "F_BASE", "C"]),
    ("{A1} shall {V} {A2}'s {F_BASE} {C}", ["A1", "V", "A2", "F_BASE", "C"]),
    ("Ensure {A1} can {V} the {F_BASE} {C}", ["A1", "V", "F_BASE", "C"]),
    ("The {F_BASE} must be {V}ed by the {A1} {C}", ["F_BASE", "V", "A1", "C"]),
]

SLOT_POOLS = {
    "A1": ACTORS,
    "A2": ACTORS,
    "V": ACTIONS,
    "F_BASE": ["dashboard", "settings", "profile", "log", "records", "panel", "module"],
    "C": CONSTRAINTS
}

def generate_contrastive_sample():
    template, slots = random.choice(TEMPLATES)
    picks = {}
    for s in slots:
        picks[s] = random.choice(SLOT_POOLS[s])
        
    text = template
    entities = []
    
    # Process ACTOR 1
    if "A1" in slots:
        val = picks["A1"]
        idx = text.find("{A1}")
        text = text.replace("{A1}", val, 1)
        entities.append((idx, idx + len(val), "ACTOR"))
        
    # Process ACTION
    if "V" in slots:
        val = picks["V"]
        if "ed by" in text and not val.endswith("e"):
            pass # simplified passive, handled by template string replacement
            
        idx = text.find("{V}")
        text = text.replace("{V}", val, 1)
        entities.append((idx, idx + len(val), "ACTION"))
        
    # Process FEATURE (which may combine A2 + F_BASE)
    if "A2" in slots and "F_BASE" in slots:
        a2 = picks["A2"]
        f_base = picks["F_BASE"]
        idx = text.find("{A2}")
        
        # Replace
        text = text.replace("{A2}", a2, 1)
        text = text.replace("{F_BASE}", f_base, 1)
        
        # Determine exact span of the combined feature
        # e.g., "user dashboard" or "user's dashboard"
        # We need to find it in the mutated text
        combined = f"{a2} {f_base}"
        if f"{a2}'s {f_base}" in text:
            combined = f"{a2}'s {f_base}"
            
        f_idx = text.find(combined)
        if f_idx != -1:
            entities.append((f_idx, f_idx + len(combined), "FEATURE"))
            
    elif "F_BASE" in slots:
        f_base = picks["F_BASE"]
        idx = text.find("{F_BASE}")
        text = text.replace("{F_BASE}", f_base, 1)
        entities.append((idx, idx + len(f_base), "FEATURE"))
        
    # Process CONSTRAINT
    if "C" in slots:
        val = picks["C"]
        idx = text.find("{C}")
        text = text.replace("{C}", val, 1)
        entities.append((idx, idx + len(val), "CONSTRAINT"))
        
    entities.sort(key=lambda e: e[0])
    
    # Validate overlaps
    for i in range(len(entities) - 1):
        if entities[i][1] > entities[i+1][0]:
            return None
            
    return [text, {"entities": entities}]

def main():
    samples = []
    seen = set()
    attempts = 0
    
    while len(samples) < 500 and attempts < 5000:
        attempts += 1
        res = generate_contrastive_sample()
        if res:
            text = res[0]
            if text not in seen:
                seen.add(text)
                samples.append(res)
                
    out_path = os.path.join(os.path.dirname(__file__), "boundary_samples.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
        
    print(f"Generated {len(samples)} contrastive boundary samples -> {out_path}")

if __name__ == "__main__":
    main()
