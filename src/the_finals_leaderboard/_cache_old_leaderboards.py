from __future__ import annotations

import httpx
import the_finals_leaderboard
import json
from pathlib import PurePath, Path


SCRIPT_DIR = Path(__file__).parent
CACHED_DATA_PATH = SCRIPT_DIR / "cached_data"
CURRENT_SEASON = "s8"
CLIENT = httpx.Client(
    base_url="https://api.the-finals-leaderboard.com"
)


def main():
    paths: list[PurePath] = []
    for leaderboard, platforms in the_finals_leaderboard.api.LEADERBOARD_PLATFORM_MAP.items():
        if leaderboard.startswith(CURRENT_SEASON):
            continue

        path = PurePath(leaderboard)

        if platforms:
            for platform in platforms:
                paths.append(
                    path / platform
                )
        else:
            paths.append(path)

    for path in paths:
        fs_path = Path(CACHED_DATA_PATH / "leaderboard" / path)
        fs_path.mkdir(parents=True, exist_ok=True)

        data = CLIENT.get(
            (PurePath("v1", "leaderboard")/path).as_posix()
        )
        data.raise_for_status()
        data_json = data.json()

        with open(fs_path / "data.json", "w", encoding="utf-8") as fp:
            json.dump(data_json, fp, ensure_ascii=False)


if __name__ == "__main__":
    main()
