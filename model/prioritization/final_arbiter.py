"""
final_arbiter.py — Final Priority Arbitration Layer
=====================================================
The LAST intelligence layer in the prioritization cascade:

    Phase 6  : NLP signal scoring (keyword / entity based)
    Phase 6b : Semantic correction (domain + urgency patterns)
    Phase 6c : Final arbitration  ← THIS MODULE

This module receives the full accumulated context —  requirement text,
structured data, NLP priority, semantic correction output, AND the
surrounding cluster context — and makes the ultimate, non-appealable
priority decision using deep reasoning.

Key capabilities beyond previous layers:
    • Cross-requirement consistency (cluster-level dedup awareness)
    • Sanity checking (catches contradictions like critical feature → LOW)
    • Agreement tracking with all upstream layers
    • Rich signal decomposition in output

Output per requirement (attached as ``final_arbitration`` key):
    {
        "final_priority": "HIGH",
        "confidence": 0.96,
        "override": false,
        "agreement_with_previous_layers": true,
        "reason": ["...", "..."],
        "signals_detected": {
            "business_critical": true,
            "urgency": false,
            "mandatory_language": true,
            "high_user_impact": true,
            "cosmetic": false
        }
    }

Usage:
    from prioritization.final_arbiter import FinalPriorityArbiter
    arbiter = FinalPriorityArbiter()
    clusters = arbiter.arbitrate_clusters(clusters)
"""

import re
from typing import Any


# ───────────────────────────────────────────────────────────────────────
# Domain Knowledge Registries
# ───────────────────────────────────────────────────────────────────────

# Core features whose disruption blocks fundamental system usage.
# Wider net than the semantic corrector — includes infrastructure.
CRITICAL_FEATURES = {
    # Authentication & identity
    "authentication", "login", "logout", "signup", "register",
    "password", "session", "token", "oauth", "sso", "mfa", "2fa",
    "identity", "credentials", "biometric",
    # Financial
    "payment", "checkout", "billing", "transaction", "invoice",
    "subscription", "refund", "charge", "wallet", "pricing",
    # Security
    "authorization", "permission", "role", "access control", "rbac",
    "encryption", "decrypt", "ssl", "tls", "certificate", "firewall",
    "audit log", "compliance",
    # Infrastructure
    "database", "migration", "backup", "recovery", "restore",
    "api gateway", "load balancer", "cdn", "cache", "queue",
    "deployment", "ci/cd", "monitoring", "alerting",
    # Data integrity
    "data loss", "corruption", "consistency", "replication",
}

# Failure / blocking patterns (semantic, not keyword-only)
FAILURE_PATTERNS = [
    re.compile(r"cannot\s+(access|login|use|proceed|work|connect)", re.I),
    re.compile(r"(blocks?|blocking|blocked)\s+\w+", re.I),
    re.compile(r"(system|service|server|app)\s+(down|crash|fail|offline)", re.I),
    re.compile(r"production\s+(issue|incident|outage|failure|bug)", re.I),
    re.compile(r"(data\s+)?(loss|leak|breach|corruption)", re.I),
    re.compile(r"(no\s+workaround|completely\s+broken|not\s+working)", re.I),
    re.compile(r"(security|vulnerability|exploit|attack)", re.I),
    re.compile(r"(customers?|users?)\s+(unable|cannot|affected)", re.I),
    re.compile(r"(failing|fails?|broken)\s+(in|on|for|during)", re.I),
    re.compile(r"(deadline|launch\s+date|release\s+blocker)", re.I),
]

# Urgency signals (time-pressure, not just bad-state)
URGENCY_PATTERNS = [
    re.compile(r"(immediate(ly)?|right\s+away|as\s+soon\s+as)", re.I),
    re.compile(r"(urgent|asap|critical|emergency|p[01])\b", re.I),
    re.compile(r"(before|by)\s+(deadline|release|launch|eod|end\s+of)", re.I),
    re.compile(r"time[- ]?sensitive", re.I),
    re.compile(r"(customers?\s+)?(complain|escalat)", re.I),
]

# Cosmetic / low-value patterns
COSMETIC_PATTERNS = [
    re.compile(r"(change|update|modify)\s+(color|colour|font|icon|logo|theme)", re.I),
    re.compile(r"(adjust|tweak|align)\s+(spacing|padding|margin|layout)", re.I),
    re.compile(r"(tooltip|placeholder|label)\s+(text|wording|message)", re.I),
    re.compile(r"(rename|relabel)\s+(button|field|tab|menu|link)", re.I),
    re.compile(r"(dark\s+mode|light\s+mode|theme\s+switch)", re.I),
    re.compile(r"(cosmetic|visual\s+polish|aesthetic|look\s+and\s+feel)", re.I),
    re.compile(r"(typo|spelling|grammar)\s+(fix|error|mistake)", re.I),
]

