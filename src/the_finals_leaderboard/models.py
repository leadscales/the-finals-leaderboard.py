from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import TypeAlias, Union
from pydantic import BaseModel, field_validator, model_validator

__all__ = [
    "RankedLeague",
    # General users
    "BaseUser",
    "TaggedUser",
    "RankedUser",
    "QuickPlayUser",
    "WorldTourUser",
    "SponsorUser",
    "TerminalAttackUser",
    "PowerShiftUser",
    "QuickCashUser",
    "BankItUser",
    "TeamDeathmatchUser",
    # Specific users
    "CB1RankedUser",
    #
    "CB2RankedUser",
    #
    "OBRankedUser",
    #
    "Season1RankedUser",
    #
    "Season2RankedUser",
    #
    "Season3RankedUser",
    "Season3WorldTourUser",
    #
    "Season4RankedUser",
    "Season4SponsorUser",
    "Season4WorldTourUser",
    #
    "Season5RankedUser",
    "Season5SponsorUser",
    "Season5WorldTourUser",
    "Season5TerminalAttackUser",
    "Season5PowerShiftUser",
    "Season5QuickCashUser",
    "Season5BankItUser",
    #
    "Season6RankedUser",
    "Season6SponsorUser",
    "Season6WorldTourUser",
    "Season6TerminalAttackUser",
    "Season6PowerShiftUser",
    "Season6QuickCashUser",
    "Season6TeamDeathmatchUser",
    "Season6HeavyHittersUser",
    #
    "Season7RankedUser",
    "Season7SponsorUser",
    "Season7WorldTourUser",
    "Season7TerminalAttackUser",
    "Season7PowerShiftUser",
    "Season7QuickCashUser",
    "Season7TeamDeathmatchUser",
    "Season7BlastOffUser",
    "Season7CashBallUser",
    #
    "Season8RankedUser",
    "Season8SponsorUser",
    "Season8WorldTourUser",
    "Season8Head2HeadUser",
    "Season8PowerShiftUser",
    "Season8QuickCashUser",
    "Season8TeamDeathmatchUser",
    #
    "Season1User",
    "Season2User",
    "Season3User",
    "Season4User",
    "Season5User",
    "Season6User",
    "Season7User",
    "Season8User"
]  # pyright: ignore[reportUnsupportedDunderAll]

Season1User: TypeAlias = "Season1RankedUser"
Season2User: TypeAlias = "Season2RankedUser"
Season3User: TypeAlias = "Season3RankedUser"
Season4User: TypeAlias = Union["Season4RankedUser", "Season4SponsorUser", "Season4WorldTourUser"]
Season5User: TypeAlias = Union["Season5RankedUser", "Season5SponsorUser", "Season5WorldTourUser", "Season5TerminalAttackUser", "Season5PowerShiftUser", "Season5QuickCashUser", "Season5BankItUser"]
Season6User: TypeAlias = Union["Season6RankedUser", "Season6SponsorUser", "Season6WorldTourUser", "Season6TerminalAttackUser", "Season6PowerShiftUser", "Season6QuickCashUser", "Season6TeamDeathmatchUser", "Season6HeavyHittersUser"]
Season7User: TypeAlias = Union["Season7RankedUser", "Season7SponsorUser", "Season7WorldTourUser", "Season7TerminalAttackUser", "Season7PowerShiftUser", "Season7QuickCashUser", "Season7TeamDeathmatchUser", "Season7BlastOffUser", "Season7CashBallUser"]
Season8User: TypeAlias = Union["Season8RankedUser", "Season8SponsorUser", "Season8WorldTourUser", "Season8Head2HeadUser", "Season8PowerShiftUser", "Season8QuickCashUser", "Season8TeamDeathmatchUser"]


class RankedLeague(StrEnum):
    BRONZE = "Bronze"
    BRONZE_4 = "Bronze 4"
    BRONZE_3 = "Bronze 3"
    BRONZE_2 = "Bronze 2"
    BRONZE_1 = "Bronze 1"
    SILVER = "Silver"
    SILVER_4 = "Silver 4"
    SILVER_3 = "Silver 3"
    SILVER_2 = "Silver 2"
    SILVER_1 = "Silver 1"
    GOLD = "Gold"
    GOLD_4 = "Gold 4"
    GOLD_3 = "Gold 3"
    GOLD_2 = "Gold 2"
    GOLD_1 = "Gold 1"
    PLATINUM = "Platinum"
    PLATINUM_4 = "Platinum 4"
    PLATINUM_3 = "Platinum 3"
    PLATINUM_2 = "Platinum 2"
    PLATINUM_1 = "Platinum 1"
    DIAMOND = "Diamond"
    DIAMOND_4 = "Diamond 4"
    DIAMOND_3 = "Diamond 3"
    DIAMOND_2 = "Diamond 2"
    DIAMOND_1 = "Diamond 1"
    RUBY = "Ruby"


class LeagueNumber(IntEnum):
    BRONZE_4 = 1
    BRONZE_3 = 2
    BRONZE_2 = 3
    BRONZE_1 = 4
    SILVER_4 = 5
    SILVER_3 = 6
    SILVER_2 = 7
    SILVER_1 = 8
    GOLD_4 = 9
    GOLD_3 = 10
    GOLD_2 = 11
    GOLD_1 = 12
    PLATINUM_4 = 13
    PLATINUM_3 = 14
    PLATINUM_2 = 15
    PLATINUM_1 = 16
    DIAMOND_4 = 17
    DIAMOND_3 = 18
    DIAMOND_2 = 19
    DIAMOND_1 = 20
    RUBY = 21


def _to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


# Base classes


