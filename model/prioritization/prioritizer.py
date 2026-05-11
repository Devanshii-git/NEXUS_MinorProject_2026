"""
prioritizer.py — Multi-Signal Requirement Prioritization
==========================================================
Assigns priority (HIGH / MEDIUM / LOW) using multiple signals:

  1. PRIORITY_INDICATOR entities from NER  (+5)
  2. Urgency keywords in text              (+5)
  3. Time constraints in CONSTRAINT        (+2)
  4. Sentiment analysis (negative = urgent) (+4)
  5. QUALITY_ATTRIBUTE presence             (+1)
  6. Frequency of mentions (repeated reqs)  (+3)
  7. Impact words (data loss, downtime)     (+4)
  8. Modal verbs (must > should > could)    (+1)

Scoring:  score >= 5 → HIGH | score >= 2 → MEDIUM | else LOW

Each signal produces an explainable reason string.

Usage:
    from prioritization.prioritizer import RequirementPrioritizer
    prioritizer = RequirementPrioritizer()
    scored = prioritizer.prioritize_requirement(req_dict)
"""

import re
from collections import Counter
from typing import Any


# ---------------------------------------------------------------------------
# Signal dictionaries
# ---------------------------------------------------------------------------
HIGH_PRIORITY_KEYWORDS = {
    "urgent", "critical", "immediately", "asap", "blocker",
    "showstopper", "high priority", "must fix", "p0", "p1",
    "essential", "mandatory", "crucial", "vital",
}

BUSINESS_VALUE_WORDS = {
    "revenue", "roi", "compliance", "legal", "cost", 
    "customer retention", "conversion", "billing", "payment"
}

COSMETIC_WORDS = {
    "color", "font", "padding", "margin", "aesthetic",
    "look and feel", "cosmetic", "typo", "minor", "tweak"
}

IMPACT_WORDS = {
    "data loss", "security breach", "downtime", "crash", "failure",
    "outage", "vulnerability", "exploit", "corruption", "unavailable",
    "broken", "unresponsive", "timeout",
}

STRONG_MODALS = {"must", "shall", "will", "require", "need"}
MEDIUM_MODALS = {"should", "expect", "want"}
WEAK_MODALS = {"could", "may", "might", "consider"}

TIME_CONSTRAINT_PATTERN = re.compile(
    r"within\s+\d+\s*(seconds?|minutes?|hours?|ms|milliseconds?)"
    r"|under\s+\d+\s*(seconds?|minutes?|hours?|ms|milliseconds?)"
    r"|in\s+real\s*time"
    r"|real-time",
    re.IGNORECASE,
)

# Simple lexicon-based sentiment for requirement-domain text
NEGATIVE_WORDS = {
    "slow", "fail", "crash", "error", "bug", "broken", "complaint",
    "complaining", "issue", "problem", "timeout", "delay", "lag",
    "unresponsive", "unavailable", "poor", "bad", "weak", "insecure",
    "vulnerable", "difficult", "confusing", "frustrating", "missing",
}


