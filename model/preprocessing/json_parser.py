import json
import re
from typing import Any

class JSONPreprocessor:
    """
    JSON Preprocessor for AI Requirements Engineering System.
    Handles payloads from Jira, Slack, Email, and generic JSON APIs.
    """

    def __init__(self):
        # Target fields known to contain requirement-like text
        self.target_keys = {"summary", "title", "description", "body", "text", "message", "comments"}
        
        # Regex for cleaning noise
        self.url_pattern = re.compile(r'https?://\S+')
        self.email_pattern = re.compile(r'\S+@\S+\.\S+')
        self.slack_mention_pattern = re.compile(r'<@[A-Z0-9]+>')
        self.markdown_pattern = re.compile(r'[*_~`]')
        
        # We explicitly preserve urgency words and time constraints.
        # This is handled by replacing multiple whitespaces/newlines but ensuring
        # the text remains structurally intact so the downstream NER isn't broken.
        self.whitespace_pattern = re.compile(r'\s+')

    def _clean_text(self, text: str) -> str:
        """
        Normalize text: remove noise (URLs, emails, markdown, tags) while
        preserving critical semantic structure for the NLP pipeline.
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove noisy metadata
        text = self.url_pattern.sub('', text)
        text = self.email_pattern.sub('', text)
        text = self.slack_mention_pattern.sub('', text)
        text = self.markdown_pattern.sub('', text)
        
        # Normalize spacing
        text = self.whitespace_pattern.sub(' ', text)
        
        return text.strip()

    def _extract_text_fields(self, data: Any) -> list[str]:
        """
        Recursively extract target text fields from an arbitrary JSON structure.
        """
        extracted = []

        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in self.target_keys:
                    if isinstance(value, str):
                        extracted.append(value)
                    elif isinstance(value, list) and all(isinstance(v, str) for v in value):
                        extracted.extend(value)
                else:
                    # Recurse into nested dicts/lists
                    extracted.extend(self._extract_text_fields(value))

        elif isinstance(data, list):
            for item in data:
                extracted.extend(self._extract_text_fields(item))

        return extracted

    def parse_to_text(self, json_input: str | dict | list) -> str:
        """
        Main entry point. Parse JSON (string or object) and return clean, flat text.
        """
        try:
            # Handle stringified JSON
            if isinstance(json_input, str):
                data = json.loads(json_input)
            else:
                data = json_input
                
            raw_texts = self._extract_text_fields(data)
            
            # Clean and append punctuation to ensure sentence segmentation works
            clean_texts = []
            for t in raw_texts:
                cleaned = self._clean_text(t)
                if cleaned:
                    if not cleaned.endswith(('.', '!', '?')):
                        cleaned += '.'
                    clean_texts.append(cleaned)
                    
            return " ".join(clean_texts)
            
        except json.JSONDecodeError as e:
            print(f"[JSONPreprocessor] Error parsing JSON string: {e}")
            return ""
        except Exception as e:
            print(f"[JSONPreprocessor] Unexpected error during extraction: {e}")
            return ""
