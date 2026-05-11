"""
audit_analyzer.py — LLM Audit Disagreement Analysis
=====================================================
Analyzes disagreements between the rule-based ``FinalPriorityArbiter``
and the ``LLMAuditor`` to identify patterns that can be used to
refine rules or retrain models.

Reads pipeline output JSON or the JSONL disagreement log and
produces a structured Markdown report.

Usage:
    # From pipeline output JSON:
    python -m evaluation.audit_analyzer --source output/requirements.json

    # From disagreement log:
    python -m evaluation.audit_analyzer --source output/llm_audit_log.jsonl

    # Programmatic:
    from evaluation.audit_analyzer import AuditAnalyzer
    analyzer = AuditAnalyzer()
    analyzer.analyze_from_log("output/llm_audit_log.jsonl")
"""

import argparse
import json
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Any

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless environments
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize


class AuditAnalyzer:
    """
    Analyzes LLM audit results to find disagreement patterns
    and generate actionable improvement reports.
    """

    def analyze_from_pipeline_output(
        self,
        json_path: str,
    ) -> dict[str, Any]:
        """
        Extract and analyze LLM audit data from full pipeline output.

        Parameters
        ----------
        json_path : str
            Path to the pipeline output JSON (list of clusters).

        Returns
        -------
        dict
            Analysis results with statistics and case details.
        """
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        clusters = data.get("requirement_groups", []) if isinstance(data, dict) else data

        all_audits = []
        for cluster in clusters:
            for req in cluster.get("requirements", []):
                audit = req.get("llm_audit", {})
                if not audit.get("skipped", True):
                    all_audits.append({
                        "text": req.get("sentence", "")[:200],
                        "arbiter_priority": req.get(
                            "final_arbitration", {}
                        ).get("final_priority", "N/A"),
                        "arbiter_confidence": req.get(
                            "final_arbitration", {}
                        ).get("confidence", 0.0),
                        "arbiter_reasons": req.get(
                            "final_arbitration", {}
                        ).get("reason", []),
                        "llm_priority": audit.get("llm_priority"),
                        "llm_confidence": audit.get("llm_confidence"),
                        "llm_reasons": audit.get("llm_reason", []),
                        "agrees": audit.get("agrees_with_arbiter", True),
                        "disagreement_details": audit.get(
                            "disagreement_details"
                        ),
                    })

        return self._compute_analysis(all_audits)

    def analyze_from_log(
        self,
        log_path: str,
    ) -> dict[str, Any]:
        """
        Analyze disagreements from the JSONL log file.

        Parameters
        ----------
        log_path : str
            Path to ``output/llm_audit_log.jsonl``.

        Returns
        -------
        dict
            Analysis with disagreement patterns and recommendations.
        """
        entries = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Convert log entries to audit format
        all_audits = []
        for entry in entries:
            all_audits.append({
                "text": entry.get("text", "")[:200],
                "arbiter_priority": entry.get("arbiter_priority", "N/A"),
                "arbiter_confidence": entry.get("arbiter_confidence", 0.0),
                "arbiter_reasons": entry.get("arbiter_reasons", []),
                "llm_priority": entry.get("llm_priority"),
                "llm_confidence": entry.get("llm_confidence", 0.0),
                "llm_reasons": entry.get("llm_reasons", []),
                "agrees": False,  # Log only contains disagreements
                "disagreement_details": {
                    "arbiter_said": entry.get("arbiter_priority"),
                    "llm_said": entry.get("llm_priority"),
                },
                "timestamp": entry.get("timestamp"),
            })

        return self._compute_analysis(all_audits)

    def generate_report(
        self,
        analysis: dict[str, Any],
        output_path: str = "output/audit_report.md",
    ) -> str:
        """
        Generate a Markdown report from the analysis results.

        Parameters
        ----------
        analysis : dict
            Output from ``analyze_from_pipeline_output`` or
            ``analyze_from_log``.
        output_path : str
            Where to save the report.

        Returns
        -------
        str
            The generated Markdown content.
        """
        stats = analysis["statistics"]
        disagreements = analysis["disagreements"]
        patterns = analysis["patterns"]
        recommendations = analysis["recommendations"]

        lines = [
            "# LLM Audit — Disagreement Analysis Report",
            "",
            f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
            "",
            "## Summary Statistics",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Audited | {stats['total_audited']} |",
            f"| Agreements | {stats['agreements']} ({stats['agreement_rate']:.1f}%) |",
            f"| Disagreements | {stats['disagreements']} ({stats['disagreement_rate']:.1f}%) |",
            "",
        ]

        # Confusion Matrix
        confusion_matrix = analysis.get("confusion_matrix", {})
        if confusion_matrix:
            labels = list(confusion_matrix.keys())
            if labels:
                lines.extend([
                    "## Confusion Matrix",
                    "",
                    "Rows: Arbiter Priority (Actual), Columns: LLM Priority (Predicted)",
                    "",
                    "| Arbiter \\ LLM | " + " | ".join(labels) + " |",
                    "|---" + "|---" * len(labels) + "|",
                ])
                for r_label in labels:
                    row = [r_label]
                    for c_label in labels:
                        row.append(str(confusion_matrix[r_label][c_label]))
                    lines.append("| " + " | ".join(row) + " |")
                lines.append("")

        # Disagreement patterns
        if patterns:
            lines.extend([
                "## Disagreement Patterns",
                "",
                "| Arbiter Said | LLM Said | Count |",
                "|-------------|----------|-------|",
            ])
            for pattern, count in patterns.items():
                lines.append(f"| {pattern.split('→')[0]} | {pattern.split('→')[1]} | {count} |")
            lines.append("")

        # Individual disagreement cases
        if disagreements:
            lines.extend([
                "## Disagreement Cases",
                "",
            ])
            for i, case in enumerate(disagreements[:20], 1):  # Cap at 20
                lines.extend([
                    f"### Case {i}",
                    "",
                    f"**Text:** {case['text']}",
                    "",
                    f"| | Arbiter | LLM |",
                    f"|---|---------|-----|",
                    f"| Priority | {case['arbiter_priority']} | {case['llm_priority']} |",
                    f"| Confidence | {case['arbiter_confidence']:.2f} | {case.get('llm_confidence', 0):.2f} |",
                    "",
                    f"**Arbiter Reasons:** {'; '.join(case.get('arbiter_reasons', [])[:3])}",
                    "",
                    f"**LLM Reasons:** {'; '.join(case.get('llm_reasons', [])[:3])}",
                    "",
                    "---",
                    "",
                ])

        # ROC Curve
        roc_path = analysis.get("roc_curve_path")
        if roc_path:
            lines.extend([
                "## ROC Curve (One-vs-Rest)",
                "",
                f"![ROC Curve]({os.path.basename(roc_path)})",
                "",
            ])

        # Recommendations
        if recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        content = "\n".join(lines)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  Audit report saved to {output_path}")
        return content

    # ── ROC Curve Generation ───────────────────────────────────────────

    @staticmethod
    def generate_roc_curve(
        audits: list[dict[str, Any]],
        output_path: str = "output/roc_curve.png",
    ) -> str | None:
        """
        Generate a One-vs-Rest ROC curve for each priority class.

        Uses the **arbiter priority** as the ground-truth label and the
        **LLM confidence** as the predicted score.  For each class
        (e.g. HIGH), a binary indicator is built (1 = this class,
        0 = any other class) and the LLM confidence is used as the
        positive-class score when the LLM predicted that class, or
        ``1 − confidence`` otherwise.

        Parameters
        ----------
        audits : list[dict]
            List of audit dicts (same format used by ``_compute_analysis``).
        output_path : str
            File path where the PNG will be saved.

        Returns
        -------
        str or None
            The path to the saved PNG, or ``None`` if there was
            insufficient data to plot.
        """
        # Filter to audits that have usable confidence values
        valid = [
            a for a in audits
            if a.get("arbiter_priority") not in (None, "N/A", "?")
            and a.get("llm_priority") not in (None, "N/A", "?")
            and a.get("llm_confidence") is not None
        ]

        if len(valid) < 2:
            print("  ⚠ Not enough audited samples to generate ROC curve.")
            return None

        # Determine class labels in canonical order
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        all_labels = sorted(
            {a["arbiter_priority"] for a in valid} | {a["llm_priority"] for a in valid},
            key=lambda x: priority_order.get(x, 99),
        )

        if len(all_labels) < 2:
            print("  ⚠ Only one class present — ROC curve requires at least two.")
            return None

        # Build ground-truth and score arrays
        y_true = np.array([a["arbiter_priority"] for a in valid])
        y_pred_labels = np.array([a["llm_priority"] for a in valid])
        y_conf = np.array([float(a["llm_confidence"]) for a in valid])

        # Binarize ground truth
        y_true_bin = label_binarize(y_true, classes=all_labels)
        # Handle the special case of exactly 2 classes (label_binarize returns 1 column)
        if y_true_bin.shape[1] == 1:
            y_true_bin = np.hstack([1 - y_true_bin, y_true_bin])

        # Build per-class score matrix:
        # For each sample, the score for class c =
        #   confidence       if the LLM predicted class c
        #   1 − confidence   if the LLM predicted a different class
        n_classes = len(all_labels)
        y_score = np.zeros((len(valid), n_classes))
        for i, (pred_label, conf) in enumerate(zip(y_pred_labels, y_conf)):
            for j, label in enumerate(all_labels):
                if pred_label == label:
                    y_score[i, j] = conf
                else:
                    y_score[i, j] = (1.0 - conf) / max(n_classes - 1, 1)

        # Plot
        colors = ["#e74c3c", "#f39c12", "#2ecc71", "#3498db", "#9b59b6"]
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")

        for idx, label in enumerate(all_labels):
            fpr, tpr, _ = roc_curve(y_true_bin[:, idx], y_score[:, idx])
            roc_auc = auc(fpr, tpr)
            color = colors[idx % len(colors)]
            ax.plot(
                fpr, tpr,
                color=color,
                linewidth=2.2,
                label=f"{label}  (AUC = {roc_auc:.2f})",
            )

        # Diagonal reference
        ax.plot([0, 1], [0, 1], "--", color="#636e72", linewidth=1)

        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel("False Positive Rate", color="white", fontsize=12)
        ax.set_ylabel("True Positive Rate", color="white", fontsize=12)
        ax.set_title(
            "ROC Curve — Arbiter vs LLM (One-vs-Rest)",
            color="white", fontsize=14, fontweight="bold",
        )
        ax.legend(loc="lower right", fontsize=10, facecolor="#2d2d44", edgecolor="#636e72", labelcolor="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("#636e72")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)

        print(f"  ROC curve saved to {output_path}")
        return output_path

    # ── Private Analysis Logic ─────────────────────────────────────────

    @staticmethod
    def _compute_analysis(
        audits: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Compute statistics, patterns, and recommendations."""
        total = len(audits)
        agreements = sum(1 for a in audits if a.get("agrees", True))
        disagreements_list = [a for a in audits if not a.get("agrees", True)]
        num_disagreements = len(disagreements_list)

        # Disagreement patterns (e.g., "HIGH → LOW": 3)
        pattern_counter: Counter = Counter()
        all_labels = set()
        for case in audits:
            arbiter = case.get("arbiter_priority", "?")
            llm = case.get("llm_priority", "?")
            all_labels.add(arbiter)
            all_labels.add(llm)

        for case in disagreements_list:
            arbiter = case.get("arbiter_priority", "?")
            llm = case.get("llm_priority", "?")
            pattern_counter[f"{arbiter} → {llm}"] += 1

        # Confusion Matrix
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_labels = sorted(list(all_labels - {"?"}), key=lambda x: priority_order.get(x, 99))
        if "?" in all_labels:
            sorted_labels.append("?")

        confusion_matrix = {r: {c: 0 for c in sorted_labels} for r in sorted_labels}
        for case in audits:
            arbiter = case.get("arbiter_priority", "?")
            llm = case.get("llm_priority", "?")
            confusion_matrix[arbiter][llm] += 1

        # Generate recommendations
        recommendations = []

        if total == 0:
            recommendations.append(
                "No audited cases found. Run the pipeline with "
                "enable_llm_audit=True to generate audit data."
            )
        elif num_disagreements == 0:
            recommendations.append(
                "Perfect agreement between rule-based arbiter and LLM. "
                "No rule changes needed."
            )
        else:
            rate = (num_disagreements / total * 100) if total else 0

            if rate > 20:
                recommendations.append(
                    f"High disagreement rate ({rate:.1f}%). "
                    "Review rule-based scoring thresholds and domain "
                    "knowledge dictionaries."
                )
            elif rate > 10:
                recommendations.append(
                    f"Moderate disagreement rate ({rate:.1f}%). "
                    "Review individual cases for potential rule improvements."
                )
            else:
                recommendations.append(
                    f"Low disagreement rate ({rate:.1f}%). "
                    "System is well-calibrated."
                )

            # Pattern-specific recommendations
            for pattern, count in pattern_counter.most_common(3):
                arbiter_said, llm_said = pattern.split(" → ")
                if arbiter_said == "LOW" and llm_said == "HIGH":
                    recommendations.append(
                        f"Arbiter underestimates {count} requirement(s) "
                        f"that LLM considers HIGH. Check if business "
                        f"criticality patterns need expansion."
                    )
                elif arbiter_said == "HIGH" and llm_said == "LOW":
                    recommendations.append(
                        f"Arbiter overestimates {count} requirement(s) "
                        f"that LLM considers LOW. Check for false "
                        f"positives in critical feature matching."
                    )

        return {
            "statistics": {
                "total_audited": total,
                "agreements": agreements,
                "disagreements": num_disagreements,
                "agreement_rate": (agreements / total * 100) if total else 0,
                "disagreement_rate": (
                    num_disagreements / total * 100
                ) if total else 0,
            },
            "disagreements": disagreements_list,
            "patterns": dict(pattern_counter.most_common()),
            "confusion_matrix": confusion_matrix,
            "recommendations": recommendations,
        }


# ───────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze LLM audit disagreements."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to pipeline output JSON or JSONL disagreement log.",
    )
    parser.add_argument(
        "--output",
        default="output/audit_report.md",
        help="Path for the generated Markdown report.",
    )
    args = parser.parse_args()

    analyzer = AuditAnalyzer()

    if args.source.endswith(".jsonl"):
        analysis = analyzer.analyze_from_log(args.source)
    else:
        analysis = analyzer.analyze_from_pipeline_output(args.source)

    # Generate ROC curve and attach path to analysis for the report
    roc_output = os.path.join(
        os.path.dirname(args.output), "roc_curve.png"
    )
    all_audits = analysis["disagreements"]  # disagreements only from log
    # For a full picture, re-extract all audits (agreements + disagreements)
    if args.source.endswith(".jsonl"):
        # Log only has disagreements, still plot what we can
        roc_path = analyzer.generate_roc_curve(all_audits, roc_output)
    else:
        # Re-read to get all audits including agreements
        with open(args.source, "r", encoding="utf-8") as f:
            data = json.load(f)
        clusters = data.get("requirement_groups", []) if isinstance(data, dict) else data
        full_audits = []
        for cluster in clusters:
            for req in cluster.get("requirements", []):
                audit = req.get("llm_audit", {})
                if not audit.get("skipped", True):
                    full_audits.append({
                        "arbiter_priority": req.get(
                            "final_arbitration", {}
                        ).get("final_priority", "N/A"),
                        "llm_priority": audit.get("llm_priority"),
                        "llm_confidence": audit.get("llm_confidence"),
                    })
        roc_path = analyzer.generate_roc_curve(full_audits, roc_output)

    analysis["roc_curve_path"] = roc_path
    analyzer.generate_report(analysis, args.output)

    stats = analysis["statistics"]
    print(f"\n  Total audited: {stats['total_audited']}")
    print(f"  Agreements: {stats['agreements']}")
    print(f"  Disagreements: {stats['disagreements']}")


if __name__ == "__main__":
    main()
