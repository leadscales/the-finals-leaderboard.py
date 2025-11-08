from __future__ import annotations

from copy import deepcopy
from enum import StrEnum
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel, Field, model_validator

from the_finals_leaderboard import filtering, models

T = TypeVar("T")


def _to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class LeaderboardResult(BaseModel, Generic[T]):
    leaderboard: Leaderboard
    platform: Platform | None = None
    filters: dict[str, Any] | None = None

    players: list[T] = Field(alias="data")

    model_config = {
        "alias_generator": _to_camel,
        "populate_by_name": True,
    }

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, values: dict):
        meta = values.get("meta", {})

        mapping = {
            "leaderboardVersion": "leaderboard",
            "leaderboardPlatform": "platform",
        }

        for json_key, model_field in mapping.items():
            if json_key in meta:
                values[model_field] = meta[json_key]

        for k, v in values.items():
            if isinstance(v, str) and not v.strip():
                values[k] = None

        return values

    def filter(self, **filters):
        new = deepcopy(self)
        new.players = filtering.extended_filter(new.players, **filters)
        new.filters = filters
        return new


class Leaderboard(StrEnum):
    CB1 = "cb1"
    CB2 = "cb2"
    OB = "ob"
    S1 = "s1"
    S2 = "s2"
    S3 = "s3"
    S3ORIGINAL = "s3original"
    S3WORLDTOUR = "s3worldtour"
    S4 = "s4"
    S4WORLDTOUR = "s4worldtour"
    S4SPONSOR = "s4sponsor"
    S5 = "s5"
    S5SPONSOR = "s5sponsor"
    S5WORLDTOUR = "s5worldtour"
    S5TERMINALATTACK = "s5terminalattack"
    S5POWERSHIFT = "s5powershift"
    S5QUICKCASH = "s5quickcash"
    S5BANKIT = "s5bankit"
    S6 = "s6"
    S6SPONSOR = "s6sponsor"
    S6WORLDTOUR = "s6worldtour"
    S6TERMINALATTACK = "s6terminalattack"
    S6POWERSHIFT = "s6powershift"
    S6QUICKCASH = "s6quickcash"
    S6TEAMDEATHMATCH = "s6teamdeathmatch"
    S6HEAVYHITTERS = "s6heavyhitters"
    S7 = "s7"
    S7SPONSOR = "s7sponsor"
    S7WORLDTOUR = "s7worldtour"
    S7TERMINALATTACK = "s7terminalattack"
    S7POWERSHIFT = "s7powershift"
    S7QUICKCASH = "s7quickcash"
    S7TEAMDEATHMATCH = "s7teamdeathmatch"
    S7BLASTOFF = "s7blastoff"
    S7CASHBALL = "s7cashball"
    S8 = "s8"
    S8SPONSOR = "s8sponsor"
    S8WORLDTOUR = "s8worldtour"
    S8HEAD2HEAD = "s8head2head"
    S8POWERSHIFT = "s8powershift"
    S8QUICKCASH = "s8quickcash"
    S8TEAMDEATHMATCH = "s8teamdeathmatch"
    S8HEAVENORELSE = "s8heavenorelse"
    S8GHOULRUSH = "s8ghoulrush"


class Platform(StrEnum):
    CROSSPLAY = "crossplay"
    STEAM = "steam"
    XBOX = "xbox"
    PSN = "psn"


LEADERBOARD_USER_MAP: dict[Leaderboard, Type[models.BaseUser]] = {
    Leaderboard.CB1: models.CB1RankedUser,
    Leaderboard.CB2: models.CB2RankedUser,
    Leaderboard.OB: models.OBRankedUser,
    Leaderboard.S1: models.Season1RankedUser,
    Leaderboard.S2: models.Season2RankedUser,
    Leaderboard.S3: models.Season3RankedUser,
    Leaderboard.S3ORIGINAL: models.Season3RankedUser,
    Leaderboard.S3WORLDTOUR: models.Season3WorldTourUser,
    Leaderboard.S4: models.Season4RankedUser,
    Leaderboard.S4WORLDTOUR: models.Season4WorldTourUser,
    Leaderboard.S4SPONSOR: models.Season4SponsorUser,
    Leaderboard.S5: models.Season5RankedUser,
    Leaderboard.S5SPONSOR: models.Season5SponsorUser,
    Leaderboard.S5WORLDTOUR: models.Season5WorldTourUser,
    Leaderboard.S5TERMINALATTACK: models.Season5TerminalAttackUser,
    Leaderboard.S5POWERSHIFT: models.Season5PowerShiftUser,
    Leaderboard.S5QUICKCASH: models.Season5QuickCashUser,
    Leaderboard.S5BANKIT: models.Season5BankItUser,
    Leaderboard.S6: models.Season6RankedUser,
    Leaderboard.S6SPONSOR: models.Season6SponsorUser,
    Leaderboard.S6WORLDTOUR: models.Season6WorldTourUser,
    Leaderboard.S6TERMINALATTACK: models.Season6TerminalAttackUser,
    Leaderboard.S6POWERSHIFT: models.Season6PowerShiftUser,
    Leaderboard.S6QUICKCASH: models.Season6QuickCashUser,
    Leaderboard.S6TEAMDEATHMATCH: models.Season6TeamDeathmatchUser,
    Leaderboard.S6HEAVYHITTERS: models.Season6HeavyHittersUser,
    Leaderboard.S7: models.Season7RankedUser,
    Leaderboard.S7SPONSOR: models.Season7SponsorUser,
    Leaderboard.S7WORLDTOUR: models.Season7WorldTourUser,
    Leaderboard.S7TERMINALATTACK: models.Season7TerminalAttackUser,
    Leaderboard.S7POWERSHIFT: models.Season7PowerShiftUser,
    Leaderboard.S7QUICKCASH: models.Season7QuickCashUser,
    Leaderboard.S7TEAMDEATHMATCH: models.Season7TeamDeathmatchUser,
    Leaderboard.S7BLASTOFF: models.Season7BlastOffUser,
    Leaderboard.S7CASHBALL: models.Season7CashBallUser,
    Leaderboard.S8: models.Season8RankedUser,
    Leaderboard.S8SPONSOR: models.Season8SponsorUser,
    Leaderboard.S8WORLDTOUR: models.Season8WorldTourUser,
    Leaderboard.S8HEAD2HEAD: models.Season8Head2HeadUser,
    Leaderboard.S8POWERSHIFT: models.Season8PowerShiftUser,
    Leaderboard.S8QUICKCASH: models.Season8QuickCashUser,
    Leaderboard.S8TEAMDEATHMATCH: models.Season8TeamDeathmatchUser,
    Leaderboard.S8HEAVENORELSE: models.Season8HeavenOrElseUser,
    Leaderboard.S8GHOULRUSH: models.Season8GhoulRushUser
}

