"""
pipeline.py — Improved End-to-End Requirements Engineering Pipeline
=====================================================================
All 8 phases with improvements:

    Phase 1: Raw Text Input
    Phase 2: Sentence Segmentation
    Phase 3: Requirement Detection       (DistilBERT classifier)
    Phase 4: Named Entity Recognition    (spaCy + BERT NER)
    Phase 4b: Requirement Structuring    (actor-action-constraint)  ★ NEW
    Phase 5: Requirement Clustering      (Sentence-BERT + Agglomerative)  ★ IMPROVED
    Phase 6: Prioritization              (Multi-signal scoring)  ★ IMPROVED
    Phase 7: Summarization               (T5/BART, dynamic length)  ★ FIXED
    Phase 7b: Explainability             (Transparent reasoning)  ★ NEW
    Phase 8: Structured Output           (JSON / Markdown / Console)  ★ IMPROVED
"""

import re
from typing import Any

from requirement_classifier.inference import RequirementClassifier
from ner_model.inference_ner import NERExtractor
from structuring.structurer import RequirementStructurer
from clustering.cluster import RequirementClusterer
from prioritization.prioritizer import RequirementPrioritizer
from prioritization.semantic_corrector import SemanticPriorityCorrector
from prioritization.final_arbiter import FinalPriorityArbiter
from prioritization.llm_auditor import LLMAuditor
from summarization.summarizer import RequirementSummarizer
from explainability.explainer import ExplainabilityEngine
from output_generator.generator import OutputGenerator
from preprocessing.json_parser import JSONPreprocessor


