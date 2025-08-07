import os

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "./prompt.txt")

def load_prompt() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

PROMPT_TEXT = load_prompt()