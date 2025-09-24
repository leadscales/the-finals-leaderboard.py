# the-finals-leaderboard.py

[![Python Version](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)

A sync/async Python wrapper for the-finals-leaderboard.com, with some more user-friendly abstractions.

---

No PyPI module yet, you'll need to install it from the repo.
Not intended for production use yet.


## Features

- **Both sync and async interfaces.**
- **Django-style filters** (e.g., `score__gte=100_000`).
- **Caching for both "static" and "live" leaderboards.**
- **Generics** (e.g., `LeaderboardResult[Season7RankedUser]`).
- **"Convenience" properties** (e.g, `score`).
- **"Convenience" types** (e.g. `Season7User = Season7RankedUser | Season7SponsorUser | ...`)
- Pydantic inheritance.
- Various Pythonic changes, such as empty data from the API being converted to `None`.
- Works with the "official" instance, and self-hosted instances.

## Usage

```py
import the_finals_leaderboard

client = the_finals_leaderboard.Client(
    static_caching_policy="lazy",  # Lazily load stored instances of old leaderboards from the disk, bundled with the module, as opposed from fetching them from the API.
    live_caching_ttl=300  # Save results for 5 minutes, avoiding having to wait to a response from the API.
)

results = client.get_leaderboard_sync(
    "s8powershift",  # Or the_finals_leaderboard.Leaderboard.S8POWERSHIFT. Positional only.
    "crossplay",
    True,  # Ignore the cache this once, positional only.
    score__gte=100_000  # Django-style filters!
)  # -> LeaderboardResult[Season8PowerShiftUser]

print(results.players)  # View the results.

results = results.filter(club_tag__iexact="TM")  # Filter it some more.

print(results.players)  # View the newly filtered results.
```