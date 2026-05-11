"""
llm_auditor.py — LLM-Based Priority Validation Layer (Phase 6d)
================================================================
A **secondary** validation / auditing layer that runs AFTER the
deterministic rule-based ``FinalPriorityArbiter`` (Phase 6c).

Purpose:
    • Validate edge cases where rules might miss implicit meaning.
    • Generate human-readable reasoning for comparison.
    • Log disagreements between rule-based and LLM decisions.
    • Benchmark and continuously improve the rule-based system.

Key design principles:
    1. The rule-based arbiter's decision is ALWAYS final.
       The LLM **never** overrides it — only audits.
    2. Conditional execution to keep latency and cost low:
       - ``enable_llm_audit=True`` (manual / debug mode)
       - Arbiter confidence < ``confidence_threshold`` (edge cases)
       - Final priority is ``HIGH`` (critical decisions)
    3. Provider-agnostic interface — easily swap OpenAI for
       Gemini, Ollama, or any other LLM backend.

Output per requirement (attached as ``llm_audit`` key):
    {
        "llm_priority": "HIGH",
        "llm_confidence": 0.92,
        "llm_is_valid_requirement": true,
        "llm_reason": ["authentication is core", "urgency implied"],
        "agrees_with_arbiter": true,
        "disagreement_details": null,
        "provider": "openai",
        "skipped": false
    }

Usage:
    from prioritization.llm_auditor import LLMAuditor
    auditor = LLMAuditor(api_key="sk-...")
    clusters = auditor.audit_clusters(clusters)
"""

import json
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any


# ───────────────────────────────────────────────────────────────────────
# Prompt Template
# ───────────────────────────────────────────────────────────────────────

AUDIT_PROMPT_TEMPLATE = """\
You are the FINAL intelligence layer in an AI-based Requirements Engineering system.

The input has been extracted from real-world sources such as Jira issues, comments, \
Slack messages, or emails. The text may be incomplete, noisy, or loosely structured.

The system has already performed:
* NLP extraction (classification, NER, structuring)
* Initial prioritization
* Semantic correction
* Rule-based final arbitration

Your role is to independently validate the final priority decision.

---

INPUT PROVIDED:

* Raw Combined Text (summary + description + comments)
* Structured Data
* Initial Priority
* Semantic Correction Output
* Final Arbitration Output

---

YOUR TASK:

1. Understand Context Holistically
   The text may come from multiple sources merged together. Interpret it as a single \
requirement context.

2. Handle Noisy or Incomplete Input
   If the text is vague (e.g., "we don't need it"), treat it as low-value or \
non-requirement unless strong signals exist.

3. Semantic Reasoning
   Infer urgency, importance, or impact from meaning — not just keywords.

4. Business Criticality
   Authentication, login, payments, infrastructure, APIs → HIGH importance.

5. Requirement Validity Check
   If the text does NOT describe a requirement → mark LOW and explain.

6. Consistency Check
   Ensure priority aligns with reasoning and system signals.

---

STRICT DECISION RULES:

* Core feature + strong intent → HIGH
* Urgent or blocking issue → HIGH
* Vague or non-requirement text → LOW
* Cosmetic/UI change → LOW
* Only override if clearly necessary

---

OUTPUT FORMAT (respond with ONLY valid JSON, no markdown):

{{
  "final_priority": "HIGH | MEDIUM | LOW",
  "confidence": 0 to 1,
  "override": true or false,
  "is_valid_requirement": true or false,
  "reason": [
    "context-based reasoning",
    "explanation of decision"
  ]
}}

---

Now process:

Text: "{text}"
Structured Data: {structured_data}
Initial Priority: {initial_priority}
Semantic Correction: {semantic_output}
Final Arbitration: {arbitration_output}
"""


# ───────────────────────────────────────────────────────────────────────
# Abstract LLM Provider Interface
# ───────────────────────────────────────────────────────────────────────

class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    Implement this to add support for Gemini, Ollama, Anthropic, etc.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send a prompt and return the raw text response."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name for logging."""


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider (default)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: int = 512,
    ):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Run: pip install openai"
            )

        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "OpenAI API key required. Pass api_key= or set "
                "OPENAI_API_KEY environment variable."
            )

        self._client = OpenAI(api_key=self._api_key)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert requirements engineering analyst. "
                        "Respond only with valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return response.choices[0].message.content.strip()

    @property
    def provider_name(self) -> str:
        return f"openai/{self._model}"


# ───────────────────────────────────────────────────────────────────────
# Main Auditor
# ───────────────────────────────────────────────────────────────────────

