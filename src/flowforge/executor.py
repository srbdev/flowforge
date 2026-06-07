from flowforge.compiler import compile_graph
from flowforge.spec import GraphSpec
from flowforge.validate import validate


def run(spec: GraphSpec, params: dict[str, float]) -> float:
    validate(spec)
    app = compile_graph(spec)
    final_state = app.invoke({"params": params, "values": {}})
    return final_state["values"][spec.output]
