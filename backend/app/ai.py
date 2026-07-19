import os

from openai import OpenAI

# Free-tier model on OpenRouter (no billing/credits required).
# Note: openai/gpt-oss-120b:free was retired by OpenRouter (only the paid
# openai/gpt-oss-120b remains); openai/gpt-oss-20b:free is the free sibling.
DEFAULT_MODEL = "openai/gpt-oss-20b:free"


def get_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


def ask(prompt: str) -> str:
    client = get_client()
    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""
