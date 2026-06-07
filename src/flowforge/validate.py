from collections import defaultdict, deque

from flowforge.catalog import CATALOG
from flowforge.spec import GraphSpec


class ValidationError(ValueError):
    pass


def validate(spec: GraphSpec) -> list[str]:
    """Return topological order of node ids; raise ValidationError on any structural problem."""
    node_ids = {n.id for n in spec.nodes}
    known_refs = set(spec.params) | node_ids

    for node in spec.nodes:
        if node.op not in CATALOG:
            raise ValidationError(f"unknown op '{node.op}' in node '{node.id}'")
        expected = CATALOG[node.op].arity
        if len(node.inputs) != expected:
            raise ValidationError(
                f"node '{node.id}' op '{node.op}' expects {expected} inputs, got {len(node.inputs)}"
            )
        for ref in node.inputs:
            if ref not in known_refs:
                raise ValidationError(f"node '{node.id}' has unknown input ref '{ref}'")

    if spec.output not in node_ids:
        raise ValidationError(f"output '{spec.output}' is not a known node id")

    # Build adjacency for topological sort (node → nodes that depend on it)
    in_degree: dict[str, int] = {n.id: 0 for n in spec.nodes}
    dependents: dict[str, list[str]] = defaultdict(list)

    for node in spec.nodes:
        for ref in node.inputs:
            if ref in node_ids:
                dependents[ref].append(node.id)
                in_degree[node.id] += 1

    queue: deque[str] = deque(nid for nid, deg in in_degree.items() if deg == 0)
    order: list[str] = []

    while queue:
        nid = queue.popleft()
        order.append(nid)
        for dep in dependents[nid]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    if len(order) != len(spec.nodes):
        raise ValidationError("graph contains a cycle")

    used_params = {
        ref for node in spec.nodes for ref in node.inputs if ref in set(spec.params)
    }
    for p in spec.params:
        if p not in used_params:
            import warnings

            warnings.warn(f"param '{p}' is declared but never used", stacklevel=2)

    return order
