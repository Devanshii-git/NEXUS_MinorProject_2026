"""
run_all_evaluations.py — Consolidated Evaluation Suite
========================================================
Runs evaluation for all pipeline components:

  1. Requirement Detection (Accuracy, Precision, Recall, F1)
  2. NER (Entity-level P/R/F1 per type)
  3. Clustering (Silhouette score)
  4. Prioritization (Priority distribution analysis)

Usage:
    python -m evaluation.run_all_evaluations
"""

import sys


def evaluate_classifier():
    """Evaluate the requirement detection classifier."""
    print("=" * 60)
    print("  EVALUATION: Requirement Detection (DistilBERT)")
    print("=" * 60)
    try:
        from requirement_classifier.evaluate import evaluate
        metrics = evaluate(
            model_dir="requirement_classifier/saved_model",
            test_csv="data/requirement_classification/test.csv",
        )
        return metrics
    except Exception as e:
        print(f"  ✗ Classifier evaluation failed: {e}")
        return None


def evaluate_ner():
    """Evaluate the NER model."""
    print()
    print("=" * 60)
    print("  EVALUATION: Named Entity Recognition (spaCy + BERT)")
    print("=" * 60)
    try:
        from ner_model.evaluate_ner import evaluate_ner as eval_ner
        metrics = eval_ner(
            model_dir="ner_model/output/model-best",
            test_data="data/ner/dev.spacy",
        )
        return metrics
    except Exception as e:
        print(f"  ✗ NER evaluation failed: {e}")
        return None


def evaluate_clustering():
    """Evaluate clustering quality using silhouette score."""
    print()
    print("=" * 60)
    print("  EVALUATION: Clustering Quality")
    print("=" * 60)
    try:
        import numpy as np
        from sklearn.metrics import silhouette_score
        from clustering.embeddings import SentenceEmbedder
        from sklearn.cluster import AgglomerativeClustering
        from sklearn.metrics.pairwise import cosine_distances

        # Test sentences for clustering evaluation
        test_sentences = [
            "Users need faster login.",
            "Login is too slow during peak hours.",
            "Improve login speed.",
            "The payment must process within 2 seconds.",
            "Payment gateway needs to be faster.",
            "Dashboard must load quickly.",
            "Export reports as PDF.",
            "Users should download files.",
            "The system must encrypt passwords.",
            "Security should be improved.",
        ]

        embedder = SentenceEmbedder()
        embeddings = embedder.encode(test_sentences)
        dist_matrix = cosine_distances(embeddings)

        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.65,
            metric="precomputed",
            linkage="average",
        )
        labels = clustering.fit_predict(dist_matrix)

        n_clusters = len(set(labels))
        sil = silhouette_score(dist_matrix, labels, metric="precomputed")

        print(f"  Sentences       : {len(test_sentences)}")
        print(f"  Clusters formed : {n_clusters}")
        print(f"  Silhouette score: {sil:.4f}")
        print(f"  Quality         : {'Good' if sil > 0.5 else 'Moderate' if sil > 0.25 else 'Weak'}")
        print()

        # Show cluster assignments
        from collections import defaultdict
        cluster_map = defaultdict(list)
        for idx, label in enumerate(labels):
            cluster_map[label].append(test_sentences[idx])

        for cid, sents in sorted(cluster_map.items()):
            print(f"  Cluster {cid}:")
            for s in sents:
                print(f"    • {s}")

        return {"silhouette": sil, "n_clusters": n_clusters}
    except Exception as e:
        print(f"  ✗ Clustering evaluation failed: {e}")
        return None


def evaluate_prioritization():
    """Evaluate prioritization distribution."""
    print()
    print("=" * 60)
    print("  EVALUATION: Prioritization Distribution")
    print("=" * 60)
    try:
        from prioritization.prioritizer import RequirementPrioritizer

        test_requirements = [
            {"sentence": "Users must login within 2 seconds.", "grouped": {"ACTOR": ["Users"], "ACTION": ["login"], "CONSTRAINT": ["within 2 seconds"]}},
            {"sentence": "It is critical to fix the payment bug.", "grouped": {"PRIORITY_INDICATOR": ["critical"], "ACTION": ["fix"], "FEATURE": ["payment"]}},
            {"sentence": "Admin should configure settings.", "grouped": {"ACTOR": ["Admin"], "ACTION": ["configure"], "FEATURE": ["settings"]}},
            {"sentence": "Urgent: security vulnerability found.", "grouped": {"PRIORITY_INDICATOR": ["Urgent"], "QUALITY_ATTRIBUTE": ["security"]}},
            {"sentence": "Users can export reports.", "grouped": {"ACTOR": ["Users"], "ACTION": ["export"], "FEATURE": ["reports"]}},
            {"sentence": "The system must handle 10000 users.", "grouped": {"CONSTRAINT": ["10000 users"], "QUALITY_ATTRIBUTE": ["scalability"]}},
            {"sentence": "Login timeout causes data loss.", "grouped": {"FEATURE": ["Login"], "QUALITY_ATTRIBUTE": ["timeout"]}},
            {"sentence": "Dashboard needs improvement.", "grouped": {"FEATURE": ["Dashboard"]}},
        ]

        prioritizer = RequirementPrioritizer()
        results = prioritizer.prioritize_all(test_requirements)

        counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for r in results:
            counts[r["priority"]] += 1
            print(f"  {r['priority']:6s} (score {r['priority_score']:4.1f}): {r['sentence']}")
            for reason in r.get("priority_reasons", []):
                print(f"         → {reason}")

        print()
        print(f"  Distribution: HIGH={counts['HIGH']}, MEDIUM={counts['MEDIUM']}, LOW={counts['LOW']}")

        return counts
    except Exception as e:
        print(f"  ✗ Prioritization evaluation failed: {e}")
        return None


def main():
    """Run all evaluations."""
    print()
    print("*" * 60)
    print("*  CONSOLIDATED EVALUATION SUITE")
    print("*" * 60)

    classifier_metrics = evaluate_classifier()
    ner_metrics = evaluate_ner()
    cluster_metrics = evaluate_clustering()
    priority_metrics = evaluate_prioritization()

    # Summary
    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    if classifier_metrics:
        print(f"  Classifier F1   : {classifier_metrics.get('f1', 'N/A')}")
    else:
        print("  Classifier      : Not evaluated (model not trained yet)")
    if ner_metrics:
        print(f"  NER Entity F1   : {ner_metrics.get('ents_f', 'N/A')}")
    else:
        print("  NER             : Not evaluated (model not trained yet)")
    if cluster_metrics:
        print(f"  Clustering sil. : {cluster_metrics['silhouette']:.4f}")
    if priority_metrics:
        print(f"  Priority dist.  : H={priority_metrics['HIGH']} M={priority_metrics['MEDIUM']} L={priority_metrics['LOW']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
