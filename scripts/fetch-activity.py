#!/usr/bin/env python3
"""Fetch the last month of daily contribution counts into assets/activity.json.

Replaces the third-party activity-graph widget, whose Vercel deployment answers 402. The
GitHub GraphQL API has no anonymous access, so GITHUB_TOKEN is required. On any failure the
existing file is kept, like fetch-profile-stats.py does for the repo and follower counts.
"""
import datetime
import json
import os
import urllib.request
from pathlib import Path

USER = "DuongNAD"
DAYS = 31
DEST = Path(__file__).resolve().parent.parent / "assets" / "activity.json"
QUERY = (
    "query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){"
    "contributionsCollection(from:$from,to:$to){contributionCalendar{"
    "weeks{contributionDays{date contributionCount}}}}}}"
)


def window(today: datetime.date) -> tuple[datetime.date, datetime.date]:
    return today - datetime.timedelta(days=DAYS - 1), today


def extract(payload: dict, start: datetime.date, end: datetime.date) -> dict[str, int]:
    """Daily counts inside [start, end], keyed by ISO date."""
    if payload.get("errors") or not (payload.get("data") or {}).get("user"):
        raise ValueError(f"GraphQL error: {payload.get('errors') or 'user not found'}")
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = {
        day["date"]: int(day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    }
    counts = {d: days[d] for d in sorted(days) if start.isoformat() <= d <= end.isoformat()}
    if not counts:
        raise ValueError("no contribution days in the requested window")
    return counts


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print(f"SKIPPED: GITHUB_TOKEN is not set; keeping {DEST.name}")
        return 0
    start, end = window(datetime.datetime.now(datetime.timezone.utc).date())
    body = json.dumps(
        {
            "query": QUERY,
            "variables": {"login": USER, "from": f"{start}T00:00:00Z", "to": f"{end}T23:59:59Z"},
        }
    ).encode("utf-8")
    headers = {
        "User-Agent": "profile-readme",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        request = urllib.request.Request("https://api.github.com/graphql", body, headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            counts = extract(json.load(response), start, end)
    except Exception as error:  # network, rate limit, or an unexpected payload
        print(f"SKIPPED: could not fetch contribution activity ({error}); keeping {DEST.name}")
        return 0
    DEST.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {DEST.name}: {len(counts)} days, {sum(counts.values())} contributions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
