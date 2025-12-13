from __future__ import annotations

import os
import time
from typing import Any

from app.utils.config import settings
from google.generativeai import configure, GenerativeModel, list_models


GEMINI_KEY = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment or settings")

configure(api_key=GEMINI_KEY)

# Cache for the model instance
_model: GenerativeModel | None = None
_model_name: str | None = None


def _get_available_model() -> GenerativeModel:
    """Get an available Gemini model, trying multiple strategies."""
    global _model, _model_name
    
    if _model is not None:
        return _model
    
    # Strategy 1: Use explicitly configured model name
    explicit_model = getattr(settings, "GEMINI_MODEL", None) or os.getenv("GEMINI_MODEL")
    if explicit_model:
        try:
            _model = GenerativeModel(explicit_model)
            _model_name = explicit_model
            return _model
        except Exception:
            pass  # Fall through to other strategies
    
    # Strategy 2: Try to list available models and use the first one that supports generateContent
    try:
        models = list_models()
        for m in models:
            # Check if model supports generateContent
            supports_generate = False
            if hasattr(m, "supported_generation_methods"):
                methods = m.supported_generation_methods
                if isinstance(methods, (list, tuple)):
                    supports_generate = "generateContent" in methods
                elif isinstance(methods, str):
                    supports_generate = "generateContent" in methods
            # Also try if the attribute doesn't exist (some versions might not expose it)
            if not supports_generate and not hasattr(m, "supported_generation_methods"):
                supports_generate = True  # Try anyway
            
            if supports_generate:
                # Extract model name, handling different formats
                model_name = None
                if hasattr(m, "name"):
                    model_name = str(m.name).replace("models/", "")  # Remove models/ prefix if present
                elif hasattr(m, "model_name"):
                    model_name = str(m.model_name)
                elif isinstance(m, str):
                    model_name = m.replace("models/", "")
                
                if model_name:
                    try:
                        _model = GenerativeModel(model_name)
                        _model_name = model_name
                        return _model
                    except Exception:
                        continue
    except Exception:
        pass  # Fall through to fallback models
    
    # Strategy 3: Try common model names in order of preference
    fallback_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
    ]
    
    for model_name in fallback_models:
        try:
            _model = GenerativeModel(model_name)
            _model_name = model_name
            return _model
        except Exception:
            continue
    
    raise RuntimeError(
        "Could not find an available Gemini model. "
        "Please set GEMINI_MODEL environment variable to a valid model name, "
        "or check your API key permissions."
    )


def ask_gemini(prompt: str) -> str:
    """Send a prompt to the Gemini model and return a text response.

    This helper is defensive: different versions of the google.generativeai
    client expose different method names and response shapes. We try a set
    of likely method names and normalize the response to a string.
    """
    model = _get_available_model()
    last_exc: Exception | None = None

    # A small retry loop to handle transient errors like 504 Deadline Exceeded
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        # Try the standard generate_content method first (most common in recent versions)
        try:
            response = model.generate_content(prompt)
            if hasattr(response, "text") and response.text:
                return response.text
            if hasattr(response, "candidates") and response.candidates:
                first = response.candidates[0]
                if hasattr(first, "content") and hasattr(first.content, "parts"):
                    parts = first.content.parts
                    if parts and hasattr(parts[0], "text"):
                        return parts[0].text
        except Exception as exc:
            last_exc = exc
            # For 5xx / Deadline Exceeded-like errors, retry with backoff
            msg = str(exc)
            if (attempt < max_attempts) and (
                "504" in msg
                or "deadline exceeded" in msg.lower()
                or "internal" in msg.lower()
                or "unavailable" in msg.lower()
            ):
                # Exponential backoff: 1s, 2s, 4s
                time.sleep(2 ** (attempt - 1))
                continue
            # Otherwise, fall through to trying other methods

        # Fallback to trying other method names
        for method_name in ("generate", "generate_text", "predict", "respond", "create"):
            fn = getattr(model, method_name, None)
            if not fn:
                continue
            try:
                try:
                    response = fn(prompt=prompt)
                except TypeError:
                    response = fn(prompt)
            except Exception as exc:
                last_exc = exc
                continue

            if hasattr(response, "text") and response.text:
                return response.text

            if hasattr(response, "candidates") and response.candidates:
                first = response.candidates[0]
                for attr in ("output", "content", "text"):
                    if hasattr(first, attr) and getattr(first, attr):
                        return getattr(first, attr)
                return str(first)

            if isinstance(response, dict):
                for key in ("text", "output", "content", "response"):
                    if key in response and response[key]:
                        val = response[key]
                        if isinstance(val, (list, tuple)) and val:
                            return str(val[0])
                        return str(val)

            return str(response)

        # If we got here, and it's a retryable error, sleep and retry
        if last_exc is not None and attempt < max_attempts:
            msg = str(last_exc)
            if (
                "504" in msg
                or "deadline exceeded" in msg.lower()
                or "internal" in msg.lower()
                or "unavailable" in msg.lower()
            ):
                time.sleep(2 ** (attempt - 1))
                continue
            # Non-retryable: break out and raise below
            break

    raise RuntimeError(
        f"Could not call Gemini model '{_model_name}'; last error: {last_exc}. "
        "Try setting GEMINI_MODEL environment variable to a different model name."
    )
