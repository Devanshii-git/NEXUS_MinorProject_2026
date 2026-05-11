"""
generator.py — Improved Structured Output Generator
======================================================
Outputs structured requirement documents with:
  • Actor-action-constraint breakdown per requirement
  • Requirement type (functional / non-functional)
  • Priority explanation (explainability)
  • Cluster quality metrics
  • JSON, Markdown, and Console formats
"""

import json
import os
import numpy as np
from datetime import datetime
from typing import Any


class OutputGenerator:
    """Generate structured requirement documents from pipeline output."""

    # -----------------------------------------------------------------------
    # JSON Output
    # -----------------------------------------------------------------------
    def to_json(
        self,
        clusters: list[dict[str, Any]],
        output_path: str = "output/requirements.json",
    ) -> str:
        """Save pipeline results as a structured JSON file."""
        document = {
            "metadata": {
                "title": "Software Requirements Specification",
                "generated_at": datetime.now().isoformat(),
                "total_requirements": sum(len(c["requirements"]) for c in clusters),
                "total_clusters": len(clusters),
            },
            "requirement_groups": [],
        }

        for cluster in clusters:
            group = {
                "group_id": f"REQ-{cluster['cluster_id'] + 1:03d}",
                "group_name": cluster["cluster_name"],
                "priority": cluster.get("cluster_priority", "LOW"),
                "summary": cluster.get("cluster_summary", ""),
                "silhouette_score": cluster.get("silhouette_score"),
                "explanation": cluster.get("cluster_explanation", ""),
                "requirements": [],
            }

            for req in cluster["requirements"]:
                structured = req.get("structured", {})
                req_entry = {
                    "sentence": req["sentence"],
                    "confidence": req.get("confidence", 0),
                    "priority": req.get("priority", "LOW"),
                    "priority_score": req.get("priority_score", 0),
                    "priority_reasons": req.get("priority_reasons", []),
                    "requirement_type": structured.get("requirement_type", "unknown"),
                    "structured": {
                        "actor": structured.get("actor"),
                        "action": structured.get("action"),
                        "feature": structured.get("feature"),
                        "all_features": structured.get("all_features", []),
                        "quality_attribute": structured.get("quality_attribute"),
                        "constraints": structured.get("constraints", []),
                        "priority_indicator": structured.get("priority_indicator"),
                        "canonical_statement": structured.get("structured_statement", ""),
                    },
                    "entities": {
                        "actors": req.get("grouped", {}).get("ACTOR", []),
                        "actions": req.get("grouped", {}).get("ACTION", []),
                        "features": req.get("grouped", {}).get("FEATURE", []),
                        "quality_attributes": req.get("grouped", {}).get("QUALITY_ATTRIBUTE", []),
                        "constraints": req.get("grouped", {}).get("CONSTRAINT", []),
                        "priority_indicators": req.get("grouped", {}).get("PRIORITY_INDICATOR", []),
                    },
                }
                group["requirements"].append(req_entry)

            document["requirement_groups"].append(group)

        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super(NpEncoder, self).default(obj)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(document, f, indent=2, ensure_ascii=False, cls=NpEncoder)

        print(f"[OK] JSON output saved to: {output_path}")
        return output_path

    # -----------------------------------------------------------------------
    # Markdown Output (SRS Document)
    # -----------------------------------------------------------------------
    def to_markdown(
        self,
        clusters: list[dict[str, Any]],
        output_path: str = "output/requirements.md",
    ) -> str:
        """Generate a Markdown SRS document with structured breakdown."""
        lines = []
        total_reqs = sum(len(c["requirements"]) for c in clusters)

        # Header
        lines.append("# Software Requirements Specification (SRS)")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Requirements:** {total_reqs}")
        lines.append(f"**Requirement Groups:** {len(clusters)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("")
        for cluster in clusters:
            gid = f"REQ-{cluster['cluster_id'] + 1:03d}"
            name = cluster["cluster_name"]
            pri = cluster.get("cluster_priority", "LOW")
            n = len(cluster["requirements"])
            lines.append(f"- **{gid}: {name}** [{pri}] ({n} req)")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Requirement Groups
        for cluster in clusters:
            gid = f"REQ-{cluster['cluster_id'] + 1:03d}"
            name = cluster["cluster_name"]
            pri = cluster.get("cluster_priority", "LOW")
            summary = cluster.get("cluster_summary", "")
            explanation = cluster.get("cluster_explanation", "")

            badge = {"HIGH": "🔴 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🟢 LOW"}.get(pri, pri)

            lines.append(f"## {gid}: {name}")
            lines.append("")
            lines.append(f"**Priority:** {badge}")
            if summary:
                lines.append(f"**Summary:** {summary}")
            if explanation:
                lines.append(f"**Analysis:** {explanation}")
            lines.append("")

            lines.append("### Requirements")
            lines.append("")

            for i, req in enumerate(cluster["requirements"], 1):
                structured = req.get("structured", {})
                req_type = structured.get("requirement_type", "unknown")
                type_badge = "⚙️ Functional" if req_type == "functional" else "📊 Non-Functional"

                lines.append(f"**{gid}.{i}:** {req['sentence']}")
                lines.append("")
                lines.append(f"*Type: {type_badge}*")
                lines.append("")

                # Structured breakdown
                lines.append("| Attribute | Value |")
                lines.append("|-----------|-------|")
                if structured.get("actor"):
                    lines.append(f"| **Actor** | {structured['actor']} |")
                if structured.get("action"):
                    lines.append(f"| **Action** | {structured['action']} |")
                if structured.get("feature"):
                    lines.append(f"| **Feature** | {structured['feature']} |")
                if structured.get("quality_attribute"):
                    lines.append(f"| **Quality** | {structured['quality_attribute']} |")
                for c in structured.get("constraints", []):
                    lines.append(f"| **Constraint** | {c} |")
                if structured.get("priority_indicator"):
                    lines.append(f"| **Priority Indicator** | {structured['priority_indicator']} |")
                lines.append("")

                # Canonical form
                canon = structured.get("structured_statement", "")
                if canon:
                    lines.append(f"> **Canonical:** {canon}")
                    lines.append("")

                # Priority explanation
                req_pri = req.get("priority", "LOW")
                reasons = req.get("priority_reasons", [])
                conf = req.get("confidence", 0)
                lines.append(f"**Priority: {req_pri}** | Confidence: {conf:.1%}")
                if reasons:
                    for reason in reasons:
                        lines.append(f"  - {reason}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Limitations & Future Scope
        lines.append("## Limitations & Future Improvements")
        lines.append("")
        lines.append("While the current pipeline demonstrates a functional end-to-end AI Requirements Engineering system, there are several avenues for future enhancement:")
        lines.append("")
        lines.append("- **Clustering Algorithms:** The current Agglomerative approach works well for small datasets. For larger corpora, transitioning to **BERTopic** would provide dynamic, topic-aware groupings.")
        lines.append("- **NER Accuracy:** The Named Entity Recognition model is currently trained on a highly restricted dataset. Expanding this dataset with diverse domain-specific requirements will dramatically improve boundary detection and recall.")
        lines.append("- **Real-time Integration:** The system currently processes static text chunks. Future iterations should integrate with **Jira, Slack, or Trello APIs** to pull requirements dynamically and log structured outputs directly into project management tools.")
        lines.append("- **Advanced Prioritization:** Currently, prioritization is driven by a rule-based multi-signal engine. Transitioning to a **learning-based model** (e.g., fine-tuning a transformer on historical project priority data) would yield more nuanced and context-aware scoring.")
        lines.append("")
        lines.append("---")
        lines.append("")

        content = "\n".join(lines)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[OK] Markdown SRS saved to: {output_path}")
        return output_path

    # -----------------------------------------------------------------------
    # Console Output
    # -----------------------------------------------------------------------
    def to_console(self, clusters: list[dict[str, Any]]) -> None:
        """Pretty-print the full pipeline results to the terminal."""
        total_reqs = sum(len(c["requirements"]) for c in clusters)
        print()
        print("=" * 70)
        print("  SOFTWARE REQUIREMENTS SPECIFICATION (IMPROVED)")
        print("=" * 70)
        print(f"  Total Requirements : {total_reqs}")
        print(f"  Requirement Groups : {len(clusters)}")
        print("=" * 70)

        for cluster in clusters:
            gid = f"REQ-{cluster['cluster_id'] + 1:03d}"
            name = cluster["cluster_name"]
            pri = cluster.get("cluster_priority", "LOW")
            summary = cluster.get("cluster_summary", "")

            print()
            print(f"  +--- {gid}: {name}  [{pri}]")
            if summary:
                print(f"  |  Summary: {summary}")

            explanation = cluster.get("cluster_explanation", "")
            if explanation:
                print(f"  |  Analysis: {explanation}")

            for i, req in enumerate(cluster["requirements"], 1):
                structured = req.get("structured", {})
                req_type = structured.get("requirement_type", "unknown")
                prefix = "  |"

                print(f"{prefix}")
                print(f"{prefix}  {gid}.{i}: {req['sentence']}")
                print(f"{prefix}    Type: {req_type}")

                if structured.get("actor"):
                    print(f"{prefix}    Actor      : {structured['actor']}")
                if structured.get("action"):
                    print(f"{prefix}    Action     : {structured['action']}")
                if structured.get("feature"):
                    print(f"{prefix}    Feature    : {structured['feature']}")
                if structured.get("quality_attribute"):
                    print(f"{prefix}    Quality    : {structured['quality_attribute']}")
                for c in structured.get("constraints", []):
                    print(f"{prefix}    Constraint : {c}")

                req_pri = req.get("priority", "LOW")
                score = req.get("priority_score", 0)
                conf = req.get("confidence", 0)
                print(f"{prefix}    Priority: {req_pri} (score: {score}) | Confidence: {conf:.1%}")

                # Show priority reasons
                reasons = req.get("priority_reasons", [])
                for reason in reasons:
                    print(f"{prefix}      -> {reason}")

            print("  +" + "-" * 66)

        print()
        print("=" * 70)
