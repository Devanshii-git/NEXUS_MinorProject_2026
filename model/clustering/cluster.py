"""
cluster.py — Improved Requirement Clustering
==============================================
Groups similar requirement sentences using:
  1. Sentence-BERT embeddings (semantic vectors)
  2. Agglomerative Clustering with cosine distance

Improvements over original
--------------------------
• Switched from DBSCAN (too many single-item clusters) to
  **Agglomerative Clustering** with a tuned distance threshold.
• Uses ``distance_threshold`` instead of fixed cluster count,
  so it auto-determines the number of clusters.
• Added silhouette score evaluation for cluster quality.
• Improved cluster naming from FEATURE + ACTION entities.

Usage:
    from clustering.cluster import RequirementClusterer

    clusterer = RequirementClusterer()
    clusters = clusterer.cluster(requirements_list)
"""

import numpy as np
import umap
import hdbscan
from collections import defaultdict, Counter
from typing import Any
from sklearn.metrics import silhouette_score
from clustering.embeddings import SentenceEmbedder

class RequirementClusterer:
    """
    Cluster requirement sentences by semantic similarity using UMAP + HDBSCAN.
    """

    def __init__(
        self,
        embedder: SentenceEmbedder | None = None,
    ):
        self.embedder = embedder or SentenceEmbedder()

    def cluster(
        self,
        requirements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Cluster a list of requirement dicts.
        """
        if not requirements:
            return []

        # --- Step 1: Compute embeddings -------------------------------------
        sentences = [r["sentence"] for r in requirements]
        embeddings = self.embedder.encode(sentences)

        # Handle edge case: too few sentences for clustering
        if len(sentences) <= 2:
            return [{
                "cluster_id": 0,
                "cluster_name": self._generate_cluster_name(requirements, 0),
                "requirements": requirements,
            }]

        # --- Step 2: UMAP Dimensionality Reduction --------------------------
        # Ensure n_neighbors doesn't exceed dataset size
        n_neighbors = min(12, len(sentences) - 1)
        if n_neighbors < 2:
            n_neighbors = 2
            
        n_components = min(5, max(2, len(sentences) - 2))
        reducer = umap.UMAP(
            n_neighbors=n_neighbors,
            min_dist=0.05,
            n_components=n_components,
            metric='cosine',
            random_state=42
        )
        reduced_embeddings = reducer.fit_transform(embeddings)

        # --- Step 3: HDBSCAN Clustering -------------------------------------
        # Ensure min_cluster_size is appropriate for small datasets
        min_cluster_size = min(4, len(sentences))
        if min_cluster_size < 2:
            min_cluster_size = 2
            
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        labels = clusterer.fit_predict(reduced_embeddings)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

        # --- Step 4: Compute silhouette score (cluster quality) -------------
        sil_score = -1.0
        # For silhouette, ignore noise points (-1)
        mask = labels != -1
        if np.sum(mask) > min_cluster_size and n_clusters > 1:
            try:
                sil_score = silhouette_score(reduced_embeddings[mask], labels[mask])
            except Exception:
                pass

        # --- Step 5: Group requirements by cluster --------------------------
        cluster_map: dict[int, list[dict[str, Any]]] = defaultdict(list)
        noise_counter = max(labels) + 1 if len(labels) > 0 else 1
        
        for idx, label in enumerate(labels):
            if label == -1:
                # Map noise to singleton clusters
                cluster_map[noise_counter].append(requirements[idx])
                noise_counter += 1
            else:
                cluster_map[label].append(requirements[idx])

        # --- Step 6: Build output -------------------------------------------
        clusters = []
        for cluster_id, reqs in sorted(cluster_map.items()):
            cluster_name = self._generate_cluster_name(reqs, cluster_id)
            clusters.append({
                "cluster_id": cluster_id,
                "cluster_name": cluster_name,
                "requirements": reqs,
                "silhouette_score": round(sil_score, 4) if len(reqs) > 1 else 0.0,
            })

        return clusters

    @staticmethod
    def _generate_cluster_name(
        requirements: list[dict[str, Any]],
        cluster_id: int,
    ) -> str:
        """
        Auto-generate a professional cluster name from extracted entities.
        """
        feature_counts: Counter = Counter()
        action_counts: Counter = Counter()
        quality_counts: Counter = Counter()

        for req in requirements:
            grouped = req.get("grouped", {})
            for feature in grouped.get("FEATURE", []):
                feature_counts[feature.lower()] += 1
            for action in grouped.get("ACTION", []):
                action_counts[action.lower()] += 1
            for quality in grouped.get("QUALITY_ATTRIBUTE", []):
                quality_counts[quality.lower()] += 1
            for constraint in grouped.get("CONSTRAINT", []):
                if "offline" in constraint.lower():
                    quality_counts["offline support"] += 1

        parts = []
        
        # 1. Start with the core feature
        if feature_counts:
            top_feature = feature_counts.most_common(1)[0][0]
            parts.append(top_feature.title())
            
        # 2. Add modifying quality/context
        if quality_counts:
            top_quality = quality_counts.most_common(1)[0][0]
            parts.append(top_quality.title())

        # 3. Prepend specific action (avoiding generic verbs)
        if action_counts and feature_counts and not quality_counts:
            top_action = action_counts.most_common(1)[0][0]
            if top_action.lower() not in {"work", "use", "do", "make", "be"}:
                parts.insert(0, top_action.title())

        if parts:
            return " ".join(parts).replace("  ", " ").strip()
        
        return f"Cluster {cluster_id + 1}"