class LLMAuditor:
    """
    LLM-based validation layer for priority decisions.

    Runs conditionally (not on every requirement) and NEVER overrides
    the rule-based arbiter. Attaches audit results and tracks
    disagreements for continuous system improvement.

    Parameters
    ----------
    provider : LLMProvider, optional
        LLM backend to use. Defaults to OpenAI.
    api_key : str, optional
        API key (shortcut for OpenAI provider).
    model : str
        Model name for the default OpenAI provider.
    confidence_threshold : float
        Audit requirements where arbiter confidence is below this.
    audit_high_priority : bool
        Whether to always audit HIGH-priority decisions.
    log_file : str, optional
        Path to write disagreement logs. None disables logging.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        confidence_threshold: float = 0.80,
        audit_high_priority: bool = True,
        log_file: str | None = "output/llm_audit_log.jsonl",
    ):
        if provider is not None:
            self._provider = provider
        else:
            self._provider = OpenAIProvider(api_key=api_key, model=model)

        self._confidence_threshold = confidence_threshold
        self._audit_high_priority = audit_high_priority
        self._log_file = log_file

        # Session statistics
        self._stats = {
            "total_audited": 0,
            "total_skipped": 0,
            "agreements": 0,
            "disagreements": 0,
            "errors": 0,
        }

    # ── Public API ─────────────────────────────────────────────────────

    def audit(
        self,
        requirement: dict[str, Any],
        force: bool = False,
    ) -> dict[str, Any]:
        """
        Audit a single requirement's priority decision.

        Parameters
        ----------
        requirement : dict
            Enriched requirement dict (must have ``final_arbitration``).
        force : bool
            If True, audit regardless of conditional triggers.

        Returns
        -------
        dict
            Requirement enriched with ``llm_audit`` key.
        """
        arbitration = requirement.get("final_arbitration", {})

        # Check if this requirement should be audited
        if not force and not self._should_audit(requirement):
            requirement["llm_audit"] = self._skip_result()
            self._stats["total_skipped"] += 1
            return requirement

        # Build the prompt with full context
        prompt = self._build_prompt(requirement)

        # Call the LLM
        try:
            raw_response = self._provider.generate(prompt)
            llm_result = self._parse_response(raw_response)
        except Exception as exc:
            requirement["llm_audit"] = self._error_result(str(exc))
            self._stats["errors"] += 1
            return requirement

        # Compare with arbiter decision
        arbiter_priority = arbitration.get("final_priority", "LOW")
        llm_priority = llm_result.get("final_priority", "LOW")
        agrees = llm_priority == arbiter_priority

        audit_output = {
            "llm_priority": llm_priority,
            "llm_confidence": llm_result.get("confidence", 0.0),
            "llm_is_valid_requirement": llm_result.get(
                "is_valid_requirement", True
            ),
            "llm_reason": llm_result.get("reason", []),
            "agrees_with_arbiter": agrees,
            "disagreement_details": None,
            "provider": self._provider.provider_name,
            "skipped": False,
        }

        if not agrees:
            audit_output["disagreement_details"] = {
                "arbiter_said": arbiter_priority,
                "llm_said": llm_priority,
                "arbiter_reasons": arbitration.get("reason", []),
                "llm_reasons": llm_result.get("reason", []),
            }
            self._stats["disagreements"] += 1
            self._log_disagreement(requirement, audit_output)
        else:
            self._stats["agreements"] += 1

        self._stats["total_audited"] += 1
        requirement["llm_audit"] = audit_output

        # NOTE: We do NOT override the arbiter's decision.
        # requirement["priority"] stays unchanged.

        return requirement

    def audit_all(
        self,
        requirements: list[dict[str, Any]],
        force: bool = False,
    ) -> list[dict[str, Any]]:
        """Audit a list of requirements."""
        return [self.audit(r, force=force) for r in requirements]

    def audit_clusters(
        self,
        clusters: list[dict[str, Any]],
        force: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Audit requirements within each cluster.

        Attaches ``llm_audit_stats`` to each cluster with
        audit/skip/agreement/disagreement counts.
        """
        for cluster in clusters:
            reqs = cluster.get("requirements", [])
            cluster["requirements"] = self.audit_all(reqs, force=force)

            # Per-cluster stats
            audited = sum(
                1 for r in reqs
                if not r.get("llm_audit", {}).get("skipped", True)
            )
            disagreements = sum(
                1 for r in reqs
                if r.get("llm_audit", {}).get("disagreement_details")
                is not None
            )
            cluster["llm_audit_stats"] = {
                "audited": audited,
                "skipped": len(reqs) - audited,
                "disagreements": disagreements,
            }

        return clusters

    @property
    def stats(self) -> dict[str, int]:
        """Return session-level audit statistics."""
        return dict(self._stats)

    def reset_stats(self) -> None:
        """Reset session statistics."""
        for key in self._stats:
            self._stats[key] = 0

    # ── Conditional Trigger Logic ──────────────────────────────────────

    def _should_audit(self, requirement: dict[str, Any]) -> bool:
        """
        Determine if a requirement should be audited based on
        the conditional strategy.

        Triggers:
            1. Arbiter confidence < threshold (edge cases)
            2. Final priority is HIGH (critical decisions)
        """
        arbitration = requirement.get("final_arbitration", {})
        confidence = arbitration.get("confidence", 1.0)
        priority = arbitration.get("final_priority", "LOW")

        # Trigger 1: Low-confidence edge case
        if confidence < self._confidence_threshold:
            return True

        # Trigger 2: HIGH-priority critical decision
        if self._audit_high_priority and priority == "HIGH":
            return True

        return False

    # ── Prompt Construction ────────────────────────────────────────────

    @staticmethod
    def _build_prompt(requirement: dict[str, Any]) -> str:
        """Construct the full audit prompt from requirement context."""
        sentence = requirement.get("sentence", "")
        structured = requirement.get("structured", {})
        initial_priority = requirement.get("priority_score", "N/A")
        semantic = requirement.get("semantic_correction", {})
        arbitration = requirement.get("final_arbitration", {})

        # Safely serialize dicts for the prompt
        def safe_json(obj: Any) -> str:
            try:
                return json.dumps(obj, indent=2, default=str)
            except (TypeError, ValueError):
                return str(obj)

        return AUDIT_PROMPT_TEMPLATE.format(
            text=sentence,
            structured_data=safe_json(structured),
            initial_priority=initial_priority,
            semantic_output=safe_json(semantic),
            arbitration_output=safe_json(arbitration),
        )

    # ── Response Parsing ───────────────────────────────────────────────

    @staticmethod
    def _parse_response(raw: str) -> dict[str, Any]:
        """
        Parse the LLM response into a structured dict.
        Handles markdown-wrapped JSON and malformed responses.
        """
        # Strip markdown code fences if present
        cleaned = re.sub(r"```json\s*", "", raw)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            # Attempt to find JSON object in the response
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if match:
                try:
                    result = json.loads(match.group())
                except json.JSONDecodeError:
                    result = {
                        "final_priority": "LOW",
                        "confidence": 0.0,
                        "override": False,
                        "is_valid_requirement": True,
                        "reason": [
                            f"LLM response could not be parsed: {raw[:200]}"
                        ],
                    }
            else:
                result = {
                    "final_priority": "LOW",
                    "confidence": 0.0,
                    "override": False,
                    "is_valid_requirement": True,
                    "reason": [
                        f"LLM returned non-JSON response: {raw[:200]}"
                    ],
                }

        # Normalize priority value
        priority = str(result.get("final_priority", "LOW")).upper().strip()
        if priority not in {"HIGH", "MEDIUM", "LOW"}:
            priority = "LOW"
        result["final_priority"] = priority

        # Ensure confidence is a float in [0, 1]
        try:
            conf = float(result.get("confidence", 0.0))
            result["confidence"] = max(0.0, min(1.0, conf))
        except (TypeError, ValueError):
            result["confidence"] = 0.0

        # Ensure reason is a list
        reason = result.get("reason", [])
        if isinstance(reason, str):
            result["reason"] = [reason]

        return result

    # ── Disagreement Logging ───────────────────────────────────────────

    def _log_disagreement(
        self,
        requirement: dict[str, Any],
        audit_output: dict[str, Any],
    ) -> None:
        """Append disagreement to the JSONL log file."""
        if not self._log_file:
            return

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "text": requirement.get("sentence", "")[:300],
            "arbiter_priority": audit_output["disagreement_details"][
                "arbiter_said"
            ],
            "llm_priority": audit_output["llm_priority"],
            "arbiter_confidence": requirement.get(
                "final_arbitration", {}
            ).get("confidence", 0.0),
            "llm_confidence": audit_output["llm_confidence"],
            "arbiter_reasons": audit_output["disagreement_details"][
                "arbiter_reasons"
            ],
            "llm_reasons": audit_output["llm_reason"],
            "provider": audit_output["provider"],
        }

        try:
            os.makedirs(os.path.dirname(self._log_file), exist_ok=True)
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except OSError:
            pass  # Silent fail — logging should not break the pipeline

    # ── Result Templates ───────────────────────────────────────────────

    @staticmethod
    def _skip_result() -> dict[str, Any]:
        """Result template for skipped (not audited) requirements."""
        return {
            "llm_priority": None,
            "llm_confidence": None,
            "llm_is_valid_requirement": None,
            "llm_reason": [],
            "agrees_with_arbiter": None,
            "disagreement_details": None,
            "provider": None,
            "skipped": True,
        }

    @staticmethod
    def _error_result(error_msg: str) -> dict[str, Any]:
        """Result template for LLM call failures."""
        return {
            "llm_priority": None,
            "llm_confidence": None,
            "llm_is_valid_requirement": None,
            "llm_reason": [f"LLM audit error: {error_msg}"],
            "agrees_with_arbiter": None,
            "disagreement_details": None,
            "provider": None,
            "skipped": False,
            "error": True,
        }
