import sys
from pathlib import Path

import click

import flowforge.executor as executor
from flowforge.agent import Agent
from flowforge.catalog import CATALOG
from flowforge.render import render
from flowforge.spec import GraphSpec
from flowforge.validate import validate


@click.group()
@click.version_option()
def main() -> None:
    """ff — dynamically generate and execute agentic graphs."""


@main.command()
@click.argument("prompt")
@click.option("--output", "-o")
def generate(prompt: str, output: str) -> None:
    """Generate a new graph."""
    agent = Agent()
    spec = agent.plan(prompt)

    print(render(spec))

    answer = input("Approve and save? [y/N] ").strip().lower()
    approve = answer in ("y", "yes")

    if not approve:
        print("Aborted.")
        sys.exit(0)

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    spec.save(path)
    print(f"Saved to {path}")


@main.command()
@click.argument("graph")
def run(graph: str) -> None:
    """Run a graph."""
    spec = GraphSpec.load(graph)
    params = dict(spec.initial_params)

    result = executor.run(spec, params)
    topo_order = validate(spec)
    node_map = {n.id: n for n in spec.nodes}

    print(f"Graph: {spec.name}")
    print(f"Params: {params}")
    print("Execution:")
    values: dict[str, float] = {}
    for nid in topo_order:
        node = node_map[nid]
        lookup = {**params, **values}
        args_display = ", ".join(f"{r}={lookup[r]}" for r in node.inputs)
        values[nid] = (
            lookup[nid] if nid in lookup else result if nid == spec.output else 0.0
        )
        # re-derive for display
        args_vals = [lookup[r] for r in node.inputs]
        val = CATALOG[node.op].fn(*args_vals)
        values[nid] = val
        print(f"  {nid} = {node.op}({args_display}) = {val}")
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
