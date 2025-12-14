from __future__ import annotations

import gzip
import json
from importlib import resources
from pathlib import Path, PurePath
from typing import Any

import httpx

from the_finals_leaderboard import api

_SCRIPT_DIR = Path(__file__).parent
_STATIC_PATH = _SCRIPT_DIR / "static"
_CURRENT_SEASON = "s9"


def fetch_static():
    result: dict[str, dict[str, Any]] = {}

    with httpx.Client(base_url="https://api.the-finals-leaderboard.com") as client:
        for leaderboard, platforms in api.LEADERBOARD_PLATFORM_MAP.items():
            if leaderboard.value.startswith(_CURRENT_SEASON):
                continue

            if platforms:
                for platform in platforms:
                    path = PurePath("leaderboard", leaderboard)
                    path /= platform.value
                    result[path.as_posix().replace("/", "_")] = client.get(
                        url=f"v1/{path.as_posix()}"
                    ).json()

            else:
                path = PurePath("leaderboard", leaderboard)
                result[path.as_posix().replace("/", "_")] = client.get(
                    url=f"v1/{path.as_posix()}"
                ).json()

    return result


def save_static(data: dict[str, dict[str, Any]]):
    for key, value in data.items():
        _STATIC_PATH.mkdir(exist_ok=True, parents=True)
        out_path = _STATIC_PATH / f"{key}.json.gz"

        with gzip.open(out_path, "wt", encoding="utf-8") as fp:
            json.dump(value, fp, ensure_ascii=False)


def load_static(leaderboard: api.Leaderboard, platform: api.Platform | None) -> dict[str, Any]:
    fname = f"leaderboard_{leaderboard.value}"
    if platform:
        fname += f"_{platform.value}.json.gz"

    return load_static_fname(fname)


def load_static_fname(fname: str) -> dict[str, Any]:
    ref = resources.files("the_finals_leaderboard.static").joinpath(fname)
    with ref.open("rb") as fp:
        with gzip.open(fp, "rt", encoding="utf-8") as gz:
            return json.load(gz)


def list_static_fname():
    return [
        f.name
        for f in resources.files("the_finals_leaderboard.static").iterdir()
        if f.name.endswith(".json.gz")
    ]


if __name__ == "__main__":
    a = fetch_static()
    b = save_static(a)
