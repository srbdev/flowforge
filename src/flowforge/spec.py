from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class NodeSpec(BaseModel):
    id: str
    op: str
    inputs: list[str]


class GraphSpec(BaseModel):
    name: str
    description: str
    params: list[str]
    initial_params: dict[str, float]
    nodes: list[NodeSpec]
    output: str

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: str | Path) -> GraphSpec:
        return cls.model_validate_json(Path(path).read_text())