LEADERBOARD_PLATFORM_MAP = {
    Leaderboard.CB1: (),
    Leaderboard.CB2: (),
    Leaderboard.OB: (Platform.CROSSPLAY, Platform.STEAM, Platform.XBOX, Platform.PSN),
    Leaderboard.S1: (Platform.CROSSPLAY, Platform.STEAM, Platform.XBOX, Platform.PSN),
    Leaderboard.S2: (Platform.CROSSPLAY, Platform.STEAM, Platform.XBOX, Platform.PSN),
    Leaderboard.S3: (Platform.CROSSPLAY,),
    Leaderboard.S3ORIGINAL: (Platform.CROSSPLAY,),
    Leaderboard.S3WORLDTOUR: (Platform.CROSSPLAY,),
    Leaderboard.S4: (Platform.CROSSPLAY,),
    Leaderboard.S4WORLDTOUR: (Platform.CROSSPLAY,),
    Leaderboard.S4SPONSOR: (Platform.CROSSPLAY,),
    Leaderboard.S5: (Platform.CROSSPLAY,),
    Leaderboard.S5SPONSOR: (Platform.CROSSPLAY,),
    Leaderboard.S5WORLDTOUR: (Platform.CROSSPLAY,),
    Leaderboard.S5TERMINALATTACK: (Platform.CROSSPLAY,),
    Leaderboard.S5POWERSHIFT: (Platform.CROSSPLAY,),
    Leaderboard.S5QUICKCASH: (Platform.CROSSPLAY,),
    Leaderboard.S5BANKIT: (Platform.CROSSPLAY,),
    Leaderboard.S6: (Platform.CROSSPLAY,),
    Leaderboard.S6SPONSOR: (Platform.CROSSPLAY,),
    Leaderboard.S6WORLDTOUR: (Platform.CROSSPLAY,),
    Leaderboard.S6TERMINALATTACK: (Platform.CROSSPLAY,),
    Leaderboard.S6POWERSHIFT: (Platform.CROSSPLAY,),
    Leaderboard.S6QUICKCASH: (Platform.CROSSPLAY,),
    Leaderboard.S6TEAMDEATHMATCH: (Platform.CROSSPLAY,),
    Leaderboard.S6HEAVYHITTERS: (Platform.CROSSPLAY,),
    Leaderboard.S7: (Platform.CROSSPLAY,),
    Leaderboard.S7SPONSOR: (Platform.CROSSPLAY,),
    Leaderboard.S7WORLDTOUR: (Platform.CROSSPLAY,),
    Leaderboard.S7TERMINALATTACK: (Platform.CROSSPLAY,),
    Leaderboard.S7POWERSHIFT: (Platform.CROSSPLAY,),
    Leaderboard.S7QUICKCASH: (Platform.CROSSPLAY,),
    Leaderboard.S7TEAMDEATHMATCH: (Platform.CROSSPLAY,),
    Leaderboard.S7BLASTOFF: (Platform.CROSSPLAY,),
    Leaderboard.S7CASHBALL: (Platform.CROSSPLAY,),
    Leaderboard.S8: (Platform.CROSSPLAY,),
    Leaderboard.S8SPONSOR: (Platform.CROSSPLAY,),
    Leaderboard.S8WORLDTOUR: (Platform.CROSSPLAY,),
    Leaderboard.S8HEAD2HEAD: (Platform.CROSSPLAY,),
    Leaderboard.S8POWERSHIFT: (Platform.CROSSPLAY,),
    Leaderboard.S8QUICKCASH: (Platform.CROSSPLAY,),
    Leaderboard.S8TEAMDEATHMATCH: (Platform.CROSSPLAY,),
    Leaderboard.S8HEAVENORELSE: (Platform.CROSSPLAY,),
    Leaderboard.S8GHOULRUSH: (Platform.CROSSPLAY,)
}

CURRENT_SEASON_LEADERBOARDS = (
    Leaderboard.S8,
    Leaderboard.S8SPONSOR,
    Leaderboard.S8WORLDTOUR,
    Leaderboard.S8HEAD2HEAD,
    Leaderboard.S8POWERSHIFT,
    Leaderboard.S8QUICKCASH,
    Leaderboard.S8TEAMDEATHMATCH,
    Leaderboard.S8HEAVENORELSE,
    Leaderboard.S8GHOULRUSH
)