# Mandatory language tiers
STRONG_MANDATORY = {"must", "shall", "required", "mandate", "obligatory", "essential"}
MEDIUM_MANDATORY = {"should", "expected", "need", "needs", "necessary", "important"}
WEAK_OPTIONAL    = {"could", "may", "might", "consider", "nice to have", "optional", "prefer"}

# Broad user-impact signals
IMPACT_PATTERNS = [
    re.compile(r"all\s+users", re.I),
    re.compile(r"every\s+(user|customer|client|employee|member)", re.I),
    re.compile(r"(entire|whole)\s+(team|organization|company|system|platform)", re.I),
    re.compile(r"(public|customer|external)[- ]?facing", re.I),
    re.compile(r"(thousands?|millions?|hundreds?)\s+of\s+(users?|requests?|customers?)", re.I),
    re.compile(r"(high\s+traffic|peak\s+load|at\s+scale)", re.I),
    re.compile(r"(system[- ]?wide|platform[- ]?wide|global)", re.I),
]


class FinalPriorityArbiter:
    """
    Final arbitration layer that makes the ultimate priority decision.

    It receives the full context chain — NLP priority, semantic correction,
    structured data, and cluster neighbors — and applies deep reasoning
    to produce a non-appealable final priority with full transparency.
    """

    def arbitrate(
        self,
        requirement: dict[str, Any],
        cluster_context: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Make the final priority decision for a single requirement.

        Parameters
        ----------
        requirement : dict
            Enriched requirement dict with at minimum:
                - ``sentence``, ``priority``, ``structured``, ``grouped``
                - ``semantic_correction`` (from Phase 6b)
        cluster_context : list[dict], optional
            Other requirements in the same cluster for consistency checks.

        Returns
        -------
        dict
            Original dict enriched with ``final_arbitration`` key.
        """
        sentence = requirement.get("sentence", "")
        sentence_lower = sentence.lower()
        words = set(sentence_lower.split())
        structured = requirement.get("structured", {})
        grouped = requirement.get("grouped", {})

        # Gather upstream decisions
        nlp_priority = requirement.get("priority_score", 0)
        current_priority = requirement.get("priority", "LOW")
        semantic = requirement.get("semantic_correction", {})
        semantic_priority = semantic.get("final_priority", current_priority)

        # ── Detect all signals ────────────────────────────────────────
        signals = {
            "business_critical": False,
            "urgency": False,
            "mandatory_language": False,
            "high_user_impact": False,
            "cosmetic": False,
        }

        score = 0.0
        reasons = []

        # Signal 1: Business criticality
        crit_score, crit_reasons, is_critical = self._assess_criticality(
            sentence_lower, structured, grouped
        )
        score += crit_score
        reasons.extend(crit_reasons)
        signals["business_critical"] = is_critical

        # Signal 2: Failure / blocking scenarios
        fail_score, fail_reasons = self._assess_failure(sentence)
        score += fail_score
        reasons.extend(fail_reasons)
        if fail_score > 0:
            signals["urgency"] = True

        # Signal 3: Explicit urgency / time pressure
        urg_score, urg_reasons = self._assess_urgency(sentence)
        score += urg_score
        reasons.extend(urg_reasons)
        if urg_score > 0:
            signals["urgency"] = True

        # Signal 4: Mandatory language strength
        mand_score, mand_reasons, has_mandatory = self._assess_mandatory(words)
        score += mand_score
        reasons.extend(mand_reasons)
        signals["mandatory_language"] = has_mandatory

        # Signal 5: User impact scope
        imp_score, imp_reasons = self._assess_impact(sentence)
        score += imp_score
        reasons.extend(imp_reasons)
        if imp_score > 0:
            signals["high_user_impact"] = True

        # Signal 6: Cosmetic / trivial detection (negative pressure)
        cos_score, cos_reasons, is_cosmetic = self._assess_cosmetic(sentence)
        score += cos_score
        reasons.extend(cos_reasons)
        signals["cosmetic"] = is_cosmetic

        # ── Cross-requirement consistency ─────────────────────────────
        if cluster_context:
            cons_reasons = self._check_consistency(
                requirement, cluster_context, score
            )
            reasons.extend(cons_reasons)

        # ── Sanity checks ─────────────────────────────────────────────
        sanity_reasons = self._sanity_check(
            signals, semantic_priority, score
        )
        reasons.extend(sanity_reasons)

        # ── Final decision ────────────────────────────────────────────
        final_priority = self._decide(score, semantic_priority, signals)
        override = final_priority != semantic_priority
        agrees = final_priority == semantic_priority
        confidence = self._compute_confidence(score, signals, reasons, agrees)

        if override:
            reasons.append(
                f"Semantic layer said '{semantic_priority}' but final "
                f"arbitration overrides to '{final_priority}'"
            )

        arbitration = {
            "final_priority": final_priority,
            "confidence": round(confidence, 2),
            "override": override,
            "agreement_with_previous_layers": agrees,
            "reason": reasons if reasons else [
                "No strong signals; deferring to upstream priority"
            ],
            "signals_detected": signals,
        }

        requirement["final_arbitration"] = arbitration
        requirement["priority"] = final_priority

        return requirement

    def arbitrate_all(
        self,
        requirements: list[dict[str, Any]],
        cluster_context: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Arbitrate a list of requirements with shared cluster context."""
        ctx = cluster_context or requirements
        return [self.arbitrate(r, ctx) for r in requirements]

    def arbitrate_clusters(
        self,
        clusters: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Apply final arbitration within each cluster, using sibling
        requirements as context, then re-derive cluster priority.
        """
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

        for cluster in clusters:
            reqs = cluster.get("requirements", [])
            cluster["requirements"] = self.arbitrate_all(reqs, reqs)

            # Derive cluster priority from its strongest requirement
            if reqs:
                best = min(
                    reqs,
                    key=lambda r: priority_order.get(
                        r.get("priority", "LOW"), 2
                    ),
                )
                cluster["cluster_priority"] = best["priority"]
            else:
                cluster["cluster_priority"] = "LOW"

            # Track arbitration statistics
            overrides = sum(
                1 for r in reqs
                if r.get("final_arbitration", {}).get("override", False)
            )
            cluster["final_overrides"] = overrides

        clusters.sort(
            key=lambda c: priority_order.get(
                c.get("cluster_priority", "LOW"), 2
            )
        )
        return clusters

    # ───────────────────────────────────────────────────────────────────
    # Private signal assessors
    # ───────────────────────────────────────────────────────────────────

    @staticmethod
    def _assess_criticality(
        sentence_lower: str,
        structured: dict,
        grouped: dict,
    ) -> tuple[float, list[str], bool]:
        """Deep business criticality scan across all available fields."""
        feature = (structured.get("feature") or "").lower()
        action = (structured.get("action") or "").lower()
        all_features = [f.lower() for f in structured.get("all_features", [])]
        ner_features = [f.lower() for f in grouped.get("FEATURE", [])]
        ner_actions = [a.lower() for a in grouped.get("ACTION", [])]

        searchable = " ".join(
            [sentence_lower, feature, action]
            + all_features + ner_features + ner_actions
        )

        matched = [cf for cf in CRITICAL_FEATURES if cf in searchable]
        if matched:
            return (
                5.0,
                [f"Business-critical feature: {', '.join(matched)}"],
                True,
            )
        return 0.0, [], False

    @staticmethod
    def _assess_failure(sentence: str) -> tuple[float, list[str]]:
        """Detect failure, blocking, or system-down scenarios."""
        for pattern in FAILURE_PATTERNS:
            match = pattern.search(sentence)
            if match:
                return (
                    5.0,
                    [f"Failure/blocking scenario: '{match.group()}'"],
                )
        return 0.0, []

    @staticmethod
    def _assess_urgency(sentence: str) -> tuple[float, list[str]]:
        """Detect explicit urgency or time pressure."""
        for pattern in URGENCY_PATTERNS:
            match = pattern.search(sentence)
            if match:
                return (
                    4.0,
                    [f"Urgency signal: '{match.group()}'"],
                )
        return 0.0, []

    @staticmethod
    def _assess_mandatory(words: set[str]) -> tuple[float, list[str], bool]:
        """Evaluate the strength of mandatory/optional language."""
        strong = words & STRONG_MANDATORY
        medium = words & MEDIUM_MANDATORY
        weak = words & WEAK_OPTIONAL

        if strong:
            return (
                2.0,
                [f"Strong mandatory language: '{', '.join(sorted(strong))}'"],
                True,
            )
        elif medium:
            return (
                1.0,
                [f"Moderate mandatory language: '{', '.join(sorted(medium))}'"],
                True,
            )
        elif weak:
            return (
                -1.0,
                [f"Weak/optional language: '{', '.join(sorted(weak))}'"],
                False,
            )
        return 0.0, [], False

    @staticmethod
    def _assess_impact(sentence: str) -> tuple[float, list[str]]:
        """Detect signals indicating broad user or system impact."""
        for pattern in IMPACT_PATTERNS:
            match = pattern.search(sentence)
            if match:
                return (
                    3.0,
                    [f"High user impact: '{match.group()}'"],
                )
        return 0.0, []

    @staticmethod
    def _assess_cosmetic(sentence: str) -> tuple[float, list[str], bool]:
        """Detect cosmetic/trivial UI changes that should be LOW."""
        for pattern in COSMETIC_PATTERNS:
            match = pattern.search(sentence)
            if match:
                return (
                    -4.0,
                    [f"Cosmetic/trivial change: '{match.group()}'"],
                    True,
                )
        return 0.0, [], False

    @staticmethod
    def _check_consistency(
        requirement: dict,
        cluster_context: list[dict],
        current_score: float,
    ) -> list[str]:
        """
        Ensure the requirement's priority is consistent with its
        cluster siblings. If siblings expressing the same intent
        have a higher priority, flag a potential inconsistency.
        """
        reasons = []
        my_priority = requirement.get("priority", "LOW")
        priority_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        my_rank = priority_rank.get(my_priority, 2)

        # Check if most siblings have a different priority
        sibling_priorities = [
            r.get("priority", "LOW")
            for r in cluster_context
            if r.get("sentence") != requirement.get("sentence")
        ]

        if sibling_priorities:
            higher_count = sum(
                1 for p in sibling_priorities
                if priority_rank.get(p, 2) < my_rank
            )
            if higher_count > len(sibling_priorities) * 0.6:
                reasons.append(
                    f"Cluster consistency: {higher_count}/{len(sibling_priorities)} "
                    f"siblings have higher priority — consider alignment"
                )

        return reasons

    @staticmethod
    def _sanity_check(
        signals: dict[str, bool],
        semantic_priority: str,
        score: float,
    ) -> list[str]:
        """
        Catch contradictions that upstream layers may have missed.
        E.g. a business-critical feature marked LOW, or a cosmetic
        change marked HIGH.
        """
        reasons = []

        # Critical feature should never be LOW
        if signals["business_critical"] and semantic_priority == "LOW":
            reasons.append(
                "Sanity check: business-critical feature was marked LOW "
                "— correcting upward"
            )

        # Cosmetic change should never be HIGH
        if signals["cosmetic"] and semantic_priority == "HIGH":
            reasons.append(
                "Sanity check: cosmetic change was marked HIGH "
                "— correcting downward"
            )

        # Urgency + business critical should be HIGH
        if (
            signals["urgency"]
            and signals["business_critical"]
            and semantic_priority != "HIGH"
        ):
            reasons.append(
                "Sanity check: urgent + business-critical combination "
                "should be HIGH priority"
            )

        return reasons

    @staticmethod
    def _decide(
        score: float,
        semantic_priority: str,
        signals: dict[str, bool],
    ) -> str:
        """
        Make the final, non-appealable priority decision.

        Decision hierarchy:
          1. Hard overrides for clear contradictions
          2. Score-based decision for strong signals
          3. Defer to semantic layer for ambiguous cases
        """
        # Hard override: cosmetic is always LOW regardless of score
        if signals["cosmetic"] and not signals["business_critical"]:
            return "LOW"

        # Hard override: urgent + business-critical is always HIGH
        if signals["urgency"] and signals["business_critical"]:
            return "HIGH"

        # Hard override: business-critical + mandatory is always HIGH
        if signals["business_critical"] and signals["mandatory_language"]:
            return "HIGH"

        # Score-based decision for strong signals
        if score >= 8.0:
            return "HIGH"
        elif score >= 5.0:
            # Strong evidence — at least MEDIUM, HIGH if score is decisive
            return "HIGH" if score >= 7.0 else "MEDIUM" if semantic_priority != "HIGH" else "HIGH"
        elif score >= 2.0:
            # Moderate evidence — trust semantic layer if it's reasonable
            if semantic_priority == "LOW" and signals["business_critical"]:
                return "MEDIUM"
            return semantic_priority
        elif score <= -2.0:
            return "LOW"
        else:
            # Weak/ambiguous — defer to semantic layer
            return semantic_priority

    @staticmethod
    def _compute_confidence(
        score: float,
        signals: dict[str, bool],
        reasons: list[str],
        agrees: bool,
    ) -> float:
        """
        Compute confidence (0–1) based on signal strength,
        corroboration depth, and agreement with upstream layers.
        """
        abs_score = abs(score)

        # Base confidence from score magnitude
        base = min(0.50 + (abs_score * 0.05), 0.92)

        # Bonus for multiple corroborating signals
        active_signals = sum(1 for v in signals.values() if v)
        corroboration = min(active_signals * 0.04, 0.12)

        # Bonus for agreement with upstream (consensus = confidence)
        agreement_bonus = 0.06 if agrees else 0.0

        # Bonus for having many concrete reasons
        reason_bonus = min(len(reasons) * 0.02, 0.08)

        return min(base + corroboration + agreement_bonus + reason_bonus, 0.98)
