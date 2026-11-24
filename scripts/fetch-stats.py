#!/usr/bin/env python3
"""Fetch the profile's GitHub numbers into assets/stats.json for the stats panel.

Stars and repositories count public, non-fork repositories the account owns, which is what a
visitor can check. Commits and pull requests are what the token can see (the daily workflow's
GITHUB_TOKEN sees public work); contributions and both streaks come from the contribution
calendar, which also counts private work when the profile shares it. The GraphQL API has no
anonymous access, so GITHUB_TOKEN is required. On any failure the existing file is kept.

    GITHUB_TOKEN=... python scripts/fetch-stats.py
"""
import datetime
import json
import os
import urllib.request
from pathlib import Path

USER = "DuongNAD"
DEST = Path(__file__).resolve().parent.parent / "assets" / "stats.json"

PROFILE_QUERY = (
    "query($login:String!,$after:String){user(login:$login){"
    "followers{totalCount} pullRequests{totalCount} "
    "contributionsCollection{contributionYears} "
    "repositories(ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false,first:100,after:$after){"
    "totalCount nodes{stargazerCount} pageInfo{hasNextPage endCursor}}}}"
)
YEAR_FIELDS = (
    "totalCommitContributions "
    "contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}"
)


def years_query(years: list[int]) -> str:
    """One aliased contributionsCollection per calendar year (the API allows a year at most)."""
    parts = [
        f'y{year}:contributionsCollection(from:"{year}-01-01T00:00:00Z",to:"{year}-12-31T23:59:59Z")'
        f"{{{YEAR_FIELDS}}}"
        for year in years
    ]
    return f'query($login:String!){{user(login:$login){{{" ".join(parts)}}}}}'


def user_of(payload: dict) -> dict:
    if payload.get("errors") or not (payload.get("data") or {}).get("user"):
        raise ValueError(f"GraphQL error: {payload.get('errors') or 'user not found'}")
    return payload["data"]["user"]


def streaks(days: dict[str, int], today: datetime.date) -> tuple[int, int]:
    """(current, best) runs of consecutive days with at least one contribution.

    Days after `today` are ignored. A quiet `today` does not break the current streak yet:
    the day is not over, so the run is counted up to yesterday.
    """
    active = sorted(
        datetime.date.fromisoformat(day) for day, count in days.items()
        if count > 0 and datetime.date.fromisoformat(day) <= today
    )
    best = run = 0
    previous = None
    for day in active:
        run = run + 1 if previous is not None and day - previous == datetime.timedelta(days=1) else 1
        best = max(best, run)
        previous = day
    current = 0
    if active and today - active[-1] <= datetime.timedelta(days=1):
        current = run
    return current, best


def summarize(profile_pages: list[dict], years_payload: dict, today: datetime.date) -> dict[str, int]:
    first = user_of(profile_pages[0])
    repos = [node for page in profile_pages for node in user_of(page)["repositories"]["nodes"]]
    collections = user_of(years_payload).values()
    days: dict[str, int] = {}
    for collection in collections:
        for week in collection["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                days[day["date"]] = int(day["contributionCount"])
    current, best = streaks(days, today)
    return {
        "stars": sum(int(repo["stargazerCount"]) for repo in repos),
        "commits": sum(int(c["totalCommitContributions"]) for c in collections),
        "pull_requests": int(first["pullRequests"]["totalCount"]),
        "contributions": sum(int(c["contributionCalendar"]["totalContributions"]) for c in collections),
        "repositories": int(first["repositories"]["totalCount"]),
        "followers": int(first["followers"]["totalCount"]),
        "current_streak": current,
        "best_streak": best,
    }


def graphql(token: str, query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    headers = {
        "User-Agent": "profile-readme",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    request = urllib.request.Request("https://api.github.com/graphql", body, headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print(f"SKIPPED: GITHUB_TOKEN is not set; keeping {DEST.name}")
        return 0
    today = datetime.datetime.now(datetime.timezone.utc).date()
    try:
        pages, after = [], None
        while True:
            page = graphql(token, PROFILE_QUERY, {"login": USER, "after": after})
            pages.append(page)
            info = user_of(page)["repositories"]["pageInfo"]
            if not info["hasNextPage"]:
                break
            after = info["endCursor"]
        years = sorted(user_of(pages[0])["contributionsCollection"]["contributionYears"])
        if not years:
            raise ValueError("the account has no contribution years")
        stats = summarize(pages, graphql(token, years_query(years), {"login": USER}), today)
    except Exception as error:  # network, rate limit, or an unexpected payload
        print(f"SKIPPED: could not fetch profile stats ({error}); keeping {DEST.name}")
        return 0
    DEST.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {DEST.name}: {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
