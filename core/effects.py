# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure-Python audio effects pipeline using pedalboard. No system binaries."""

from __future__ import annotations

import numpy as np
from pedalboard import (  # type: ignore[import-untyped]
    Delay,
    Gain,
    Pedalboard,
    Reverb,
)
from pedalboard import time_stretch as _time_stretch  # type: ignore[import-untyped]


def apply_effects(
    waveform: np.ndarray,
    sample_rate: int,
    pitch_shift: float = 0.0,
    speed_factor: float = 1.0,
    gain_db: float = 0.0,
    normalize: bool = False,
    add_reverb: bool = False,
    reverb_room_size: float = 0.5,
    reverb_amount: float = 0.3,
    add_echo: bool = False,
    echo_delay: float = 0.5,
    echo_decay: float = 0.5,
) -> np.ndarray:
    """Apply audio effects chain to a 1-D float32 waveform.

    Effect chain order: pitch+speed (time_stretch) → reverb → echo → gain → normalize.
    Returns float32 numpy array; length changes when speed_factor != 1.0.
    """
    audio = waveform.astype(np.float32)

    # pedalboard.time_stretch accepts (channels, samples), returns same shape
    if pitch_shift != 0.0 or speed_factor != 1.0:
        audio_2d = audio[np.newaxis, :]
        audio_2d = _time_stretch(
            audio_2d,
            samplerate=float(sample_rate),
            stretch_factor=float(speed_factor),
            pitch_shift_in_semitones=float(pitch_shift),
        )
        audio = audio_2d[0]

    # Pedalboard plugin chain for remaining effects
    board: list[object] = []

    if add_reverb:
        board.append(
            Reverb(
                room_size=float(reverb_room_size),
                wet_level=float(reverb_amount),
                dry_level=1.0 - float(reverb_amount),
            )
        )

    if add_echo:
        board.append(
            Delay(
                delay_seconds=float(echo_delay),
                feedback=float(echo_decay),
                mix=0.5,
            )
        )

    if gain_db != 0.0:
        board.append(Gain(gain_db=gain_db))

    if board:
        pb = Pedalboard(board)  # type: ignore[arg-type]
        audio_2d = audio[np.newaxis, :]
        audio = pb(audio_2d, sample_rate)[0]

    if normalize:
        peak = np.abs(audio).max()
        if peak > 0.0:
            audio = audio * (0.891 / peak)  # normalize to -1 dBFS

    return audio.astype(np.float32)
