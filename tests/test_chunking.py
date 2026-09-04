# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit tests for core.chunking — no torch or ComfyUI dependency."""

import numpy as np
import pytest

from core.chunking import MAX_CHARS, chunk_text, concatenate_audio


class TestChunkText:
    def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="empty"):
            chunk_text("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="empty"):
            chunk_text("   ")

    def test_short_text_single_chunk(self):
        text = "Hello, world!"
        result = chunk_text(text)
        assert len(result) == 1
        assert result[0] == text

    def test_two_sentences_one_chunk_when_fits(self):
        text = "Hello. World."
        result = chunk_text(text, max_chars=50)
        assert len(result) == 1

    def test_splits_at_sentence_boundary(self):
        long_a = "A" * 100 + "."
        long_b = "B" * 100 + "."
        result = chunk_text(f"{long_a} {long_b}", max_chars=120)
        assert len(result) == 2
        assert "A" in result[0]
        assert "B" in result[1]

    def test_single_sentence_exceeding_max_splits_by_char(self):
        text = "x" * (MAX_CHARS * 3)
        result = chunk_text(text)
        assert len(result) >= 3
        for chunk in result:
            assert len(chunk) <= MAX_CHARS

    def test_no_content_lost(self):
        sentences = ["This is sentence one.", "This is sentence two.", "Three."]
        text = " ".join(sentences)
        result = chunk_text(text, max_chars=30)
        rejoined = " ".join(result)
        for sentence in sentences:
            for word in sentence.split():
                assert word.strip(".,!?") in rejoined

    def test_pipe_characters_preserved(self):
        text = "Before | After."
        result = chunk_text(text)
        assert "|" in " ".join(result)


class TestConcatenateAudio:
    def test_empty_list_returns_empty_array(self):
        result = concatenate_audio([])
        assert result.shape == (0,)
        assert result.dtype == np.float32

    def test_single_array_returned_correctly(self):
        arr = np.ones(100, dtype=np.float32)
        result = concatenate_audio([arr])
        np.testing.assert_array_equal(result, arr)

    def test_two_arrays_concatenated(self):
        a = np.ones(100, dtype=np.float32)
        b = np.zeros(50, dtype=np.float32)
        result = concatenate_audio([a, b])
        assert result.shape == (150,)
        assert result[:100].sum() == 100.0
        assert result[100:].sum() == 0.0

    def test_coerces_dtype_to_float32(self):
        arr = np.ones(10, dtype=np.float64)
        result = concatenate_audio([arr])
        assert result.dtype == np.float32
