from __future__ import annotations
from pathlib import Path, PurePath
from typing import Literal

import logging
import httpx
import warnings
import aiofiles
import json
from pydantic import ValidationError
from the_finals_leaderboard.api import *
from the_finals_leaderboard.models import *
from the_finals_leaderboard.filtering import *

SCRIPT_DIR = Path(__file__).parent
CACHED_DATA_PATH = SCRIPT_DIR / "cached_data"

logger = logging.getLogger(__name__)


class Client():
    def __init__(
        self,
        use_cached: bool = False,
        url: str = "https://api.the-finals-leaderboard.com",
        timeout: float = 10.0
    ):
        self.use_cached = use_cached
        self._sync_client = httpx.Client(
            base_url=url,
            timeout=timeout
        )
        self._async_client = httpx.AsyncClient(
            base_url=url,
            timeout=timeout
        )

        if use_cached:
            logger.info(f"Client created with caching enabled")
        else:
            logger.info(f"Client created without caching enabled")

    @staticmethod
    def _api_path(leaderboard: Leaderboard, platform: Platform):
        path = PurePath("v1") / "leaderboard"
        path /= f"{leaderboard.value}"

        match leaderboard:
            case Leaderboard.CB1 | Leaderboard.CB2:
                pass
            case Leaderboard.OB | Leaderboard.S1 | Leaderboard.S2:
                path /= f"{platform.value}"
            case _:
                path /= f"crossplay"

        return path

    @staticmethod
    def _cache_path(path: PurePath):
        return CACHED_DATA_PATH / PurePath(*path.parts[1:])

    def _get_leaderboard_sync_cached(
        self,
        leaderboard: Leaderboard,
        name: str | None = None,
        club_tag: str | None = None,
        exact_club_tag: bool | None = None,
        platform: Platform = Platform.CROSSPLAY
    ) -> dict:
        leaderboard = Leaderboard(leaderboard)
        platform = Platform(platform)

        path = Client._cache_path(Client._api_path(leaderboard, platform))

        if not path.exists():
            raise ValueError(f"Cached data for {leaderboard.value} does not exist")

        with open(path/"data.json", "rb") as fp:
            data: dict = json.load(fp)

        filtered = faithful_leaderboard_filter(
            data,
            name=name,
            club_tag=club_tag,
            exact_club_tag=exact_club_tag
        )

        return filtered

    async def _get_leaderboard_async_cached(
        self,
        leaderboard: Leaderboard,
        name: str | None = None,
        club_tag: str | None = None,
        exact_club_tag: bool | None = None,
        platform: Platform = Platform.CROSSPLAY
    ) -> dict:
        leaderboard = Leaderboard(leaderboard)
        platform = Platform(platform)

        path = Client._cache_path(Client._api_path(leaderboard, platform))

        if not path.exists():
            raise ValueError(f"Cached data for {leaderboard.value} does not exist")

        async with aiofiles.open(path/"data.json", "rb") as fp:
            _data = await fp.read()
            data = json.loads(_data)

        filtered = faithful_leaderboard_filter(
            data,
            name=name,
            club_tag=club_tag,
            exact_club_tag=exact_club_tag
        )

        return filtered

    def _get_leaderboard_sync(
        self,
        leaderboard: Leaderboard,
        name: str | None = None,
        club_tag: str | None = None,
        exact_club_tag: bool | None = None,
        platform: Platform = Platform.CROSSPLAY
    ) -> dict:
        leaderboard = Leaderboard(leaderboard)
        platform = Platform(platform)

        path = Client._api_path(leaderboard, platform)

        params = {
            "name": name,
            "clubTag": club_tag,
            "exactClubTag": exact_club_tag
        }
        params = {key: value for key, value in params.items() if value}

        response = self._sync_client.get(
            path.as_posix(),
            params=params
        )
        response.raise_for_status()

        return response.json()

    async def _get_leaderboard_async(
        self,
        leaderboard: Leaderboard,
        name: str | None = None,
        club_tag: str | None = None,
        exact_club_tag: bool | None = None,
        platform: Platform = Platform.CROSSPLAY
    ) -> dict:
        leaderboard = Leaderboard(leaderboard)
        platform = Platform(platform)

        path = Client._api_path(leaderboard, platform)

        params = {
            "name": name,
            "clubTag": club_tag,
            "exactClubTag": exact_club_tag
        }
        params = {key: value for key, value in params.items() if value}

        response = await self._async_client.get(
            path.as_posix(),
            params=params
        )
        response.raise_for_status()

        return response.json()

    def get_leaderboard_sync(
        self,
        leaderboard: Leaderboard,
        name: str | None = None,
        club_tag: str | None = None,
        exact_club_tag: bool | None = None,
        platform: Platform = Platform.CROSSPLAY
    ):
        """
        Get a leaderboard synchronously.

        Args:
            leaderboard (Leaderboard): Which leaderboard to get data from.
            name (str | None, optional): Name filter, case-insensitive. Defaults to None.
            club_tag (str | None, optional): Club tag filter. Defaults to None.
            exact_club_tag (bool | None, optional): Whether or not to filter by the EXACT club tag, if club_tag is not None. Defaults to None.
            platform (Platform, optional): Required for OB, S1, and S2. Defaults to Platform.CROSSPLAY.
        """
        leaderboard = Leaderboard(leaderboard)
        platform = Platform(platform)

        logger.info(f"Sync get for {leaderboard.value} issued.")
        if self.use_cached:
            logger.info(f"Trying to retrieve {leaderboard.value} data from cache...")
            try:
                data = self._get_leaderboard_sync_cached(
                    leaderboard,
                    name,
                    club_tag,
                    exact_club_tag,
                    platform
                )
                logger.info("...Found!")
            except ValueError:
                data = self._get_leaderboard_sync(
                    leaderboard,
                    name,
                    club_tag,
                    exact_club_tag,
                    platform
                )
                logger.info("...Not found, falling back to live data from API.")
        else:
            logger.info("Skipping cache.")
            data = self._get_leaderboard_sync(
                leaderboard,
                name,
                club_tag,
                exact_club_tag,
                platform
            )

        try:
            return LeaderboardResult[LEADERBOARD_USER_MAP[leaderboard]].model_validate(data)
        except ValidationError as e:
            raise ValueError("Could not convert leaderboard data to object") from e

    async def get_leaderboard_async(
        self,
        leaderboard: Leaderboard,
        name: str | None = None,
        club_tag: str | None = None,
        exact_club_tag: bool | None = None,
        platform: Platform = Platform.CROSSPLAY
    ):
        """
        Get a leaderboard asynchronously.

        Args:
            leaderboard (Leaderboard): Which leaderboard to get data from.
            name (str | None, optional): Name filter, case-insensitive. Defaults to None.
            club_tag (str | None, optional): Club tag filter. Defaults to None.
            exact_club_tag (bool | None, optional): Whether or not to filter by the EXACT club tag, if club_tag is not None. Defaults to None.
            platform (Platform, optional): Required for OB, S1, and S2. Defaults to Platform.CROSSPLAY.
        """
        leaderboard = Leaderboard(leaderboard)
        platform = Platform(platform)

        logger.info(f"Async get for {leaderboard.value} issued.")
        if self.use_cached:
            logger.info(f"Trying to retrieve {leaderboard.value} data from cache...")
            try:
                data = await self._get_leaderboard_async_cached(
                    leaderboard,
                    name,
                    club_tag,
                    exact_club_tag,
                    platform
                )
                logger.info("...Found!")
            except ValueError:
                data = await self._get_leaderboard_async(
                    leaderboard,
                    name,
                    club_tag,
                    exact_club_tag,
                    platform
                )
                logger.info("...Not found, falling back to live data from API.")
        else:
            logger.info("Skipping cache.")
            data = await self._get_leaderboard_async(
                leaderboard,
                name,
                club_tag,
                exact_club_tag,
                platform
            )

        try:
            return LeaderboardResult[LEADERBOARD_USER_MAP[leaderboard]].model_validate(data)
        except ValidationError as e:
            raise ValueError("Could not convert leaderboard data to object") from e
