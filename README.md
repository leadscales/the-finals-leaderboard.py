# the-finals-leaderboard.py

[![Python Version](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)

A sync/async Python wrapper for the-finals-leaderboard.com, with some more user-friendly abstractions.

---

## Features
- Both sync and async interfaces.
- Every returnable model has a `score` property, which returns whatever value is used to calculate a player's rank. No more conditional and match statements for what is effectively the same data between types.
- All models are Pydantic models, and are inherited from other models (e.g. `Season7PowerShiftUser = PowerShiftUser (+TaggedUser) = QuickPlayUser = BaseUser`), which simplifies data comparison between similar leaderboards.
- "Convience Types" (e.g. `Season7User = Season7RankedUser | Season7SponsorUser | ...`), which also simplifies data comparison.
- Some more Pythonic changes, such as empty data from the API being converted to `None`.
- Works with the "official" instance, and self-hosted instances.

## Usage

```py
>>> import the_finals_leaderboard

# Getting a leaderboard with filters
>>> client = the_finals_leaderboard.Client()
>>> client.get_leaderboard_sync(leaderboard="s7powershift",club_tag="TM",exact_club_tag=True)
LeaderboardResult[Season7PowershiftUser](...)

# Connecting to your own instance
>>> client = the_finals_leaderboard.Client(url="http://127.0.0.1:8787")

# Fetching data asynchronously
>>> client = the_finals_leaderboard.Client()
>>> # ... Some async function ...
>>> result = await client.get_leaderboard_async(leaderboard=the_finals_leaderboard.Leaderboard.S6)
result = LeaderboardResult[Season6RankedUser]
```