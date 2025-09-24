from __future__ import annotations

from pathlib import Path
from the_finals_leaderboard.models import *
from the_finals_leaderboard.api import *

SCRIPT_DIR = Path(__file__).parent


def generate_client():
    stub_lines = [
        "from __future__ import annotations",
        "",
        "from the_finals_leaderboard.api import *",
        "from the_finals_leaderboard.models import *",
        "from typing import Literal, overload, Mapping",
        "",
        "# The pit of overloads",
        "",
        "",
        "class Client():",
        "    def __init__(self, use_cached: bool = False, url: str = 'https://api.the-finals-leaderboard.com', timeout: float = 10.0): ...",
        "",
    ]

    for key, value in LEADERBOARD_USER_MAP.items():
        stub_lines.append("    @overload")
        stub_lines.append(
            f"    def get_leaderboard_sync(self, leaderboard: Literal[Leaderboard.{key.name}, {repr(key.value)}], "
            f"name: str | None = None, club_tag: str | None = None, exact_club_tag: bool | None = None, platform: Platform | Literal['crossplay', 'steam', 'xbox', 'psn'] = Platform.CROSSPLAY, filters: Mapping[str, Any] | None = None) "
            f"-> LeaderboardResult[{value.__name__}]: ..."
        )
        stub_lines.append("    @overload")
        stub_lines.append(
            f"    async def get_leaderboard_async(self, leaderboard: Literal[Leaderboard.{key.name}, {repr(key.value)}], "
            f"name: str | None = None, club_tag: str | None = None, exact_club_tag: bool | None = None, platform: Platform | Literal['crossplay', 'steam', 'xbox', 'psn'] = Platform.CROSSPLAY, filters: Mapping[str, Any] | None = None) "
            f"-> LeaderboardResult[{value.__name__}]: ..."
        )
        stub_lines.append("")

    return "\n".join(stub_lines).replace("'", "\"")


def main():
    gen_client = generate_client()

    with open(SCRIPT_DIR / "client.pyi", "w", encoding="utf-8") as fp:
        fp.write(gen_client)


if __name__ == "__main__":
    main()
