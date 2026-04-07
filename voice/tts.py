"""Text-to-Speech using GCP Cloud Text-to-Speech API."""

import io
import sounddevice as sd
import soundfile as sf
from google.cloud import texttospeech


def speak(text: str) -> None:
    """Convert text to speech and play it through the speakers."""
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Journey-F",  # natural-sounding voice
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    buffer = io.BytesIO(response.audio_content)
    data, samplerate = sf.read(buffer)
    sd.play(data, samplerate)
    sd.wait()
