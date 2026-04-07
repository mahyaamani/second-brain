"""
Second Brain — Main entry point.

Usage:
  python main.py           # text mode
  python main.py --voice   # voice mode (requires GCP credentials)
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

import agent
from tools import interaction


def text_mode():
    """Interactive text-based chat loop."""
    history = []
    print("\n=== Second Brain ===")
    print("Commands: 'quit' to exit")
    print("Try: 'research high protein meal prep' | 'interview me about my fitness goals' | 'what should I eat today?'\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye"):
            print("Goodbye.")
            break

        print()
        response, history = agent.run(user_input, history)
        print(f"\nSecond Brain: {response}\n")


def voice_mode():
    """Voice-based interaction loop using GCP STT + TTS."""
    from voice.stt import listen
    from voice.tts import speak

    # Swap ask_user to use voice
    def voice_ask_user(question: str) -> str:
        speak(question)
        return listen()

    interaction.ask_user = voice_ask_user

    history = []
    speak("Second Brain is ready. How can I help you?")
    print("\n=== Second Brain (Voice Mode) ===")
    print("Say 'goodbye' or press Ctrl+C to exit.\n")

    while True:
        try:
            user_input = listen()
        except KeyboardInterrupt:
            speak("Goodbye!")
            break

        if not user_input:
            speak("I didn't catch that. Could you repeat?")
            continue

        if any(w in user_input.lower() for w in ("goodbye", "bye", "quit", "exit")):
            speak("Goodbye! Your knowledge is saved.")
            break

        print(f"\nProcessing: {user_input}")
        response, history = agent.run(user_input, history)
        print(f"\nSecond Brain: {response}\n")
        speak(response)


if __name__ == "__main__":
    if "--voice" in sys.argv:
        voice_mode()
    else:
        text_mode()
