"""
embeddings.py — Sentence Embedding Generator
==============================================
Uses Sentence-BERT (``all-MiniLM-L6-v2``) to convert requirement
sentences into fixed-size 384-dimensional vectors that capture
semantic meaning.

These embeddings are used for:
  • Clustering similar requirements together
  • Computing similarity between any two requirements

How Sentence-BERT works
------------------------
1. Input sentence is tokenised and passed through a transformer encoder.
2. The token embeddings are **mean-pooled** (averaged) to produce a
   single fixed-size vector for the whole sentence.
3. The model was trained with a **siamese network** on sentence pairs
   so that semantically similar sentences have high cosine similarity.

Unlike raw BERT [CLS] embeddings, Sentence-BERT embeddings are
specifically optimised for similarity comparison.

Usage:
    from clustering.embeddings import SentenceEmbedder

    embedder = SentenceEmbedder()
    vectors = embedder.encode(["Users need fast login.", "Login is slow."])
    similarity = embedder.similarity(vectors[0], vectors[1])
"""

import numpy as np

# ---------------------------------------------------------------------------
# We use sentence-transformers library for efficient embedding generation.
# Model: all-MiniLM-L6-v2 (384-dim, fast, good quality)
# ---------------------------------------------------------------------------
from sentence_transformers import SentenceTransformer


# Default model — small, fast, and effective for clustering
MODEL_NAME = "all-MiniLM-L6-v2"


class SentenceEmbedder:
    """
    Generate sentence embeddings using Sentence-BERT.

    Parameters
    ----------
    model_name : str
        HuggingFace sentence-transformers model identifier.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        print(f"[Embedder] Loading Sentence-BERT model: {model_name} …")
        self.model = SentenceTransformer(model_name)
        print("[Embedder] Ready.")

    def encode(self, sentences: list[str]) -> np.ndarray:
        """
        Encode a list of sentences into embedding vectors.

        Parameters
        ----------
        sentences : list[str]
            List of raw text sentences.

        Returns
        -------
        np.ndarray
            Shape: (num_sentences, embedding_dim).  embedding_dim=384
            for all-MiniLM-L6-v2.
        """
        embeddings = self.model.encode(
            sentences,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings

    @staticmethod
    def similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two embedding vectors.

        Returns a float in [-1, 1] where 1 = identical meaning.
        """
        dot = np.dot(vec_a, vec_b)
        norm = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
        if norm == 0:
            return 0.0
        return float(dot / norm)
