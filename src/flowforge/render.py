from .spec import GraphSpec
from .validate import validate


def render(spec: GraphSpec) -> str:
    topo_order = validate(spec)
    node_map = {n.id: n for n in spec.nodes}
    lines: list[str] = []

    lines.append(f"Graph: {spec.name}")
    lines.append(f"Description: {spec.description}")
    lines.append(f"Params: {', '.join(spec.params)}")
    lines.append(f"Initial params: {spec.initial_params}")
    lines.append("")
    lines.append("Expression:")

    for nid in topo_order:
        node = node_map[nid]
        args = ", ".join(node.inputs)
        lines.append(f"  {nid} = {node.op}({args})")

    lines.append(f"  output = {spec.output}")
    lines.append("")
    lines.append("Flowchart:")
    lines.append("```text")
    lines.append("flowchart TD")
    lines.append("    START --> " + topo_order[0])
    for i, nid in enumerate(topo_order):
        node = node_map[nid]
        label = f"{nid}[{nid}: {node.op}({', '.join(node.inputs)})]"
        lines.append(f"    {label}")
        if i + 1 < len(topo_order):
            lines.append(f"    {nid} --> {topo_order[i + 1]}")
    lines.append(f"    {topo_order[-1]} --> END")
    lines.append("```")

    return "\n".join(lines)
