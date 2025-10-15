# app/groq_client.py
import os
import requests
from typing import Optional
from app.config import GROQ_API_KEY

# Default model — change to the model you have access to (example: "llama3-70b-8192")
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-4096")  # pick one available to your account
GROQ_BASE = "https://api.groq.com/openai/v1"  # Chat endpoint base

API_KEY = os.getenv("GROQ_API_KEY", GROQ_API_KEY)
if not API_KEY:
    # Warning: in production, require API key via env var
    print("[warning] GROQ_API_KEY not set. Groq calls will fail without a valid key.")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

def call_groq_llm(prompt: str, model: Optional[str] = None, max_output_tokens: int = 512, temperature: float = 0.0) -> str:
    """
    Call Groq chat completions endpoint using a simple single-user message.
    Returns the assistant's text output (string).

    Replace or expand this to use streaming, tool-calls or Groq SDK if preferred.
    """
    model_name = model or DEFAULT_MODEL
    endpoint = f"{GROQ_BASE}/chat/completions"
    body = {
        "model": model_name,
        # provide the system + user messages for context
        "messages": [
            {"role": "system", "content": "You are an assistant that answers using only provided context."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }

    try:
        resp = requests.post(endpoint, headers=HEADERS, json=body, timeout=60)
    except Exception as e:
        return f"[Groq API error: request failed] {e}"

    if resp.status_code != 200:
        # return helpful error (do not leak full headers/keys)
        return f"[Groq API error] status={resp.status_code}, body={resp.text}"

    data = resp.json()
    # Groq returns a response object; extract text depending on format
    # `choices` or `response` shapes differ; try common keys
    # Try to support both older and newer shapes.
    text = None
    # If `choices` present
    if "choices" in data and isinstance(data["choices"], list) and len(data["choices"]) > 0:
        ch = data["choices"][0]
        # typical OpenAI-like shape: choice["message"]["content"]
        msg = ch.get("message") or ch.get("delta") or {}
        if isinstance(msg, dict):
            text = msg.get("content") or msg.get("text")
        # fallback to choice["text"]
        text = text or ch.get("text")
    # If `response` present (Groq docs sometimes use `response.text` or `response.output`)
    if not text:
        if "response" in data:
            # shape: response -> outputs or text
            resp_obj = data["response"]
            # try text fields
            text = resp_obj.get("output") or resp_obj.get("text")
            if not text and isinstance(resp_obj.get("outputs"), list) and len(resp_obj["outputs"])>0:
                # try first output
                out0 = resp_obj["outputs"][0]
                if isinstance(out0, dict):
                    text = out0.get("text") or out0.get("content")
    if not text:
        # as a last resort, return full json compact
        return "[Groq API] Unexpected response shape: " + str(data)[:2000]

    # if it's nested object choose content field
    if isinstance(text, dict):
        text = text.get("content") or text.get("text") or str(text)

    return text
