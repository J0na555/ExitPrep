from google.generativeai import configure, GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("Missing GEMINI_API_KEY in your .env file.")

configure(api_key=GEMINI_KEY)

model = GenerativeModel("gemini-1.5-pro")
