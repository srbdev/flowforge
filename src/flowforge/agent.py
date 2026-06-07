import os

from flowforge.catalog import CATALOG
from flowforge.spec import GraphSpec


def _catalog_description() -> str:
    lines = ["Available node types:"]
    for name, nt in CATALOG.items():
        lines.append(f"  {name}: {nt.description} (arity={nt.arity})")
    return "\n".join(lines)


class Agent:
    def __init__(self, model: str = "mistralai/mistral-medium-3-5") -> None:
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
        ).with_structured_output(GraphSpec)

    def plan(self, problem: str) -> GraphSpec:
        system = (
            "You are a graph planner. Given an arithmetic word problem, "
            "emit a GraphSpec JSON using only the following node types.\n\n"
            + _catalog_description()
            + "\n\nRules:\n"
            "- Each node reads named params or prior node ids as inputs.\n"
            "- Nodes must form a DAG (no cycles).\n"
            "- The 'output' field must be a node id.\n"
            "- 'params' lists the symbolic parameter names; 'initial_params' maps them to the "
            "concrete numbers extracted from the problem."
        )
        return self._llm.invoke(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": problem},
            ]
        )
