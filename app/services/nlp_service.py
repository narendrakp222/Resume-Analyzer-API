import re
from typing import List, Dict, Set
from collections import Counter
import spacy
from app.core.logger import logger

_nlp_model = None


def get_spacy_model():
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy en_core_web_sm model successfully.")
        except Exception:
            logger.warning("spaCy en_core_web_sm model not found. Attempting to download...")
            try:
                from spacy.cli import download
                download("en_core_web_sm")
                _nlp_model = spacy.load("en_core_web_sm")
                logger.info("Downloaded and loaded spaCy en_core_web_sm model.")
            except Exception as e:
                logger.warning(f"Could not download spaCy model: {str(e)}. Using fallback tokenizer.")
                _nlp_model = False
    return _nlp_model


class NLPService:
    @staticmethod
    def process_text(text: str) -> dict:
        nlp = get_spacy_model()
        tokens = []
        noun_chunks = []
        entities = []

        if nlp:
            doc = nlp(text)
            tokens = [token.text.lower() for token in doc if not token.is_stop and token.is_alpha]
            noun_chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks]
            entities = [(ent.text, ent.label_) for ent in doc.ents]
        else:
            # Fallback regex tokenizer
            words = re.findall(r'\b[a-zA-Z0-9+#.-]+\b', text)
            tokens = [w.lower() for w in words if len(w) > 2]

        return {
            "tokens": tokens,
            "noun_chunks": noun_chunks,
            "entities": entities
        }

    @staticmethod
    def calculate_keyword_frequencies(text: str, target_keywords: Set[str]) -> Dict[str, int]:
        text_lower = text.lower()
        counts = {}
        for keyword in target_keywords:
            # Match exact word boundaries where appropriate
            kw_lower = keyword.lower()
            if len(kw_lower) <= 3:
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
            else:
                pattern = re.escape(kw_lower)
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                counts[keyword] = matches
        return counts
