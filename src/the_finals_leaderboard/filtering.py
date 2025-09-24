from __future__ import annotations

import operator
import re
from enum import Enum
from typing import Any, TypeVar

OPS = {
    "exact": operator.eq,
    "iexact": lambda a, b: str(a).lower() == str(b).lower(),

    "contains": lambda a, b: b in a,
    "icontains": lambda a, b: str(b).lower() in str(a).lower(),
    "startswith": lambda a, b: str(a).startswith(str(b)),
    "istartswith": lambda a, b: str(a).lower().startswith(str(b).lower()),
    "endswith": lambda a, b: str(a).endswith(str(b)),
    "iendswith": lambda a, b: str(a).lower().endswith(str(b).lower()),

    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,

    "isnull": lambda a, b: (a is None) == b,

    "regex": lambda a, b: re.search(b, str(a)) is not None,
    "iregex": lambda a, b: re.search(b, str(a), re.IGNORECASE) is not None,

    "exists": lambda a, b: (a is not None) == b,
}


def _resolve_enum(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


T = TypeVar("T")


def passes_filter(item: Any, field: str, op_name: str, target_value: Any) -> bool:
    if not hasattr(item, field):
        return True

    val = getattr(item, field)

    val = _resolve_enum(val)
    if isinstance(target_value, Enum):
        target_value = target_value.value

    op_func = OPS.get(op_name)
    if not op_func:
        raise ValueError(f"Unsupported operator: {op_name}")

    try:
        return op_func(val, target_value)
    except Exception:
        return False


def extended_filter(players: list[T], **filters) -> list[T]:
    filtered = []
    for player in players:
        keep = True
        for expr, target_value in filters.items():
            if "__" in expr:
                field, op_name = expr.split("__", 1)
            else:
                field, op_name = expr, "exact"

            if not passes_filter(player, field, op_name, target_value):
                keep = False
                break
        if keep:
            filtered.append(player)
    return filtered
