# SPDX-License-Identifier: GPL-3.0-or-later
"""
Orpheus TTS Nodes for ComfyUI
"""

import os
import re

import numpy as np
import torch

# Import custom SNAC and other required libraries
# Note: These would need to be properly installed in the ComfyUI environment
try:
    import inspect
    import json

    import nltk
    from huggingface_hub import hf_hub_download, snapshot_download
    from nltk.tokenize import sent_tokenize
    from snac import SNAC
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Download nltk data if not already present
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install the required dependencies for Orpheus TTS")
    IMPORTS_SUCCESSFUL = False

# Constants for chunking
MAX_CHARS = 220  # Maximum characters per chunk

# List of paralinguistic elements
ELEMENTS = [
    "none",
    "laugh",
    "chuckle",
    "sigh",
    "cough",
    "sniffle",
    "groan",
    "yawn",
    "gasp",
]

# Available voices
VOICES = [
    "tara",
    "leah",
    "jess",
    "leo",
    "dan",
    "mia",
    "zac",
    "zoe",
    "bob",
    "rebeca",
    "lisa",
]

# Element positions
ELEMENT_POSITIONS = ["none", "append", "prepend", "pipe"]


class OrpheusModelLoader:
    """
    ComfyUI Node for loading and initializing Orpheus TTS models
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "snac_model_path": ("STRING", {"default": "hubertsiuzdak/snac_24khz"}),
                "orpheus_model_path": (
                    "STRING",
                    {"default": "canopylabs/orpheus-3b-0.1-ft"},
                ),
            },
        }

    RETURN_TYPES = ("ORPHEUS_MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_models"
    CATEGORY = "audio/tts"

    def load_snac_model(self, snac_model_path, device):
        """
        Load SNAC model with cross-platform compatibility for different SNAC versions
        """
        print("Loading SNAC model...")

        # Create a compatibility wrapper for SNAC models
        class SNACWrapper:
            """Compatibility wrapper for different SNAC model versions"""

            def __init__(self, model, device):
                self.model = model
                self.device = device
                # Check what methods the model has
                self.has_decode = hasattr(model, "decode")
                self.has_decoder = hasattr(model, "decoder")
                print(
                    f"SNAC model structure: has_decode={self.has_decode}, has_decoder={self.has_decoder}"
                )

                # Check for other common methods we might need
                self._inspect_model()

            def _inspect_model(self):
                """Inspect model structure to better understand what we're working with"""
                try:
                    self.model_type = type(self.model).__name__
                    print(f"Model type: {self.model_type}")

                    # Print some useful information about the model structure
                    if hasattr(self.model, "decoder") and hasattr(
                        self.model.decoder, "model"
                    ):
                        print(
                            f"Decoder model structure: {type(self.model.decoder.model).__name__}"
                        )

                    # If we need to access parameters, let's get a reference now
                    self.params = next(self.model.parameters())

                except Exception as e:
                    print(f"Error inspecting model: {e}")

            def decode(self, codes):
                """Universal decode method that works with different model versions"""
                try:
                    # If model has native decode method, use it
                    if self.has_decode:
                        print("Using model's native decode method")
                        return self.model.decode(codes)

                    # If model has decoder attribute, try to use it
                    elif self.has_decoder:
                        print("Using manual decoding through model.decoder")
                        # Try different approaches to decode based on common SNAC architectures

                        # Start with empty result tensor and fill it with zeros
                        batch_size = codes[0].shape[0]

                        # Try different approaches to get sample rate from model
                        sample_rate = 24000  # Default for Orpheus
                        samples_per_second = sample_rate

                        # Create 1 second of silence as fallback
                        result = torch.zeros(
                            (batch_size, samples_per_second), device=self.device
                        )

                        try:
                            # Most common approach - feed codes through the decoder
                            print("Attempting to decode through decoder module")
                            if hasattr(self.model, "codes_to_features"):
                                # Some SNAC models have this helper method
                                features = self.model.codes_to_features(codes)
                                result = self.model.decoder(features)
                            else:
                                # Manual approach - try to feed codes directly to decoder
                                result = self.model.decoder(codes)

                            # If result is a tuple, take the first element (common pattern)
                            if isinstance(result, tuple):
                                result = result[0]

                            print("Decoding succeeded")
                        except Exception as e:
                            print(f"Decoder error: {e}")
                            print("Falling back to silent audio")

                        return result

                    # Emergency fallback - return silent audio
                    else:
                        print(
                            "WARNING: No decoding method available, returning silent audio"
                        )
                        # Generate silent audio based on the code shape
                        batch_size = codes[0].shape[0]
                        return torch.zeros((batch_size, 24000), device=self.device)

                except Exception as e:
                    print(f"Error in decode compatibility layer: {e}")
                    import traceback

                    traceback.print_exc()
                    # Return silent audio as fallback
                    batch_size = codes[0].shape[0] if codes and codes[0].shape else 1
                    return torch.zeros((batch_size, 24000), device=self.device)

            def to(self, device):
                """Move model to device"""
                self.device = device
                self.model = self.model.to(device)
                return self

            def __call__(self, *args, **kwargs):
                """Forward pass through the model"""
                return self.model(*args, **kwargs)

        try:
            # Try to load using standard methods first
            try:
                print("Trying direct from_pretrained loading...")
                snac_model = SNAC.from_pretrained(snac_model_path)
                print("SNAC model loaded successfully using from_pretrained")
                return SNACWrapper(snac_model.to(device), device)
            except Exception as e:
                print(f"Could not load with from_pretrained: {e}")

            # Fallback to default initialization
            print("Falling back to default initialization...")
            snac_model = SNAC()
            print("Created default SNAC model")

            return SNACWrapper(snac_model.to(device), device)

        except Exception as e:
            print(f"All SNAC loading methods failed with error: {e}")
            import traceback

            traceback.print_exc()

            # Create dummy model as last resort
            print("CREATING DUMMY SNAC MODEL that returns silent audio")

            # Create a dummy SNAC model that just returns silent audio
            class DummySNAC:
                def __init__(self):
                    self.device = device

                def decode(self, codes):
                    print("WARNING: Using dummy SNAC model - returning silent audio")
                    # Generate 1 second of silent audio
                    batch_size = (
                        codes[0].shape[0]
                        if codes and len(codes) > 0 and hasattr(codes[0], "shape")
                        else 1
                    )
                    return torch.zeros((batch_size, 24000), device=self.device)

                def to(self, device):
                    self.device = device
                    return self

                def parameters(self):
                    # Return an empty parameter list
                    return [torch.zeros(1, device=self.device)]

            return DummySNAC()

    def load_models(
        self,
        snac_model_path="hubertsiuzdak/snac_24khz",
        orpheus_model_path="canopylabs/orpheus-3b-0.1-ft",
    ):
        if not IMPORTS_SUCCESSFUL:
            raise ImportError(
                "Required libraries are not installed. Please install the required dependencies."
            )

        print("Loading Orpheus TTS models...")

        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        # Load SNAC model with cross-platform compatibility
        snac_model = self.load_snac_model(snac_model_path, device)

        # Download only model config and safetensors if using Hugging Face model
        if not os.path.isdir(orpheus_model_path):
            print(f"Downloading Orpheus model: {orpheus_model_path}")
            snapshot_download(
                repo_id=orpheus_model_path,
                allow_patterns=[
                    "config.json",
                    "*.safetensors",
                    "model.safetensors.index.json",
                ],
                ignore_patterns=[
                    "optimizer.pt",
                    "pytorch_model.bin",
                    "training_args.bin",
                    "scheduler.pt",
                    "tokenizer.json",
                    "tokenizer_config.json",
                    "special_tokens_map.json",
                    "vocab.json",
                    "merges.txt",
                    "tokenizer.*",
                ],
            )

        # Load Orpheus model and tokenizer
        print("Loading Orpheus model and tokenizer...")
        model = AutoModelForCausalLM.from_pretrained(
            orpheus_model_path, torch_dtype=torch.bfloat16
        )
        model.to(device)
        tokenizer = AutoTokenizer.from_pretrained(orpheus_model_path)

        print("Models loaded successfully")

        # Return models and device as a tuple
        return ((snac_model, model, tokenizer, device),)


