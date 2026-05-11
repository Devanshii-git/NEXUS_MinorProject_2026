"""
summarizer.py — Improved Abstractive Requirement Summarization
================================================================
Fixed issues:
  • Dynamic max_length based on input length (fixes "max_length too high" warning)
  • Better cluster-level summarization with context
  • Handles short inputs without unnecessary summarization calls

Uses T5-small (default) or BART for abstractive summarization.
"""

from typing import Any

from transformers import pipeline as hf_pipeline


AVAILABLE_MODELS = {
    "bart": "facebook/bart-large-cnn",
    "t5-small": "t5-small",
    "t5-base": "t5-base",
}

DEFAULT_MODEL = "t5-small"


class RequirementSummarizer:
    """
    Summarize clusters of requirement sentences into a single statement.
    Uses dynamic max_length to avoid warnings and improve output quality.
    """

    def __init__(
        self,
        model_key: str = DEFAULT_MODEL,
        max_input_length: int = 512,
    ):
        model_name = AVAILABLE_MODELS.get(model_key, model_key)
        print(f"[Summarizer] Loading model: {model_name} …")

        self.summarizer = hf_pipeline(
            "summarization",
            model=model_name,
            tokenizer=model_name,
        )
        self.max_input_length = max_input_length
        self.model_key = model_key
        print("[Summarizer] Ready.")

    def _compute_dynamic_lengths(self, text: str) -> tuple[int, int]:
        """
        Compute dynamic max/min summary lengths based on input length.

        This fixes the 'max_length is set to X, but input_length is only Y'
        warning by ensuring max_length <= input_length.

        Rules:
          • max_length = min(80, input_token_count)
          • min_length = min(10, max_length - 1)
        """
        # Rough token count estimate (words ≈ tokens for English)
        word_count = len(text.split())

        # Ensure max_length does not exceed input length
        max_length = min(80, max(15, word_count))
        min_length = min(10, max_length - 1)

        return max_length, min_length

    def summarize(self, sentences: list[str]) -> str:
        """
        Summarize a list of related requirement sentences.

        For short/single sentences, returns as-is without model call.
        For longer inputs, uses dynamic length calculation.
        """
        if not sentences:
            return ""

        # For single short sentences, return as-is
        if len(sentences) == 1 and len(sentences[0].split()) <= 20:
            return sentences[0]

        # Concatenate all sentences
        combined = " ".join(sentences)

        # For very short combined text, return as-is
        if len(combined.split()) <= 20:
            return combined

        # Add task prefix for T5 models
        input_text = combined
        if "t5" in self.model_key.lower():
            input_text = "summarize: " + combined

        # Compute dynamic lengths based on actual input
        max_length, min_length = self._compute_dynamic_lengths(combined)

        # Generate summary
        result = self.summarizer(
            input_text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True,
        )

        summary = result[0]["summary_text"].strip()
        return summary

    def summarize_clusters(
        self,
        clusters: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Add a summary to each cluster of requirements."""
        for cluster in clusters:
            sentences = [r["sentence"] for r in cluster["requirements"]]
            cluster["cluster_summary"] = self.summarize(sentences)

        return clusters
