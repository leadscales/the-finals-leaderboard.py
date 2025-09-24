from __future__ import annotations

from pathlib import Path
from the_finals_leaderboard import models, api

SCRIPT_DIR = Path(__file__).parent


def generate_client():
    stub_lines = [
        "from __future__ import annotations",
        "",
        "import datetime",
        "from the_finals_leaderboard import models, api",
        "from typing import Literal, overload, Mapping, Any",
        "from enum import StrEnum",
        "",
        "",
        "class StaticCachingPolicy(StrEnum):",
        "    DISABLED = \"disabled\"",
        "    DISK = \"disk\"",
        "    LAZY = \"lazy\"",
        "    EAGER = \"eager\"",
        "",
        "",
        "class Client():",
        "    def __init__(",
        "        self,",
        "        static_caching_policy: Literal[StaticCachingPolicy.DISABLED, StaticCachingPolicy.DISK, StaticCachingPolicy.LAZY, StaticCachingPolicy.EAGER, \"disabled\", \"disk\", \"lazy\", \"eager\"] = StaticCachingPolicy.LAZY,",
        "        live_caching_ttl: datetime.timedelta | int = datetime.timedelta(minutes=5),",
        "        url: str = \"https://api.the-finals-leaderboard.com\",",
        "        timeout: float = 10.0",
        "    ): ...",
        "",
        "    # The pit of overloads",
        "",
    ]

    for key, value in api.LEADERBOARD_USER_MAP.items():
        stub_lines.append("    @overload")
        stub_lines.append(
            f"    def get_leaderboard_sync(self, leaderboard: Literal[api.Leaderboard.{key.name}, {repr(key.value)}], "
            f"platform: api.Platform | Literal['crossplay', 'steam', 'xbox', 'psn'] | None = None, "
            f"filters: Mapping[str, Any] | None = None) "
            f"-> api.LeaderboardResult[models.{value.__name__}]: ..."
        )
        stub_lines.append("    @overload")
        stub_lines.append(
            f"    async def get_leaderboard_async(self, leaderboard: Literal[api.Leaderboard.{key.name}, {repr(key.value)}], "
            f"platform: api.Platform | Literal['crossplay', 'steam', 'xbox', 'psn'] | None = None, "
            f"filters: Mapping[str, Any] | None = None) "
            f"-> api.LeaderboardResult[models.{value.__name__}]: ..."
        )
        stub_lines.append("")

    return "\n".join(stub_lines).replace("'", "\"")


def main():
    gen_client = generate_client()

    with open(SCRIPT_DIR / "client.pyi", "w", encoding="utf-8") as fp:
        fp.write(gen_client)


if __name__ == "__main__":
    main()
