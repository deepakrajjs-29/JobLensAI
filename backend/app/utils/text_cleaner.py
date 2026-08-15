"""Text cleaning and normalization utilities for extracted resume and JD text."""
import re
from typing import Optional


def clean_text(raw_text: Optional[str], max_length: int = 50000) -> str:
    """
    Clean, normalize, and format raw extracted text.
    
    Steps:
    1. Handle None / empty strings.
    2. Normalize line breaks (Windows \\r\\n and old Mac \\r -> \\n).
    3. Normalize various bullet point symbols to standard markdown hyphens.
    4. Collapse excessive horizontal whitespace while preserving indentation / spacing.
    5. Reduce 3+ consecutive newlines to at most 2 newlines (preserves paragraph breaks).
    6. Strip leading and trailing whitespace.
    7. Bound length to max_length to protect downstream memory and token limits.
    """
    if not raw_text:
        return ""

    text = str(raw_text)

    # 1. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Standardize unicode bullet points and fancy dashes to simple markdown bullets
    bullet_pattern = r"^[\t ]*[•●▪◆‣⁃►▶]\s*"
    text = re.sub(bullet_pattern, "- ", text, flags=re.MULTILINE)

    # Also replace inline decorative bullets if preceded by whitespace
    text = re.sub(r"[ \t]+[•●▪◆‣⁃][ \t]+", " - ", text)

    # 3. Normalize non-breaking spaces and tabs to single spaces
    text = text.replace("\xa0", " ").replace("\t", " ")

    # 4. Remove multiple spaces within a line (preserving single space)
    text = re.sub(r"[ ]{2,}", " ", text)

    # 5. Clean trailing/leading spaces on individual lines
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # 6. Collapse 3 or more consecutive blank lines down to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 7. Final trim
    text = text.strip()

    # 8. Length cap enforcement (sensible guardrail)
    if len(text) > max_length:
        text = text[:max_length] + "\n\n[Content truncated due to length]"

    return text


def is_meaningful_text(text: str, min_chars: int = 20) -> bool:
    """
    Check if the text contains a meaningful amount of actual words/letters.
    Prevents image-only PDFs or empty pages from proceeding.
    """
    if not text:
        return False
    
    cleaned = clean_text(text)
    # Count alphanumeric characters
    alnum_count = sum(1 for c in cleaned if c.isalnum())
    return alnum_count >= min_chars
