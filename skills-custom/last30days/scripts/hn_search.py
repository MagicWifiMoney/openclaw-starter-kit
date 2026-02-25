#!/usr/bin/env python3
"""
hn_search.py - Search Hacker News for recent discussions on a topic.

Uses the free Algolia HN API (no API key needed).

Usage:
    python3 hn_search.py "AI agents" --days 30
    python3 hn_search.py "cursor" --days 7 --limit 20
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta


HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"


def search_hn(topic: str, days: int = 30, limit: int = 50) -> list:
    """
    Search Hacker News for stories about a topic from the last N days.
    
    Args:
        topic: Search query
        days: Number of days to look back (default: 30)
        limit: Maximum number of results (default: 50)
    
    Returns:
        List of story objects with title, url, points, comments, author, date, hn_url
    """
    # Calculate Unix timestamp for N days ago
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    cutoff_timestamp = int(cutoff.timestamp())
    
    # Build search URL
    params = {
        "query": topic,
        "tags": "story",
        "numericFilters": f"created_at_i>{cutoff_timestamp}",
        "hitsPerPage": limit,
    }
    
    url = f"{HN_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "last30days/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching HN data: {e}", file=sys.stderr)
        return []
    
    # Parse results
    results = []
    for hit in data.get("hits", []):
        # Skip if no URL (text-only posts)
        story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        
        # Parse date
        created_at = hit.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
        except:
            date_str = created_at[:10] if created_at else ""
        
        results.append({
            "title": hit.get("title", ""),
            "url": story_url,
            "points": hit.get("points", 0) or 0,
            "comments": hit.get("num_comments", 0) or 0,
            "author": hit.get("author", ""),
            "date": date_str,
            "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            "source": "hackernews",
        })
    
    # Sort by points (engagement)
    results.sort(key=lambda x: x["points"], reverse=True)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Search Hacker News for recent topics")
    parser.add_argument("topic", help="Topic to search for")
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back (default: 30)")
    parser.add_argument("--limit", type=int, default=50, help="Max results (default: 50)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    results = search_hn(args.topic, args.days, args.limit)
    
    if args.json or True:  # Always JSON for script use
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"[{r['points']}↑ {r['comments']}💬] {r['title']}")
            print(f"  {r['url']}")
            print(f"  HN: {r['hn_url']} ({r['date']})")
            print()


if __name__ == "__main__":
    main()
