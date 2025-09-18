from typing import Any


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

