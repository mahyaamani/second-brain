"""Interaction tools — ask the user a question and capture their answer."""

# This module is intentionally thin. In text mode it uses input().
# In voice mode, main.py swaps in STT/TTS by monkey-patching ask_user.


def ask_user(question: str) -> str:
    """Print a question and return the user's typed response."""
    print(f"\n[Second Brain asks]: {question}")
    answer = input("Your answer: ").strip()
    return answer if answer else "[no answer provided]"
