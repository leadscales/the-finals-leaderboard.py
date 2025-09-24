from __future__ import annotations

import operator
import re
from enum import Enum
from typing import Any, List, TypeVar

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


def _match_insen_wild(haystack: str, needle: str):
    return needle.casefold() in haystack.casefold()


def _match_insen_exact(haystack: str, needle: str):
    return haystack.casefold() == needle.casefold()


def faithful_filter(data: dict, name: str | None = None, club_tag: str | None = None, exact_club_tag: bool | None = None):
    result: dict[str, Any] = {
        "meta": {
            "leaderboardVersion": data["meta"]["leaderboardVersion"],
            "dataSource": data["meta"]["dataSource"]
        }
    }
    players = data["data"]

    if name:
        players = [
            e for e in players
            if any(
                _match_insen_wild(e.get(field, ""), name)
                for field in ["name", "steamName", "psnName", "xboxName"]
            )
        ]
        result["meta"]["nameFilter"] = name

    if club_tag:
        if exact_club_tag:
            players = [
                e for e in players
                if "clubTag" in e and _match_insen_exact(e["clubTag"], club_tag)
            ]
        else:
            players = [
                e for e in players
                if "clubTag" in e and _match_insen_wild(e["clubTag"], club_tag)
            ]

        if any("clubTag" in e for e in players):
            result["meta"]["clubTagFilter"] = club_tag

    result["count"] = len(players)
    result["data"] = players

    return result


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


def extended_filter(players: List[T], **filters) -> List[T]:
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
