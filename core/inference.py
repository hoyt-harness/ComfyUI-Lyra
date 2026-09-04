# SPDX-License-Identifier: GPL-3.0-or-later
"""Orpheus 3B inference pipeline: prompt formatting, token generation, SNAC decoding."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from core.model import ModelReference

# Orpheus special token IDs
_SOH = 128259       # start-of-human
_EOT = 128009       # end-of-text
_EOH = 128260       # end-of-human
_EOS = 128258       # stop token for generation
_AUDIO_START = 128257  # marks start of audio region in output

# SNAC structure: 7 tokens per frame across 3 codebook layers
_TOKENS_PER_FRAME = 7
_TOKEN_BASE = 128266  # subtract from raw model output tokens to get SNAC codes


def generate_speech_chunk(
    model_ref: ModelReference,
    text: str,
    voice: str = "tara",
    temperature: float = 0.6,
    top_p: float = 0.95,
    repetition_penalty: float = 1.1,
    max_new_tokens: int = 2000,
) -> np.ndarray:
    """Generate audio for a single text chunk. Returns float32 numpy at 24 kHz.

    Handles voice-prefix formatting and special-token wrapping internally.
    """
    import torch  # noqa: PLC0415

    # Build input: SOH + tokenized("{voice}: {text}") + EOT + EOH
    prompted = f"{voice}: {text}"
    input_ids = model_ref.tokenizer(prompted, return_tensors="pt").input_ids

    start = torch.tensor([[_SOH]], dtype=torch.int64)
    end = torch.tensor([[_EOT, _EOH]], dtype=torch.int64)
    input_ids = torch.cat([start, input_ids, end], dim=1).to(model_ref.device)
    attention_mask = torch.ones_like(input_ids)

    with torch.no_grad():
        generated = model_ref.orpheus_model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            num_return_sequences=1,
            eos_token_id=_EOS,
        )

    codes = _parse_output_tokens(generated)
    return _decode_snac(codes, model_ref.snac_model, model_ref.device)


def _parse_output_tokens(generated_ids: object) -> list[int]:
    """Extract raw SNAC code values from model output tensor."""
    # Find last occurrence of _AUDIO_START to locate audio token region
    token_indices = (generated_ids == _AUDIO_START).nonzero(as_tuple=True)  # type: ignore[operator]
    if len(token_indices[1]) > 0:
        start_idx = token_indices[1][-1].item() + 1
        cropped = generated_ids[:, start_idx:]  # type: ignore[index]
    else:
        cropped = generated_ids  # type: ignore[assignment]

    row = cropped[0]
    row = row[row != _EOS]
    # Trim to multiple of 7 (SNAC frame boundary)
    n = (row.size(0) // _TOKENS_PER_FRAME) * _TOKENS_PER_FRAME
    return [t - _TOKEN_BASE for t in row[:n].tolist()]


def _decode_snac(
    code_list: list[int], snac_model: object, device: object
) -> np.ndarray:
    """Redistribute Orpheus 7-token frames into SNAC 3-layer codes and decode."""
    import torch  # noqa: PLC0415

    if len(code_list) < _TOKENS_PER_FRAME:
        return np.zeros(24_000, dtype=np.float32)

    l1: list[int] = []
    l2: list[int] = []
    l3: list[int] = []

    for i in range(len(code_list) // _TOKENS_PER_FRAME):
        b = i * _TOKENS_PER_FRAME
        if b < len(code_list):
            l1.append(code_list[b])
        if b + 1 < len(code_list):
            l2.append(code_list[b + 1] - 4096)
        if b + 2 < len(code_list):
            l3.append(code_list[b + 2] - 2 * 4096)
        if b + 3 < len(code_list):
            l3.append(code_list[b + 3] - 3 * 4096)
        if b + 4 < len(code_list):
            l2.append(code_list[b + 4] - 4 * 4096)
        if b + 5 < len(code_list):
            l3.append(code_list[b + 5] - 5 * 4096)
        if b + 6 < len(code_list):
            l3.append(code_list[b + 6] - 6 * 4096)

    codes = [
        torch.tensor(l1, device=device).unsqueeze(0),
        torch.tensor(l2, device=device).unsqueeze(0),
        torch.tensor(l3, device=device).unsqueeze(0),
    ]

    audio = snac_model.decode(codes).detach()  # type: ignore[union-attr]
    return audio.squeeze().cpu().numpy().astype(np.float32)


def waveform_to_comfy_audio(audio: np.ndarray, sample_rate: int = 24_000) -> dict:
    """Wrap a 1-D float32 numpy array in the ComfyUI AUDIO dict format."""
    import torch  # noqa: PLC0415

    waveform = torch.tensor(audio.astype(np.float32))
    if waveform.dim() == 1:
        waveform = waveform.unsqueeze(0)
    waveform = waveform.unsqueeze(0)  # [1, channels, samples]
    return {"waveform": waveform, "sample_rate": sample_rate}


def comfy_audio_to_numpy(audio_dict: dict) -> np.ndarray:
    """Extract a 1-D float32 numpy array from a ComfyUI AUDIO dict."""
    return audio_dict["waveform"].squeeze().cpu().numpy().astype(np.float32)
