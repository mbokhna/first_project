import json
import os
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, ValidationError

# Free-tier model on OpenRouter (no billing/credits required).
# Note: openai/gpt-oss-120b:free was retired by OpenRouter (only the paid
# openai/gpt-oss-120b remains); openai/gpt-oss-20b:free is the free sibling.
DEFAULT_MODEL = "openai/gpt-oss-20b:free"

CHAT_SYSTEM_PROMPT = """You are an assistant embedded in a Kanban board app. \
You are given the current board as JSON and a conversation with the user.

Respond with ONLY a single JSON object, no markdown fences, no commentary \
outside the JSON, of the form:
{"reply": "<short natural-language reply to the user>", "actions": [<zero or more actions>]}

Each action in "actions" is one of these shapes:
{"type": "add_card", "column_id": "<column id>", "title": "<title>", "details": "<details, optional>"}
{"type": "update_card", "card_id": "<card id>", "title": "<optional new title>", "details": "<optional new details>"}
{"type": "delete_card", "card_id": "<card id>"}
{"type": "move_card", "card_id": "<card id>", "column_id": "<target column id>", "index": <0-based position in the target column>}
{"type": "rename_column", "column_id": "<column id>", "title": "<new title>"}

Rules:
- Only include actions the user actually asked for. If the user just asked a \
question or made small talk, "actions" must be an empty list.
- Only ever use column ids and card ids that literally appear in the board \
JSON below. Never invent ids.
- You may include multiple actions in one reply if the user asked for \
multiple changes.
- Keep "reply" short and conversational.
"""


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


class BoardAction(BaseModel):
    type: str
    column_id: str | None = None
    card_id: str | None = None
    title: str | None = None
    details: str | None = None
    index: int | None = None


class ChatReply(BaseModel):
    reply: str
    actions: list[BoardAction] = []


def chat(
    board: dict[str, Any], history: list[dict[str, str]], message: str
) -> ChatReply:
    client = get_client()
    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)

    messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        {"role": "system", "content": f"Current board JSON:\n{json.dumps(board)}"},
        *history,
        {"role": "user", "content": message},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"

    try:
        return ChatReply.model_validate_json(content)
    except ValidationError:
        return ChatReply(reply=content, actions=[])