class OrpheusGenerate:
    """
    ComfyUI Node for generating speech using Orpheus TTS
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("ORPHEUS_MODEL",),
                "text": ("STRING", {"multiline": True}),
                "voice": (VOICES, {"default": "tara"}),
                "element": (ELEMENTS, {"default": "none"}),
                "element_position": (ELEMENT_POSITIONS, {"default": "none"}),
                "temperature": (
                    "FLOAT",
                    {"default": 0.6, "min": 0.1, "max": 1.5, "step": 0.05},
                ),
                "top_p": (
                    "FLOAT",
                    {"default": 0.95, "min": 0.1, "max": 1.0, "step": 0.05},
                ),
                "repetition_penalty": (
                    "FLOAT",
                    {"default": 1.1, "min": 1.0, "max": 2.0, "step": 0.05},
                ),
                "max_new_tokens": (
                    "INT",
                    {"default": 2700, "min": 100, "max": 4000, "step": 100},
                ),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_speech"
    CATEGORY = "audio/tts"

    # Define the audio output structure expected by ComfyUI
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")  # Always process

    def generate_speech(
        self,
        model,
        text,
        voice,
        element,
        element_position,
        temperature,
        top_p,
        repetition_penalty,
        max_new_tokens,
    ):
        """Generate speech from text using Orpheus TTS"""
        if not text.strip():
            return (None,)

        # Unpack the model tuple
        snac_model, orpheus_model, tokenizer, device = model

        # Apply selected element if needed
        if element != "none" and element_position != "none":
            element_tag = f"<{element}>"
            if element_position == "append":
                text = f"{text} {element_tag}"
            elif element_position == "prepend":
                text = f"{element_tag} {text}"
            elif element_position == "pipe":
                # Replace all pipe characters with the selected element
                if "|" in text:
                    text = text.replace("|", element_tag)
                # If no pipes found, we just leave the text as is

        try:
            # Check if the text is long and needs chunking
            if len(text) <= MAX_CHARS:
                # Short text - process normally
                input_ids, attention_mask = self.process_prompt(
                    text, voice, tokenizer, device
                )

                with torch.no_grad():
                    generated_ids = orpheus_model.generate(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        max_new_tokens=max_new_tokens,
                        do_sample=True,
                        temperature=temperature,
                        top_p=top_p,
                        repetition_penalty=repetition_penalty,
                        num_return_sequences=1,
                        eos_token_id=128258,
                    )

                code_list = self.parse_output(generated_ids)
                audio_samples = self.redistribute_codes(code_list, snac_model)

                # Convert to the exact format expected by ComfyUI
                # Format needs to be [batch, channels, samples]
                audio_samples_float = audio_samples.astype(np.float32)
                waveform = torch.tensor(audio_samples_float)

                # Ensure we have a channel dimension
                if waveform.dim() == 1:
                    waveform = waveform.unsqueeze(0)  # [samples] -> [1, samples]

                # Add batch dimension
                waveform = waveform.unsqueeze(
                    0
                )  # [channels, samples] -> [1, channels, samples]

                print(f"Final audio tensor shape: {waveform.shape}, 24000Hz")

                return ({"waveform": waveform, "sample_rate": 24000},)
            else:
                # Long text - needs chunking
                chunks = self.split_into_chunks(text, MAX_CHARS)

                # Create a message for the user
                chunk_message = (
                    f"Processing text in {len(chunks)} chunks for better quality..."
                )
                print(chunk_message)

                all_audio_samples = []
                chunk_count = len(chunks)

                for i, chunk in enumerate(chunks):
                    print(
                        f"Processing chunk {i + 1}/{chunk_count}: {chunk[:30]}{'...' if len(chunk) > 30 else ''}"
                    )

                    # Process this chunk
                    chunk_audio = self.process_audio_chunk(
                        chunk,
                        voice,
                        snac_model,
                        orpheus_model,
                        tokenizer,
                        device,
                        temperature,
                        top_p,
                        repetition_penalty,
                        max_new_tokens,
                    )

                    all_audio_samples.append(chunk_audio)

                combined_audio = self.combine_audio_files(all_audio_samples)

                # Convert to the exact format expected by ComfyUI
                # Format needs to be [batch, channels, samples]
                combined_audio_float = combined_audio.astype(np.float32)
                waveform = torch.tensor(combined_audio_float)

                # Ensure we have a channel dimension
                if waveform.dim() == 1:
                    waveform = waveform.unsqueeze(0)  # [samples] -> [1, samples]

                # Add batch dimension
                waveform = waveform.unsqueeze(
                    0
                )  # [channels, samples] -> [1, channels, samples]

                print(f"Final audio tensor shape: {waveform.shape}, 24000Hz")

                return ({"waveform": waveform, "sample_rate": 24000},)

        except Exception as e:
            print(f"Error generating speech: {e}")
            import traceback

            traceback.print_exc()

            # Return empty audio on failure (1 second of silence at our sample rate)
            dummy_waveform = torch.zeros(1, 1, 24000)  # [batch, channels, samples]
            return ({"waveform": dummy_waveform, "sample_rate": 24000},)

    def process_prompt(self, prompt, voice, tokenizer, device):
        """Process text prompt for the model"""
        prompt = f"{voice}: {prompt}"
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids

        start_token = torch.tensor([[128259]], dtype=torch.int64)  # Start of human
        end_tokens = torch.tensor(
            [[128009, 128260]], dtype=torch.int64
        )  # End of text, End of human

        modified_input_ids = torch.cat(
            [start_token, input_ids, end_tokens], dim=1
        )  # SOH SOT Text EOT EOH

        # No padding needed for single input
        attention_mask = torch.ones_like(modified_input_ids)

        return modified_input_ids.to(device), attention_mask.to(device)

    def parse_output(self, generated_ids):
        """Parse output tokens to audio codes"""
        token_to_find = 128257
        token_to_remove = 128258

        token_indices = (generated_ids == token_to_find).nonzero(as_tuple=True)

        if len(token_indices[1]) > 0:
            last_occurrence_idx = token_indices[1][-1].item()
            cropped_tensor = generated_ids[:, last_occurrence_idx + 1 :]
        else:
            cropped_tensor = generated_ids

        processed_rows = []
        for row in cropped_tensor:
            masked_row = row[row != token_to_remove]
            processed_rows.append(masked_row)

        code_lists = []
        for row in processed_rows:
            row_length = row.size(0)
            new_length = (row_length // 7) * 7
            trimmed_row = row[:new_length]
            trimmed_row = [t - 128266 for t in trimmed_row]
            code_lists.append(trimmed_row)

        return code_lists[0]  # Return just the first one for single sample

    def redistribute_codes(self, code_list, snac_model):
        """Redistribute codes for audio generation"""
        try:
            # Get device safely using a try block
            try:
                device = next(
                    snac_model.parameters()
                ).device  # Get the device of SNAC model
            except:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                print(f"Couldn't determine model device, using: {device}")

            layer_1 = []
            layer_2 = []
            layer_3 = []

            # Safety check for code_list length
            if not code_list or len(code_list) < 7:
                print(
                    f"Warning: code_list is too short: {len(code_list) if code_list else 0} elements"
                )
                # Return silent audio as fallback
                return np.zeros(24000, dtype=np.float32)

            for i in range((len(code_list) + 1) // 7):
                # Add bounds checking to prevent index errors
                if 7 * i < len(code_list):
                    layer_1.append(code_list[7 * i])
                if 7 * i + 1 < len(code_list):
                    layer_2.append(code_list[7 * i + 1] - 4096)
                if 7 * i + 2 < len(code_list):
                    layer_3.append(code_list[7 * i + 2] - (2 * 4096))
                if 7 * i + 3 < len(code_list):
                    layer_3.append(code_list[7 * i + 3] - (3 * 4096))
                if 7 * i + 4 < len(code_list):
                    layer_2.append(code_list[7 * i + 4] - (4 * 4096))
                if 7 * i + 5 < len(code_list):
                    layer_3.append(code_list[7 * i + 5] - (5 * 4096))
                if 7 * i + 6 < len(code_list):
                    layer_3.append(code_list[7 * i + 6] - (6 * 4096))

            # Move tensors to the same device as the SNAC model
            codes = [
                torch.tensor(layer_1, device=device).unsqueeze(0),
                torch.tensor(layer_2, device=device).unsqueeze(0),
                torch.tensor(layer_3, device=device).unsqueeze(0),
            ]

            # Use decode method (will be provided by our wrapper)
            audio_hat = snac_model.decode(codes)

            # Ensure result is properly detached and converted to numpy
            audio_hat_detached = audio_hat.detach()

            # Handle various tensor shapes gracefully
            if audio_hat_detached.dim() > 1:
                audio_hat_squeezed = audio_hat_detached.squeeze()
            else:
                audio_hat_squeezed = audio_hat_detached

            # Convert to CPU numpy array
            return audio_hat_squeezed.cpu().numpy()

        except Exception as e:
            print(f"Error in redistribute_codes: {e}")
            import traceback

            traceback.print_exc()

            # Return silent audio in case of any error
            return np.zeros(24000, dtype=np.float32)

    def split_into_chunks(self, text, max_chars=MAX_CHARS):
        """
        Split text into chunks of reasonable size, trying to break at sentence boundaries.
        Returns a list of text chunks, each smaller than max_chars.
        """
        # Split text into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # If adding this sentence would exceed the limit and we already have content, start a new chunk
            if len(current_chunk) + len(sentence) > max_chars and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            # If the sentence alone is longer than max_chars, we need to split it further
            elif len(sentence) > max_chars:
                # Add current chunk if not empty
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # Split long sentence into smaller parts (at commas, or just by characters if needed)
                parts = re.split(r"(?<=,)\s+", sentence)
                sub_chunk = ""

                for part in parts:
                    if len(sub_chunk) + len(part) > max_chars:
                        if sub_chunk:
                            chunks.append(sub_chunk.strip())
                            sub_chunk = part
                        else:
                            # Even a single part is too long, so just split it arbitrarily
                            for i in range(0, len(part), max_chars):
                                chunks.append(part[i : i + max_chars].strip())
                    else:
                        sub_chunk += " " + part if sub_chunk else part

                # Add any remaining sub-chunk
                if sub_chunk:
                    current_chunk = sub_chunk
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def combine_audio_files(self, audio_data_list):
        """Combine multiple audio arrays into a single audio array."""
        return np.concatenate(audio_data_list)

    def process_audio_chunk(
        self,
        chunk_text,
        voice,
        snac_model,
        orpheus_model,
        tokenizer,
        device,
        temperature,
        top_p,
        repetition_penalty,
        max_new_tokens,
    ):
        """Generate and process audio for a single text chunk"""
        input_ids, attention_mask = self.process_prompt(
            chunk_text, voice, tokenizer, device
        )

        with torch.no_grad():
            generated_ids = orpheus_model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=min(
                    max_new_tokens, 2000
                ),  # Cap at 2000 tokens per chunk
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                num_return_sequences=1,
                eos_token_id=128258,
            )

        code_list = self.parse_output(generated_ids)
        chunk_audio = self.redistribute_codes(code_list, snac_model)

        return chunk_audio


# Register nodes
NODE_CLASS_MAPPINGS = {
    "OrpheusModelLoader": OrpheusModelLoader,
    "OrpheusGenerate": OrpheusGenerate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OrpheusModelLoader": "Orpheus TTS Model Loader",
    "OrpheusGenerate": "Orpheus TTS Generate",
}
