from __future__ import annotations

import datetime
import logging
import httpx
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal, Mapping
from pydantic import ValidationError
from the_finals_leaderboard import api, caching


_MAX_DT = datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)


@dataclass(slots=True)
class _CachedLeaderboard():
    data: dict[str, Any]
    exp_date: datetime.datetime


class StaticCachingPolicy(StrEnum):
    DISABLED = "disabled"
    DISK = "disk"
    LAZY = "lazy"
    EAGER = "eager"


logger = logging.getLogger(__name__)


class Client():
    def __init__(
        self,
        static_caching_policy: StaticCachingPolicy | Literal[StaticCachingPolicy.DISABLED, StaticCachingPolicy.DISK, StaticCachingPolicy.LAZY, StaticCachingPolicy.EAGER] = StaticCachingPolicy.LAZY,
        live_caching_ttl: datetime.timedelta | int = datetime.timedelta(minutes=5),
        url: str = "https://api.the-finals-leaderboard.com",
        timeout: float = 10.0
    ):

        self._cache: dict[str, _CachedLeaderboard] = {}

        self._static_caching_policy = StaticCachingPolicy(static_caching_policy)

        if self._static_caching_policy == StaticCachingPolicy.EAGER:
            self._preload_all_static()

        if isinstance(live_caching_ttl, int):
            self._live_caching_ttl = datetime.timedelta(seconds=live_caching_ttl)
        else:
            self._live_caching_ttl = live_caching_ttl

        self._sync_client = httpx.Client(
            base_url=url,
            timeout=timeout
        )
        self._async_client = httpx.AsyncClient(
            base_url=url,
            timeout=timeout
        )

        logger.info(f"Client created {repr(self)}")

    def __repr__(self):
        return "{0}(__static_caching_policy={1!r}, _live_caching_ttl={2!r}, url={3!r})".format(
            self.__class__.__name__,
            self._static_caching_policy,
            self._live_caching_ttl,
            str(self._sync_client.base_url)
        )

    @staticmethod
    def _cache_key(leaderboard: api.Leaderboard, platform: api.Platform | None):
        return f"leaderboard_{leaderboard.value}{'_'+platform.value if platform else ''}"

    @staticmethod
    def _api_path(leaderboard: api.Leaderboard, platform: api.Platform | None):
        return f"v1/leaderboard/{leaderboard.value}{'/'+platform.value if platform else ''}"

    @staticmethod
    def _parse_platform(leaderboard: api.Leaderboard, platform: api.Platform | None):
        match leaderboard:
            case api.Leaderboard.CB1 | api.Leaderboard.CB2:
                return None
            case api.Leaderboard.OB | api.Leaderboard.S1 | api.Leaderboard.S2:
                if platform is None:
                    raise ValueError(f"Platform must be provided for {leaderboard}")
                return api.Platform(platform)
            case _:
                return api.Platform.CROSSPLAY

    def _preload_all_static(self):
        for fname in caching.list_static_fname():
            name = fname[:-8]
            data = caching.load_static_fname(fname)
            self._cache[name] = _CachedLeaderboard(data, _MAX_DT)

    def _get_leaderboard_from_cache(self, leaderboard: api.Leaderboard, platform: api.Platform | None = None) -> _CachedLeaderboard | None:
        if self._static_caching_policy == StaticCachingPolicy.DISABLED and not self._live_caching_ttl:
            logging.info("All forms of caching disabled, returning None")
            return None

        now = datetime.datetime.now(datetime.timezone.utc)
        cache_key = Client._cache_key(leaderboard, platform)

        entry = self._cache.get(cache_key)

        logging.info(f"Trying to find cached data for {leaderboard.value}")

        if not entry:
            logging.info(f"Entry for {leaderboard.value} not found in cache")
            if self._static_caching_policy != StaticCachingPolicy.DISABLED:
                try:
                    entry = _CachedLeaderboard(caching.load_static(leaderboard, platform), _MAX_DT)
                except FileNotFoundError:
                    logging.info(f"Static file for {leaderboard.value} not found, returning None")
                    return None
                if self._static_caching_policy == StaticCachingPolicy.LAZY:
                    logging.info(f"Lazy caching enabled, saving {leaderboard.value} contents to cache")
                    self._cache[cache_key] = entry
            else:
                logging.info(f"Static caching is disabled, returning None")
                return None

        if entry.exp_date > now:
            logging.info(f"All checks passed, cache for {leaderboard.value} returned")
            return entry

        logging.info(f"Cache out of date, skipping for {leaderboard.value}")
        return None

    def _get_leaderboard_from_api_sync(self, leaderboard: api.Leaderboard, platform: api.Platform | None = None):
        now = datetime.datetime.now(datetime.timezone.utc)
        url = Client._api_path(leaderboard, platform)

        resp = self._sync_client.get(url)
        resp.raise_for_status()

        logging.info(f"Fetched leaderboard data for {leaderboard.value} from API")

        data = _CachedLeaderboard(resp.json(), now+self._live_caching_ttl)

        if self._live_caching_ttl.total_seconds() > 0:
            logging.info(f"Storing fetched data for {leaderboard.value} in cache")
            self._cache[Client._cache_key(leaderboard, platform)] = data

        return data

    async def _get_leaderboard_from_api_async(self, leaderboard: api.Leaderboard, platform: api.Platform | None = None):
        now = datetime.datetime.now(datetime.timezone.utc)
        url = Client._api_path(leaderboard, platform)

        resp = await self._async_client.get(url)
        resp.raise_for_status()

        logging.info(f"Fetched leaderboard data for {leaderboard.value} from API")

        data = _CachedLeaderboard(resp.json(), now+self._live_caching_ttl)

        if self._live_caching_ttl.total_seconds() > 0:
            logging.info(f"Storing fetched data for {leaderboard.value} in cache")
            self._cache[Client._cache_key(leaderboard, platform)] = data

        return data

    def get_leaderboard_sync(
        self,
        leaderboard: api.Leaderboard,
        platform: api.Platform | None = None,
        ignore_cache: bool = False,
        /,
        **filters: Any,
    ):
        leaderboard = api.Leaderboard(leaderboard)
        platform = Client._parse_platform(leaderboard, platform)

        data = None
        if not ignore_cache:
            data = self._get_leaderboard_from_cache(leaderboard, platform)
        if not data:
            data = self._get_leaderboard_from_api_sync(leaderboard, platform)

        try:
            return_type = api.LEADERBOARD_USER_MAP[leaderboard]
            model = api.LeaderboardResult[return_type].model_validate(data.data)
            if filters:
                model = model.filter(**filters)
            return model
        except ValidationError as e:
            raise ValueError("Unable to validate model. Was bad data returned?") from e

    async def get_leaderboard_async(
        self,
        leaderboard: api.Leaderboard,
        platform: api.Platform | None = None,
        ignore_cache: bool = False,
        /,
        **filters: Mapping[str, Any] | None,
    ):
        leaderboard = api.Leaderboard(leaderboard)
        platform = Client._parse_platform(leaderboard, platform)

        data = None
        if not ignore_cache:
            data = self._get_leaderboard_from_cache(leaderboard, platform)
        if not data:
            data = await self._get_leaderboard_from_api_async(leaderboard, platform)

        try:
            return_type = api.LEADERBOARD_USER_MAP[leaderboard]
            model = api.LeaderboardResult[return_type].model_validate(data.data)
            if filters:
                model = model.filter(**filters)
            return model
        except ValidationError as e:
            raise ValueError("Unable to validate model. Was bad data returned?") from e
