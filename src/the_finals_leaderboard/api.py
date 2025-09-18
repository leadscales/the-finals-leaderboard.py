from __future__ import annotations

from enum import StrEnum
from typing import Generic, List, TypeVar, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator
from the_finals_leaderboard.models import *

T = TypeVar("T")


def _to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class LeaderboardResult(BaseModel, Generic[T]):
    leaderboard: Leaderboard
    platform: Platform | None = None
    name_filter: str | None = None
    club_tag_filter: str | None = None
    exact_club_tag: bool | None = None
    players: List[T] = Field(alias="data")

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
            "exactClubTag": "exact_club_tag",
            "nameFilter": "name_filter",
            "clubTagFilter": "club_tag_filter",
        }

        for json_key, model_field in mapping.items():
            if json_key in meta:
                values[model_field] = meta[json_key]

        for k, v in values.items():
            if isinstance(v, str) and not v.strip():
                values[k] = None

        return values

    @field_validator("club_tag_filter")
    @classmethod
    def uppercase(cls, value):
        if value is None:
            return None
        return value.upper()


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


class Platform(StrEnum):
    CROSSPLAY = "crossplay"
    STEAM = "steam"
    XBOX = "xbox"
    PSN = "psn"


LEADERBOARD_USER_MAP = {
    Leaderboard.CB1: CB1RankedUser,
    Leaderboard.CB2: CB2RankedUser,
    Leaderboard.OB: OBRankedUser,
    Leaderboard.S1: Season1RankedUser,
    Leaderboard.S2: Season2RankedUser,
    Leaderboard.S3: Season3RankedUser,
    Leaderboard.S3ORIGINAL: Season3RankedUser,
    Leaderboard.S3WORLDTOUR: Season3WorldTourUser,
    Leaderboard.S4: Season4RankedUser,
    Leaderboard.S4WORLDTOUR: Season4WorldTourUser,
    Leaderboard.S4SPONSOR: Season4SponsorUser,
    Leaderboard.S5: Season5RankedUser,
    Leaderboard.S5SPONSOR: Season5SponsorUser,
    Leaderboard.S5WORLDTOUR: Season5WorldTourUser,
    Leaderboard.S5TERMINALATTACK: Season5TerminalAttackUser,
    Leaderboard.S5POWERSHIFT: Season5PowerShiftUser,
    Leaderboard.S5QUICKCASH: Season5QuickCashUser,
    Leaderboard.S5BANKIT: Season5BankItUser,
    Leaderboard.S6: Season6RankedUser,
    Leaderboard.S6SPONSOR: Season6SponsorUser,
    Leaderboard.S6WORLDTOUR: Season6WorldTourUser,
    Leaderboard.S6TERMINALATTACK: Season6TerminalAttackUser,
    Leaderboard.S6POWERSHIFT: Season6PowerShiftUser,
    Leaderboard.S6QUICKCASH: Season6QuickCashUser,
    Leaderboard.S6TEAMDEATHMATCH: Season6TeamDeathmatchUser,
    Leaderboard.S6HEAVYHITTERS: Season6HeavyHittersUser,
    Leaderboard.S7: Season7RankedUser,
    Leaderboard.S7SPONSOR: Season7SponsorUser,
    Leaderboard.S7WORLDTOUR: Season7WorldTourUser,
    Leaderboard.S7TERMINALATTACK: Season7TerminalAttackUser,
    Leaderboard.S7POWERSHIFT: Season7PowerShiftUser,
    Leaderboard.S7QUICKCASH: Season7QuickCashUser,
    Leaderboard.S7TEAMDEATHMATCH: Season7TeamDeathmatchUser,
    Leaderboard.S7BLASTOFF: Season7BlastOffUser,
    Leaderboard.S7CASHBALL: Season7CashBallUser,
    Leaderboard.S8: Season8RankedUser,
    Leaderboard.S8SPONSOR: Season8SponsorUser,
    Leaderboard.S8WORLDTOUR: Season8WorldTourUser,
    Leaderboard.S8HEAD2HEAD: Season8Head2HeadUser,
    Leaderboard.S8POWERSHIFT: Season8PowerShiftUser,
    Leaderboard.S8QUICKCASH: Season8QuickCashUser,
    Leaderboard.S8TEAMDEATHMATCH: Season8TeamDeathmatchUser,
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
}
