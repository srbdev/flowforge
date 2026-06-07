from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class NodeSpec:
    name: str
    description: str
    arity: int
    fn: Callable[..., float]


def _divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("divide node: divisor is zero")
    return a / b


CATALOG: dict[str, NodeSpec] = {
    "add": NodeSpec("add", "Add two values", 2, lambda a, b: a + b),
    "subtract": NodeSpec("subtract", "Subtract b from a", 2, lambda a, b: a - b),
    "multiply": NodeSpec("multiply", "Multiply two values", 2, lambda a, b: a * b),
    "divide": NodeSpec("divide", "Divide a by b", 2, _divide),
}
