from __future__ import annotations

import operator
from enum import Enum
from typing import Any, Callable, List, TypeVar
from pydantic import BaseModel

OPS: dict[str, Callable[[Any, Any], bool]] = {
    "eq": operator.eq,
    "ne": operator.ne,
    "lt": operator.lt,
    "lte": operator.le,
    "gt": operator.gt,
    "gte": operator.ge,
    "contains": lambda a, b: b.casefold() in a.casefold() if isinstance(a, str) else False,
    "iexact": lambda a, b: a.casefold() == b.casefold() if isinstance(a, str) else False,
    "in": lambda a, b: a in b if isinstance(b, (list, tuple, set)) else False,
}


def normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def match_insen_wild(haystack: str, needle: str):
    return needle.casefold() in haystack.casefold()


def match_insen_exact(haystack: str, needle: str):
    return haystack.casefold() == needle.casefold()


def faithful_leaderboard_filter(data: dict, name: str | None = None, club_tag: str | None = None, exact_club_tag: bool | None = None):
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
                match_insen_wild(e.get(field, ""), name)
                for field in ["name", "steamName", "psnName", "xboxName"]
            )
        ]
        result["meta"]["nameFilter"] = name

    if club_tag:
        if exact_club_tag:
            players = [
                e for e in players
                if "clubTag" in e and match_insen_exact(e["clubTag"], club_tag)
            ]
        else:
            players = [
                e for e in players
                if "clubTag" in e and match_insen_wild(e["clubTag"], club_tag)
            ]

        if any("clubTag" in e for e in players):
            result["meta"]["clubTagFilter"] = club_tag

    result["count"] = len(players)
    result["data"] = players

    return result


T = TypeVar("T", bound=BaseModel)


def extended_leaderboard_filter(players: List[T], **filters) -> List[T]:
    if not players:
        return []

    results = players
    cls = players[0].__class__
    model_fields = cls.model_fields

    props = set()
    for base in cls.__mro__:
        props.update(
            name for name, attr in base.__dict__.items() if isinstance(attr, property)
        )

    for key, expected in filters.items():
        if "__" in key:
            field, op = key.split("__", 1)
        else:
            field, op = key, "eq"

        if op not in OPS:
            raise ValueError(f"Unsupported operator: {op}")

        func = OPS[op]

        if field not in model_fields and field not in props:
            continue

        results = [
            p for p in results
            if func(normalize(getattr(p, field)), normalize(expected))
        ]

    return results