class BaseUser(BaseModel):
    name: str | None  # Theres a dude in OB who has no name lol check index 3301
    steam_name: str | None
    xbox_name: str | None
    psn_name: str | None

    model_config = {
        "alias_generator": _to_camel,
        "populate_by_name": True,
    }

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, values: dict):
        for k, v in values.items():
            if isinstance(v, str) and not v.strip():
                values[k] = None
        return values


class TaggedUser(BaseModel):
    club_tag: str | None


class RankedUser(BaseUser):
    rank: int
    league: RankedLeague

    @field_validator("league", mode="before")
    @classmethod
    def parse_league(cls, value):
        if isinstance(value, str):
            if value in RankedLeague._value2member_map_:
                return RankedLeague(value)
            else:
                raise ValueError(f"Invalid league name: {value}")


class QuickPlayUser(BaseUser):
    rank: int
    points: int

    @property
    def score(self):
        return self.points


class WorldTourUser(BaseUser):
    rank: int
    cashouts: int

    @property
    def score(self):
        return self.cashouts


class SponsorUser(BaseUser):
    rank: int
    fans: int
    sponsor: str

    @property
    def score(self):
        return self.fans


class TerminalAttackUser(QuickPlayUser):
    pass


class PowerShiftUser(QuickPlayUser):
    pass


class QuickCashUser(QuickPlayUser):
    pass


class BankItUser(QuickPlayUser):
    pass


class TeamDeathmatchUser(QuickPlayUser):
    pass


class Head2HeadUser(QuickPlayUser):
    pass

# Leaderboard return types


class CB1RankedUser(RankedUser):
    fame: int
    xp: int
    level: int
    cashouts: int

    @property
    def score(self):
        return self.fame


class CB2RankedUser(RankedUser):
    fame: int
    cashouts: int

    @property
    def score(self):
        return self.fame


class OBRankedUser(RankedUser):
    fame: int
    cashouts: int

    @property
    def score(self):
        return self.fame


class Season1RankedUser(RankedUser):
    fame: int
    cashouts: int

    @property
    def score(self):
        return self.fame


class Season2RankedUser(RankedUser):
    change: int
    league_number: LeagueNumber

    @property
    def score(self):
        return None


class Season3RankedUser(RankedUser):
    change: int
    league_number: LeagueNumber
    rank_score: int

    @property
    def score(self):
        return self.rank_score


class Season3WorldTourUser(WorldTourUser):
    pass


class Season4RankedUser(RankedUser):
    change: int
    league_number: LeagueNumber
    rank_score: int

    @property
    def score(self):
        return self.rank_score


class Season4WorldTourUser(WorldTourUser):
    pass


class Season4SponsorUser(SponsorUser):
    pass


class Season5RankedUser(RankedUser, TaggedUser):
    change: int
    league_number: LeagueNumber
    rank_score: int

    @property
    def score(self):
        return self.rank_score


class Season5SponsorUser(SponsorUser, TaggedUser):
    pass


class Season5WorldTourUser(WorldTourUser, TaggedUser):
    pass


class Season5TerminalAttackUser(TerminalAttackUser, TaggedUser):
    pass


class Season5PowerShiftUser(PowerShiftUser, TaggedUser):
    pass


class Season5QuickCashUser(QuickCashUser, TaggedUser):
    pass


class Season5BankItUser(BankItUser, TaggedUser):
    pass


class Season6RankedUser(RankedUser, TaggedUser):
    change: int
    league_number: LeagueNumber
    rank_score: int

    @property
    def score(self):
        return self.rank_score


class Season6SponsorUser(SponsorUser, TaggedUser):
    pass


class Season6WorldTourUser(WorldTourUser, TaggedUser):
    pass


class Season6TerminalAttackUser(TerminalAttackUser, TaggedUser):
    pass


class Season6PowerShiftUser(PowerShiftUser, TaggedUser):
    pass


class Season6QuickCashUser(QuickCashUser, TaggedUser):
    pass


class Season6TeamDeathmatchUser(TeamDeathmatchUser, TaggedUser):
    pass


class Season6HeavyHittersUser(BaseUser, TaggedUser):
    rank: int
    points: int

    @property
    def score(self):
        return self.points


class Season7RankedUser(RankedUser, TaggedUser):
    change: int
    league_number: LeagueNumber
    rank_score: int

    @property
    def score(self):
        return self.rank_score


class Season7SponsorUser(SponsorUser, TaggedUser):
    pass


class Season7WorldTourUser(WorldTourUser, TaggedUser):
    pass


class Season7TerminalAttackUser(TerminalAttackUser, TaggedUser):
    pass


class Season7PowerShiftUser(PowerShiftUser, TaggedUser):
    pass


class Season7QuickCashUser(QuickCashUser, TaggedUser):
    pass


class Season7TeamDeathmatchUser(TeamDeathmatchUser, TaggedUser):
    pass


class Season7BlastOffUser(BaseUser, TaggedUser):
    rank: int
    points: int

    @property
    def score(self):
        return self.points


class Season7CashBallUser(BaseUser, TaggedUser):
    rank: int
    points: int

    @property
    def score(self):
        return self.points


class Season8RankedUser(RankedUser, TaggedUser):
    change: int
    league_number: LeagueNumber
    rank_score: int

    @property
    def score(self):
        return self.rank_score


class Season8SponsorUser(SponsorUser, TaggedUser):
    pass


class Season8WorldTourUser(WorldTourUser, TaggedUser):
    pass


class Season8Head2HeadUser(Head2HeadUser, TaggedUser):
    pass


class Season8PowerShiftUser(PowerShiftUser, TaggedUser):
    pass


class Season8QuickCashUser(QuickCashUser, TaggedUser):
    pass


class Season8TeamDeathmatchUser(TeamDeathmatchUser, TaggedUser):
    pass
