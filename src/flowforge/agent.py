import json
import os
import re

from flowforge.catalog import CATALOG
from flowforge.spec import GraphSpec
from flowforge.validate import ValidationError, validate


def _catalog_description() -> str:
    lines = ["Available node types:"]
    for name, nt in CATALOG.items():
        lines.append(f"  {name}: {nt.description} (arity={nt.arity})")
    return "\n".join(lines)


def _build_system_prompt() -> str:
    return (
        "You are a graph planner. Given an arithmetic word problem, "
        "output a single JSON object matching the GraphSpec schema below. "
        "Output ONLY the JSON object — no markdown fences, no explanation.\n\n"
        + _catalog_description()
        + "\n\n"
        "Schema:\n"
        "{\n"
        '  "name": string,\n'
        '  "description": string,\n'
        '  "params": [string, ...],\n'
        '  "initial_params": {string: float, ...},\n'
        '  "nodes": [\n'
        '    {"id": string, "op": string, "inputs": [string, ...]}\n'
        "  ],\n"
        '  "output": string\n'
        "}\n\n"
        "Rules:\n"
        "- 'params' lists symbolic names for each number extracted from the problem.\n"
        "- 'initial_params' maps every param name to its numeric value.\n"
        "- Each node's 'inputs' entries must be param names or prior node ids.\n"
        "- Each node's 'inputs' length must match the op's arity exactly.\n"
        "- Nodes must form a DAG (no cycles).\n"
        "- 'output' must equal one of the node ids.\n\n"
        "Example — 'What is 3 plus 4?':\n"
        "{\n"
        '  "name": "add_3_4",\n'
        '  "description": "Add 3 and 4",\n'
        '  "params": ["a", "b"],\n'
        '  "initial_params": {"a": 3.0, "b": 4.0},\n'
        '  "nodes": [\n'
        '    {"id": "n0", "op": "add", "inputs": ["a", "b"]}\n'
        "  ],\n"
        '  "output": "n0"\n'
        "}"
    )


def _extract_json(text: str) -> str:
    """Return the first balanced {...} block from model output."""
    # Strip markdown fences
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object found in model response")
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise ValueError("unbalanced braces in model response")


class Agent:
    MAX_RETRIES = 2

    def __init__(self, model: str = "openai/gpt-oss-120b") -> None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENROUTER_API_KEY is not set")
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "langchain-openai is required for the live planner: uv add langchain-openai"
            )

        self._llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
        )
        self._system = _build_system_prompt()

    def plan(self, problem: str) -> GraphSpec:
        messages: list[dict] = [
            {"role": "system", "content": self._system},
            {"role": "user", "content": problem},
        ]
        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES + 1):
            response = self._llm.invoke(messages)
            raw: str = response.content if hasattr(response, "content") else str(response)

            try:
                json_str = _extract_json(raw)
                spec = GraphSpec.model_validate(json.loads(json_str))
                validate(spec)
                return spec
            except (ValueError, ValidationError, Exception) as exc:
                last_error = exc
                messages = messages + [
                    {"role": "assistant", "content": raw},
                    {
                        "role": "user",
                        "content": (
                            f"Your output failed with: {exc}\n"
                            "Fix the JSON and output only the corrected object, "
                            "with no markdown fences or extra text."
                        ),
                    },
                ]

        raise ValueError(
            f"failed to produce a valid GraphSpec after {self.MAX_RETRIES + 1} attempts"
        ) from last_error
