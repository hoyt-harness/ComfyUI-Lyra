# SPDX-License-Identifier: GPL-3.0-or-later
"""Text chunking and audio concatenation for long-form generation."""

from __future__ import annotations

import re

import numpy as np

MAX_CHARS = 220


def chunk_text(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Split text at sentence boundaries; never truncate content.

    Falls back to comma splits and character splits for sentences that
    individually exceed max_chars.

    Raises:
        ValueError: if text is empty after stripping whitespace.
    """
    if not text.strip():
        raise ValueError("Text must not be empty.")

    try:
        import nltk  # noqa: PLC0415

        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt_tab", quiet=True)
        sentences = nltk.sent_tokenize(text)
    except ImportError:
        sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        elif len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            parts = re.split(r"(?<=,)\s+", sentence)
            sub = ""
            for part in parts:
                if len(sub) + len(part) > max_chars and sub:
                    chunks.append(sub.strip())
                    sub = part
                elif len(part) > max_chars:
                    if sub:
                        chunks.append(sub.strip())
                        sub = ""
                    chunks.extend(
                        part[i : i + max_chars].strip()
                        for i in range(0, len(part), max_chars)
                    )
                else:
                    sub = f"{sub} {part}" if sub else part
            if sub:
                current = sub
        else:
            current = f"{current} {sentence}" if current else sentence

    if current:
        chunks.append(current.strip())

    return [c for c in chunks if c]


def concatenate_audio(waveforms: list[np.ndarray]) -> np.ndarray:
    """Concatenate a list of 1-D float32 audio arrays."""
    if not waveforms:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate([w.astype(np.float32) for w in waveforms])
