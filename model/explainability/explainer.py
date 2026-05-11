"""
explainer.py — Explainability Engine
=======================================
Generates human-readable explanations for every pipeline decision:

  • Why was this classified as a requirement?
  • What entities were extracted and why?
  • Why was this priority assigned?
  • Why were these requirements clustered together?

Example output:
    Priority = HIGH because:
      • Contains urgency keyword: 'urgent' (+3)
      • Negative sentiment detected: 'slow', 'complaint' (+2)
      • Strong modal verb: 'must' (+1)
      • Total score: 6/10

Usage:
    from explainability.explainer import ExplainabilityEngine

    explainer = ExplainabilityEngine()
    explanation = explainer.explain_requirement(req_dict)
"""

from typing import Any


class ExplainabilityEngine:
    """
    Generate transparent, human-readable explanations for all
    pipeline decisions on a requirement.
    """

    def explain_requirement(self, requirement: dict[str, Any]) -> dict[str, Any]:
        """
        Generate a complete explanation for a single requirement.

        Parameters
        ----------
        requirement : dict
            Enriched requirement dict from the pipeline (with NER,
            priority, and structured data)

        Returns
        -------
        dict
            Explanation dict with keys:
                classification_explanation
                entity_explanation
                priority_explanation
                structuring_explanation
                full_explanation (human-readable string)
        """
        explanation = {}

        # --- 1. Classification explanation ----------------------------------
        confidence = requirement.get("confidence", 0)
        explanation["classification"] = {
            "decision": "Requirement",
            "confidence": confidence,
            "reasoning": (
                f"Classified as a requirement with {confidence:.1%} confidence "
                f"by the DistilBERT classifier. The model identified patterns "
                f"consistent with software requirement language (modal verbs, "
                f"action statements, system references)."
            ),
        }

        # --- 2. Entity extraction explanation --------------------------------
        grouped = requirement.get("grouped", {})
        entity_reasons = []
        for label, values in grouped.items():
            for val in values:
                entity_reasons.append(f"'{val}' → {label}")

        explanation["entities"] = {
            "total_entities": sum(len(v) for v in grouped.values()),
            "entity_types_found": list(grouped.keys()),
            "details": entity_reasons,
            "reasoning": (
                f"Found {sum(len(v) for v in grouped.values())} entities "
                f"across {len(grouped)} types using BERT-based NER."
            ),
        }

        # --- 3. Priority explanation ----------------------------------------
        priority = requirement.get("priority", "LOW")
        priority_score = requirement.get("priority_score", 0)
        priority_reasons = requirement.get("priority_reasons", [])

        explanation["priority"] = {
            "level": priority,
            "score": priority_score,
            "signals": priority_reasons,
            "reasoning": self._build_priority_narrative(
                priority, priority_score, priority_reasons
            ),
        }

        # --- 4. Structuring explanation -------------------------------------
        structured = requirement.get("structured", {})
        if structured:
            explanation["structuring"] = {
                "requirement_type": structured.get("requirement_type", "unknown"),
                "actor": structured.get("actor"),
                "action": structured.get("action"),
                "feature": structured.get("feature"),
                "constraints": structured.get("constraints", []),
                "canonical_form": structured.get("structured_statement", ""),
                "reasoning": (
                    f"Classified as {structured.get('requirement_type', 'unknown')} requirement. "
                    + (
                        f"Non-functional due to quality/constraint attributes."
                        if structured.get("requirement_type") == "non-functional"
                        else f"Functional: describes a specific system capability."
                    )
                ),
            }

        # --- 5. Full explanation (human-readable narrative) -----------------
        explanation["full_text"] = self._build_full_explanation(
            requirement, explanation
        )

        requirement["explanation"] = explanation
        return requirement

    def explain_all(
        self,
        requirements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Explain a list of requirements."""
        return [self.explain_requirement(r) for r in requirements]

    def explain_clusters(
        self,
        clusters: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Explain all requirements within clusters and add
        cluster-level explanations.
        """
        for cluster in clusters:
            cluster["requirements"] = self.explain_all(
                cluster["requirements"]
            )

            # Cluster-level explanation
            n_reqs = len(cluster["requirements"])
            cluster_name = cluster.get("cluster_name", "Unknown")
            cluster_priority = cluster.get("cluster_priority", "LOW")
            sil = cluster.get("silhouette_score", None)

            cluster_explanation = (
                f"Cluster '{cluster_name}' contains {n_reqs} requirement(s) "
                f"grouped by semantic similarity. "
                f"Cluster priority: {cluster_priority}."
            )
            if sil is not None and sil > 0:
                cluster_explanation += (
                    f" Clustering quality (silhouette): {sil:.2f} "
                    f"({'good' if sil > 0.5 else 'moderate' if sil > 0.25 else 'weak'})."
                )
            cluster["cluster_explanation"] = cluster_explanation

        return clusters

    @staticmethod
    def _build_priority_narrative(
        priority: str,
        score: float,
        reasons: list[str],
    ) -> str:
        """Build a human-readable priority explanation."""
        narrative = f"Priority = {priority} (score: {score}) because:\n"
        for reason in reasons:
            narrative += f"  • {reason}\n"
        return narrative.rstrip()

    @staticmethod
    def _build_full_explanation(
        requirement: dict[str, Any],
        explanation: dict[str, Any],
    ) -> str:
        """Build a complete human-readable explanation paragraph."""
        sentence = requirement.get("sentence", "")
        lines = [
            f"Requirement: \"{sentence}\"",
            "",
            f"Classification: {explanation['classification']['reasoning']}",
            "",
            f"Entities: {explanation['entities']['reasoning']}",
        ]
        for detail in explanation["entities"]["details"]:
            lines.append(f"  • {detail}")

        lines.append("")
        lines.append(explanation["priority"]["reasoning"])

        if "structuring" in explanation:
            lines.append("")
            lines.append(f"Structure: {explanation['structuring']['reasoning']}")
            lines.append(f"  Canonical: {explanation['structuring']['canonical_form']}")

        return "\n".join(lines)
