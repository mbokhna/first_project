import json
import os
import re
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, ValidationError

# Free-tier model on OpenRouter (no billing/credits required).
# Note: openai/gpt-oss-120b:free was retired by OpenRouter (only the paid
# openai/gpt-oss-120b remains); openai/gpt-oss-20b:free is the free sibling.
DEFAULT_MODEL = "openai/gpt-oss-20b:free"

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)


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


def _build_system_prompt(board: dict[str, Any]) -> str:
    return f"""You are an assistant embedded in a Kanban board app.

The current board is given below as JSON. It already includes every column \
id (e.g. "col-1") and card id (e.g. "card-3") that exist right now -- you \
already have everything you need, so NEVER ask the user for a column id, \
card id, or the board JSON. Read it from here instead.

Current board JSON:
{json.dumps(board)}

Respond with ONLY a single JSON object, no markdown code fences, no \
commentary outside the JSON, of the form:
{{"reply": "<short natural-language reply to the user>", "actions": [<zero or more actions>]}}

Each action in "actions" is one of these shapes:
{{"type": "add_card", "column_id": "<column id from the board above>", "title": "<title>", "details": "<details, optional>"}}
{{"type": "update_card", "card_id": "<card id from the board above>", "title": "<optional new title>", "details": "<optional new details>"}}
{{"type": "delete_card", "card_id": "<card id from the board above>"}}
{{"type": "move_card", "card_id": "<card id from the board above>", "column_id": "<target column id from the board above>", "index": <0-based position in the target column>}}
{{"type": "rename_column", "column_id": "<column id from the board above>", "title": "<new title>"}}

Rules:
- Only ever use column ids and card ids that literally appear in the board \
JSON above. Never invent ids, and never ask the user to supply ids -- look \
them up yourself.
- If the user asks you to add/rename something without specifying exact \
wording (e.g. "imagine something", "you decide"), just pick something \
reasonable yourself instead of asking a follow-up question.
- Only include actions the user actually asked for. If the user just asked \
a question or made small talk, "actions" must be an empty list.
- You may include multiple actions in one reply if the user asked for \
multiple changes (e.g. one add_card action per column).
- Keep "reply" short and conversational.
"""


def _extract_json_object(content: str) -> str:
    stripped = content.strip()
    fence_match = _CODE_FENCE_RE.match(stripped)
    if fence_match:
        stripped = fence_match.group(1).strip()
    return stripped


def chat(
    board: dict[str, Any], history: list[dict[str, str]], message: str
) -> ChatReply:
    client = get_client()
    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)

    messages = [
        {"role": "system", "content": _build_system_prompt(board)},
        *history,
        {"role": "user", "content": message},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
    )
    content = _extract_json_object(response.choices[0].message.content or "{}")

    try:
        return ChatReply.model_validate_json(content)
    except ValidationError:
        return ChatReply(reply=content, actions=[])
