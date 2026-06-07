from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from flowforge.catalog import CATALOG
from flowforge.spec import GraphSpec
from flowforge.validate import validate


class _State(TypedDict):
    params: dict[str, float]
    values: dict[str, float]


def compile_graph(spec: GraphSpec):
    """Return a compiled LangGraph app from a validated GraphSpec."""
    topo_order = validate(spec)

    node_map = {n.id: n for n in spec.nodes}
    builder = StateGraph(_State)

    for nid in topo_order:
        node = node_map[nid]
        op_fn = CATALOG[node.op].fn
        inputs = list(node.inputs)

        def make_node(node_id: str, fn: Any, inp: list[str]):
            def _node(state: _State) -> dict[str, Any]:
                lookup = {**state["params"], **state["values"]}
                args = [lookup[ref] for ref in inp]
                result = fn(*args)
                return {"values": {**state["values"], node_id: result}}

            _node.__name__ = node_id
            return _node

        builder.add_node(nid, make_node(nid, op_fn, inputs))

    # Linear chain: START → n0 → n1 → … → END
    prev = START
    for nid in topo_order:
        builder.add_edge(prev, nid)
        prev = nid
    builder.add_edge(prev, END)

    return builder.compile()
