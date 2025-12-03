import os
import json

from app.ai.clients.gemini_client import ask_gemini

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "data")

TEXT_DIR = os.path.join(DATA_DIR, "past_papers_text")
OUTPUT_DIR = os.path.join(DATA_DIR, "processed_questions")

os.makedirs(OUTPUT_DIR, exist_ok=True)

PROMPT_TEMPLATE = """
You will receive text extracted from an exam past paper.

Extract all questions in this format:

[
  {
    "question": "...",
    "choices": ["A", "B", "C", "D"],
    "answer": "B"
  }
]

Only return valid JSON.
Exam text:
---
{exam_text}
---
"""

def extract_questions_from_file(filename):
    filepath = os.path.join(TEXT_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        exam_text = f.read()

    prompt = PROMPT_TEMPLATE.format(exam_text=exam_text)
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
