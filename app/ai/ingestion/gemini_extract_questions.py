import os
import sys
import json
from pathlib import Path
from string import Template


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

try:
    from app.ai.clients.gemini_client import ask_gemini
except Exception as exc:
    raise ImportError(
        "Failed to import ask_gemini from app.ai.clients.gemini_client. "
        "Run this script from the repository root or ensure the package is importable."
    ) from exc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

TEXT_DIR = os.path.join(DATA_DIR, "past_papers_text")
OUTPUT_DIR = os.path.join(DATA_DIR, "processed_questions")

os.makedirs(OUTPUT_DIR, exist_ok=True)

PROMPT_TEMPLATE = Template("""
You will receive text extracted from an exam past paper.

Convert all multiple‑choice questions into this JSON format:

[
  {
    "course_name": "Course Name",
    "question_text": "...",
    "options": [
      { "text": "...", "is_correct": false },
      { "text": "...", "is_correct": true },
      { "text": "...", "is_correct": false },
      { "text": "...", "is_correct": false }
    ]
  }
]

Rules:
- Use the field name `question_text`, NOT `question`
- Convert choices into an array of objects: `{"text": "...", "is_correct": bool}`
- Mark only the correct answer with `"is_correct": true`
- Only return valid JSON.

Exam text:
---
${exam_text}
---
""")


def extract_questions_from_file(filename):
    filepath = os.path.join(TEXT_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        exam_text = f.read()

    prompt = PROMPT_TEMPLATE.substitute(exam_text=exam_text)
    response = ask_gemini(prompt)

    output_path = os.path.join(OUTPUT_DIR, filename.replace(".txt", ".json"))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response)

    print(f"✓ Extracted questions → {output_path}")

def run():
    for file in os.listdir(TEXT_DIR):
        if file.endswith(".txt"):
            extract_questions_from_file(file)

if __name__ == "__main__":
    run()
