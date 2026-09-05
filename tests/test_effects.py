# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit tests for core.effects — no torch or ComfyUI dependency."""

import numpy as np
import pytest

from core.effects import apply_effects

SAMPLE_RATE = 24_000
DURATION = 0.5  # seconds
N_SAMPLES = int(SAMPLE_RATE * DURATION)


def _sine(freq: float = 440.0, n: int = N_SAMPLES) -> np.ndarray:
    """Generate a 440 Hz sine wave for testing."""
    t = np.linspace(0, n / SAMPLE_RATE, n, endpoint=False)
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


class TestPassthrough:
    def test_defaults_return_same_length(self):
        audio = _sine()
        result = apply_effects(audio, SAMPLE_RATE)
        assert len(result) == len(audio)

    def test_defaults_return_float32(self):
        result = apply_effects(_sine(), SAMPLE_RATE)
        assert result.dtype == np.float32

    def test_defaults_do_not_silence_audio(self):
        audio = _sine()
        result = apply_effects(audio, SAMPLE_RATE)
        assert result.max() > 0.1


class TestSpeedFactor:
    def test_double_speed_halves_length(self):
        audio = _sine(n=N_SAMPLES)
        result = apply_effects(audio, SAMPLE_RATE, speed_factor=2.0)
        assert len(result) == pytest.approx(len(audio) // 2, abs=2)

    def test_half_speed_doubles_length(self):
        audio = _sine(n=N_SAMPLES)
        result = apply_effects(audio, SAMPLE_RATE, speed_factor=0.5)
        assert len(result) == pytest.approx(len(audio) * 2, abs=2)

    def test_speed_one_unchanged(self):
        audio = _sine()
        result = apply_effects(audio, SAMPLE_RATE, speed_factor=1.0)
        assert len(result) == len(audio)


class TestGain:
    def test_positive_gain_increases_amplitude(self):
        audio = _sine() * 0.1
        louder = apply_effects(audio, SAMPLE_RATE, gain_db=20.0)
        assert louder.max() > audio.max()

    def test_negative_gain_decreases_amplitude(self):
        audio = _sine()
        quieter = apply_effects(audio, SAMPLE_RATE, gain_db=-20.0)
        assert quieter.max() < audio.max()


class TestReverb:
    def test_reverb_changes_audio(self):
        audio = _sine()
        result = apply_effects(audio, SAMPLE_RATE, add_reverb=True)
        assert not np.allclose(result[: len(audio)], audio, atol=1e-3)

    def test_reverb_output_is_float32(self):
        result = apply_effects(_sine(), SAMPLE_RATE, add_reverb=True)
        assert result.dtype == np.float32


class TestEcho:
    def test_echo_produces_longer_output_or_same_length(self):
        audio = _sine()
        result = apply_effects(audio, SAMPLE_RATE, add_echo=True, echo_delay=0.1)
        # Echo adds delay taps; length may be same or longer depending on pedalboard
        assert len(result) >= len(audio) * 0.9