class RequirementsEngineeringPipeline:
    """
    Full pipeline: Raw Text -> Structured, Prioritized, Explained Requirements.
    """

    def __init__(
        self,
        classifier_dir: str = "requirement_classifier/saved_model",
        ner_model_dir: str = "ner_model/output/model-best",
        confidence_threshold: float = 0.5,
        summarizer_model: str = "t5-small",
        cluster_distance: float = 0.65,
        enable_llm_audit: bool = False,
        llm_api_key: str | None = None,
        llm_model: str = "gpt-4o-mini",
    ):
        print("=" * 60)
        print("  Initializing Requirements Engineering Pipeline")
        print("=" * 60)

        print("\n[Phase 3] Loading Requirement Detection model ...")
        self.classifier = RequirementClassifier(classifier_dir)

        print("[Phase 4] Loading NER Extraction model ...")
        self.ner = NERExtractor(ner_model_dir)

        print("[Phase 4b] Initializing Requirement Structurer ...")
        self.structurer = RequirementStructurer()

        print("[Phase 5] Loading Sentence-BERT for clustering ...")
        self.clusterer = RequirementClusterer()

        print("[Phase 6] Initializing multi-signal prioritizer ...")
        self.prioritizer = RequirementPrioritizer()

        print(f"[Phase 7] Loading summarization model ({summarizer_model}) ...")
        self.summarizer = RequirementSummarizer(model_key=summarizer_model)

        print("[Phase 6b] Initializing semantic priority corrector ...")
        self.semantic_corrector = SemanticPriorityCorrector()

        print("[Phase 6c] Initializing final priority arbiter ...")
        self.final_arbiter = FinalPriorityArbiter()

        self._enable_llm_audit = enable_llm_audit
        self._llm_auditor = None
        if enable_llm_audit:
            print("[Phase 6d] Initializing LLM auditor (OpenAI) ...")
            try:
                self._llm_auditor = LLMAuditor(
                    api_key=llm_api_key, model=llm_model
                )
            except (ImportError, ValueError) as exc:
                print(f"  ⚠ LLM auditor disabled: {exc}")
                self._enable_llm_audit = False

        print("[Phase 7b] Initializing explainability engine ...")
        self.explainer = ExplainabilityEngine()

        print("[Phase 8] Initializing output generator ...")
        self.output_generator = OutputGenerator()

        print("[Phase 0] Initializing JSON Preprocessor (Production Ready) ...")
        self.json_preprocessor = JSONPreprocessor()

        self.confidence_threshold = confidence_threshold
        print("\n[OK] Pipeline fully initialized and ready.\n")

    @staticmethod
    def segment_sentences(text: str) -> list[str]:
        """Split raw text into individual sentences."""
        raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in raw_sentences if s.strip()]

    def _detect_and_extract(self, text: str) -> list[dict[str, Any]]:
        """Phases 2-4b: segment -> classify -> NER -> structure."""
        sentences = self.segment_sentences(text)
        requirements = []

        for sentence in sentences:
            classification = self.classifier.predict(sentence)

            if (
                classification["label"] == "Requirement"
                and classification["confidence"] >= self.confidence_threshold
            ):
                entities = self.ner.extract(sentence)
                grouped = self.ner.extract_grouped(sentence)

                req = {
                    "sentence": sentence,
                    "confidence": classification["confidence"],
                    "entities": entities,
                    "grouped": grouped,
                }

                # Phase 4b: Structure into actor-action-constraint
                req = self.structurer.structure(req)

                requirements.append(req)

        return requirements

    def run_json(
        self,
        json_payload: str | dict | list,
        output_json: str = "output/requirements.json",
        output_md: str = "output/requirements.md",
        print_to_console: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Production entry point: Parses unstructured/structured JSON payloads
        from Jira/Slack/Email, flattens them into normalized text, and passes
        them strictly to the NLP pipeline.
        """
        print("-" * 60)
        print("  PROCESSING STRUCTURED JSON PAYLOAD (Jira/Slack/Email)")
        print("-" * 60)
        
        flat_text = self.json_preprocessor.parse_to_text(json_payload)
        
        if not flat_text:
            print("  [ERROR] Parsed JSON yielded no extractable text. Exiting pipeline.")
            return []
            
        return self.run(
            text=flat_text,
            output_json=output_json,
            output_md=output_md,
            print_to_console=print_to_console
        )

    def run(
        self,
        text: str,
        output_json: str = "output/requirements.json",
        output_md: str = "output/requirements.md",
        print_to_console: bool = True,
        enable_llm_audit: bool | None = None,
    ) -> list[dict[str, Any]]:
        """Execute the complete improved pipeline."""

        print("-" * 60)
        print("  RUNNING FULL PIPELINE (IMPROVED)")
        print("-" * 60)

        # --- Phases 2-4b: Detect, Extract, Structure ------------------------
        print("\n> Phases 2-4b: Segmentation -> Classification -> NER -> Structuring ...")
        requirements = self._detect_and_extract(text)
        total_sentences = len(self.segment_sentences(text))
        print(
            f"  Found {len(requirements)} requirements "
            f"out of {total_sentences} sentences."
        )

        if not requirements:
            print("  No requirements detected. Pipeline complete.")
            return []

        # Count functional vs non-functional
        func_count = sum(
            1 for r in requirements
            if r.get("structured", {}).get("requirement_type") == "functional"
        )
        nfr_count = len(requirements) - func_count
        print(f"  Types: {func_count} functional, {nfr_count} non-functional")

        # --- Phase 5: Clustering -------------------------------------------
        print("\n> Phase 5: Clustering similar requirements (Agglomerative) ...")
        clusters = self.clusterer.cluster(requirements)
        sil = clusters[0].get("silhouette_score", -1) if clusters else -1
        print(f"  Formed {len(clusters)} cluster(s).")
        if sil > 0:
            print(f"  Silhouette score: {sil:.4f}")

        # --- Phase 6: Prioritization ----------------------------------------
        print("\n> Phase 6: Multi-signal prioritization ...")
        clusters = self.prioritizer.prioritize_clusters(clusters)
        priority_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for c in clusters:
            priority_counts[c.get("cluster_priority", "LOW")] += 1
        print(
            f"  Priorities: "
            f"{priority_counts['HIGH']} HIGH, "
            f"{priority_counts['MEDIUM']} MEDIUM, "
            f"{priority_counts['LOW']} LOW"
        )

        # --- Phase 6b: Semantic Priority Correction -------------------------
        print("\n> Phase 6b: Semantic priority correction ...")
        clusters = self.semantic_corrector.correct_clusters(clusters)
        override_count = sum(c.get("semantic_overrides", 0) for c in clusters)
        if override_count:
            print(f"  * {override_count} priority override(s) applied by semantic analysis")
        # Recount after correction
        priority_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for c in clusters:
            priority_counts[c.get("cluster_priority", "LOW")] += 1
        print(
            f"  Corrected priorities: "
            f"{priority_counts['HIGH']} HIGH, "
            f"{priority_counts['MEDIUM']} MEDIUM, "
            f"{priority_counts['LOW']} LOW"
        )

        # --- Phase 6c: Final Priority Arbitration ----------------------------
        print("\n> Phase 6c: Final priority arbitration ...")
        clusters = self.final_arbiter.arbitrate_clusters(clusters)
        final_overrides = sum(c.get("final_overrides", 0) for c in clusters)
        if final_overrides:
            print(f"  * {final_overrides} final override(s) by arbitration layer")
        priority_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for c in clusters:
            priority_counts[c.get("cluster_priority", "LOW")] += 1
        print(
            f"  Final priorities: "
            f"{priority_counts['HIGH']} HIGH, "
            f"{priority_counts['MEDIUM']} MEDIUM, "
            f"{priority_counts['LOW']} LOW"
        )

        # --- Phase 6d: LLM Audit (conditional) ------------------------------
        should_audit = (
            enable_llm_audit
            if enable_llm_audit is not None
            else self._enable_llm_audit
        )
        if should_audit and self._llm_auditor:
            print("\n> Phase 6d: LLM priority validation (selective) ...")
            clusters = self._llm_auditor.audit_clusters(clusters)
            stats = self._llm_auditor.stats
            print(
                f"  Audited: {stats['total_audited']}, "
                f"Skipped: {stats['total_skipped']}, "
                f"Agreements: {stats['agreements']}, "
                f"Disagreements: {stats['disagreements']}"
            )
            if stats['disagreements'] > 0:
                print("  [LOG] Disagreements logged to output/llm_audit_log.jsonl")
            self._llm_auditor.reset_stats()

        # --- Phase 7: Summarization ----------------------------------------
        print("\n> Phase 7: Generating cluster summaries (dynamic length) ...")
        clusters = self.summarizer.summarize_clusters(clusters)
        print("  Summaries generated.")

        # --- Phase 7b: Explainability --------------------------------------
        print("\n> Phase 7b: Generating explanations ...")
        clusters = self.explainer.explain_clusters(clusters)
        print("  Explanations generated.")

        # --- Phase 8: Structured Output ------------------------------------
        print("\n> Phase 8: Generating structured output ...")
        self.output_generator.to_json(clusters, output_json)
        self.output_generator.to_markdown(clusters, output_md)

        if print_to_console:
            self.output_generator.to_console(clusters)

        print("\n[OK] Pipeline complete.")
        return clusters
