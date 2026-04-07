"""Speech-to-Text using GCP Cloud Speech API."""

import io
import sounddevice as sd
import soundfile as sf
import numpy as np
from google.cloud import speech

SAMPLE_RATE = 16000
DURATION_SECONDS = 7  # max recording length per utterance


def record_audio() -> bytes:
    """Record from the microphone and return raw WAV bytes."""
    print("[Listening... speak now]")
    audio = sd.rec(
        int(DURATION_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    print("[Done recording]")

    buffer = io.BytesIO()
    sf.write(buffer, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
    return buffer.getvalue()


def transcribe(audio_bytes: bytes) -> str:
    """Send audio bytes to GCP and return the transcription."""
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    if not response.results:
        return ""
    return response.results[0].alternatives[0].transcript


def listen() -> str:
    """Record from mic and return transcribed text."""
    audio_bytes = record_audio()
    text = transcribe(audio_bytes)
    print(f"[You said]: {text}")
    return text