class RequirementPrioritizer:
    """
    Multi-signal requirement prioritizer with explainable scoring.
    """

    def __init__(self):
        # For frequency counting across a batch
        self._sentence_counts: Counter = Counter()

    def prioritize_requirement(
        self,
        requirement: dict[str, Any],
        all_sentences: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Compute priority for a single requirement using multiple signals.

        Returns the original dict augmented with:
            priority, priority_score, priority_reasons
        """
        score = 0
        reasons = []
        grouped = requirement.get("grouped", {})
        sentence = requirement.get("sentence", "")
        sentence_lower = sentence.lower()
        words = set(sentence_lower.split())

        # --- Signal 1: PRIORITY_INDICATOR entity (+3) -----------------------
        priority_indicators = grouped.get("PRIORITY_INDICATOR", [])
        if priority_indicators:
            score += 3
            reasons.append(
                f"Elevated priority due to explicit indicator: '{', '.join(priority_indicators)}' (+3)"
            )

        # --- Signal 2: Urgency keywords in text (+3) ------------------------
        if not priority_indicators:
            for keyword in HIGH_PRIORITY_KEYWORDS:
                if keyword in sentence_lower:
                    score += 3
                    reasons.append(f"Elevated priority due to urgency keyword: '{keyword}' (+3)")
                    break

        # --- Signal 3: Business Value keywords (+3) -------------------------
        for keyword in BUSINESS_VALUE_WORDS:
            if keyword in sentence_lower:
                score += 3
                reasons.append(f"High business value detected: '{keyword}' (+3)")
                break

        # --- Signal 4: Time constraint in CONSTRAINT (+2) -------------------
        constraints = grouped.get("CONSTRAINT", [])
        for constraint in constraints:
            if TIME_CONSTRAINT_PATTERN.search(constraint):
                score += 2
                reasons.append(f"Contains critical time constraints: '{constraint}' (+2)")
                break

        # --- Signal 5: Sentiment analysis (+4 for negative) -----------------
        neg_found = words & NEGATIVE_WORDS
        if neg_found:
            score += 4
            reasons.append(
                f"User pain point identified showing negative sentiment: '{', '.join(sorted(neg_found))}' (+4)"
            )

        # --- Signal 6: Impact words (+4) ------------------------------------
        for impact in IMPACT_WORDS:
            if impact in sentence_lower:
                score += 4
                reasons.append(f"High risk impact word detected: '{impact}' (+4)")
                break

        # --- Signal 7: QUALITY_ATTRIBUTE (+1) -------------------------------
        quality_attrs = grouped.get("QUALITY_ATTRIBUTE", [])
        if quality_attrs:
            score += 1
            reasons.append(
                f"Specifies essential quality attributes: '{', '.join(quality_attrs)}' (+1)"
            )

        # --- Signal 8: Cosmetic/Negative signals (-2) -----------------------
        for cosmetic in COSMETIC_WORDS:
            if cosmetic in sentence_lower:
                score -= 2
                reasons.append(f"Cosmetic/minor classification: '{cosmetic}' (-2)")
                break

        # --- Signal 9: Modal verb strength (+1 strong, +0.5 medium) ---------
        if words & STRONG_MODALS:
            score += 1
            found = words & STRONG_MODALS
            reasons.append(f"High importance due to mandatory requirement ('{', '.join(found)}') (+1)")
        elif words & MEDIUM_MODALS:
            score += 0.5
            found = words & MEDIUM_MODALS
            reasons.append(f"Medium importance due to expected requirement ('{', '.join(found)}') (+0.5)")

        # --- Signal 10: Frequency (if batch context provided) (+3) -----------
        if all_sentences:
            # Count how many sentences mention similar key terms
            key_features = grouped.get("FEATURE", [])
            freq_bonus = 0
            for feat in key_features:
                count = sum(1 for s in all_sentences if feat.lower() in s.lower())
                if count >= 3:
                    freq_bonus = 3
                    reasons.append(f"Highly requested feature ('{feat}' mentioned {count}x) (+3)")
                    break
                elif count >= 2:
                    freq_bonus = max(freq_bonus, 1)
                    reasons.append(f"Repeatedly requested feature ('{feat}' mentioned {count}x) (+1)")
            score += freq_bonus

        # --- Map score to priority level ------------------------------------
        if score >= 5:
            priority = "HIGH"
        elif score >= 2:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        if not reasons:
            reasons.append("No priority signals detected")

        requirement["priority"] = priority
        requirement["priority_score"] = score
        requirement["priority_reasons"] = reasons

        return requirement

    def prioritize_all(
        self,
        requirements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Prioritize a list of requirements with frequency context and distribution guard."""
        all_sentences = [r.get("sentence", "") for r in requirements]
        prioritized = [
            self.prioritize_requirement(r, all_sentences)
            for r in requirements
        ]
        return self._apply_distribution_guard(prioritized)

    def _apply_distribution_guard(self, requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Post-pass distribution guard to ensure ~20-30% HIGH priority max.
        If too many HIGHs exist, demote the weakest ones to MEDIUM.
        """
        if not requirements:
            return requirements
            
        highs = [r for r in requirements if r["priority"] == "HIGH"]
        high_ratio = len(highs) / len(requirements)
        
        # Target max 30% HIGH
        if high_ratio > 0.30:
            target_high_count = int(len(requirements) * 0.30)
            # Sort HIGHs by score ascending (weakest first)
            highs.sort(key=lambda x: x["priority_score"])
            
            # Demote the weakest ones until we hit the target
            demote_count = len(highs) - target_high_count
            for i in range(demote_count):
                highs[i]["priority"] = "MEDIUM"
                highs[i]["priority_reasons"].append("Demoted to MEDIUM by distribution guard (target ~30% HIGH)")
                
        return requirements

    def prioritize_clusters(
        self,
        clusters: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Prioritize requirements within clusters, then assign cluster priority.
        """
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

        # Collect ALL sentences for frequency analysis
        all_sentences = []
        for cluster in clusters:
            for req in cluster["requirements"]:
                all_sentences.append(req.get("sentence", ""))

        for cluster in clusters:
            reqs = cluster["requirements"]
            # Prioritize individual requirements and apply guard
            reqs = [
                self.prioritize_requirement(r, all_sentences) for r in reqs
            ]
            reqs = self._apply_distribution_guard(reqs)
            cluster["requirements"] = reqs

            if reqs:
                best = min(
                    reqs,
                    key=lambda r: priority_order.get(r.get("priority", "LOW"), 2),
                )
                cluster["cluster_priority"] = best["priority"]
                cluster["cluster_priority_score"] = best["priority_score"]
            else:
                cluster["cluster_priority"] = "LOW"
                cluster["cluster_priority_score"] = 0

        clusters.sort(
            key=lambda c: priority_order.get(c["cluster_priority"], 2)
        )
        return clusters
