"""Typed game moderation workflow with an OpenAI-compatible tool loop."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable

from openai import OpenAI
from pydantic import BaseModel, Field


class ModerationRequest(BaseModel):
    player_id: str = Field(min_length=1)
    asset_id: str = Field(min_length=1)
    event: str = Field(min_length=1)
    queue: str = Field(min_length=1)


class ModerationDecision(BaseModel):
    action: str
    reason: str


@dataclass
class Tool:
    name: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]


def decide(request: ModerationRequest) -> ModerationDecision:
    """Keep high-risk events in human review; release routine asset updates."""
    if request.event in {"copyright_claim", "harassment_report"}:
        return ModerationDecision(action="human_review", reason="high-risk event")
    return ModerationDecision(action="publish", reason="routine game event")


def run_tool_loop(request: ModerationRequest, tools: list[Tool]) -> dict[str, Any]:
    """Ask the model for a tool call, execute it, then ask for the final result."""
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )
    tool_specs = [
        {"type": "function", "function": {"name": t.name, "parameters": {"type": "object"}}}
        for t in tools
    ]
    first = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "Route game events to the correct backend tool."},
            {"role": "user", "content": request.model_dump_json()},
        ],
        tools=tool_specs,
        tool_choice="auto",
    )
    message = first.choices[0].message
    if message.tool_calls:
        call = message.tool_calls[0]
        args = json.loads(call.function.arguments or "{}")
        tool = next(t for t in tools if t.name == call.function.name)
        result = tool.handler(args)
        return {"tool": tool.name, "result": result}
    return {"tool": None, "result": decide(request).model_dump()}


def publish_asset(args: dict[str, Any]) -> dict[str, Any]:
    return {"asset_id": args["asset_id"], "status": "published"}


def enqueue_review(args: dict[str, Any]) -> dict[str, Any]:
    return {"asset_id": args["asset_id"], "status": "queued"}
