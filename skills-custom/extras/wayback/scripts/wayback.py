#!/usr/bin/env python3
"""Wayback Machine CLI — query archived snapshots via the CDX API."""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import html
import re
from datetime import datetime

CDX_API = "https://web.archive.org/cdx/search/cdx"
WEB_BASE = "https://web.archive.org/web"


def cdx_query(url, params=None):
    """Query CDX API and return list of snapshot dicts."""
    p = {"url": url, "output": "json", "fl": "timestamp,original,statuscode,mimetype,digest"}
    if params:
        p.update(params)
    req_url = f"{CDX_API}?{urllib.parse.urlencode(p)}"
    try:
        with urllib.request.urlopen(req_url, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"**Error querying CDX API:** {e}", file=sys.stderr)
        sys.exit(1)
    if len(data) < 2:
        return []
    keys = data[0]
    return [dict(zip(keys, row)) for row in data[1:]]


def fmt_ts(ts):
    """Format CDX timestamp (YYYYMMDDHHmmss) to readable."""
    try:
        dt = datetime.strptime(ts[:14].ljust(14, '0'), "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts


def archive_url(ts, url):
    return f"{WEB_BASE}/{ts}/{url}"


def strip_html(text):
    """Basic HTML to text extraction."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.S | re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def cmd_snapshots(args):
    params = {"limit": args.limit, "collapse": "timestamp:6"}  # collapse to monthly
    if args.from_year:
        params["from"] = f"{args.from_year}0101"
    if args.to_year:
        params["to"] = f"{args.to_year}1231"
    snaps = cdx_query(args.url, params)
    if not snaps:
        print(f"No snapshots found for `{args.url}`.")
        return
    print(f"## Snapshots of `{args.url}` ({len(snaps)} results)\n")
    for s in snaps:
        ts = s["timestamp"]
        print(f"- **{fmt_ts(ts)}** | Status: {s['statuscode']} | [{s['original']}]({archive_url(ts, s['original'])})")


def cmd_closest(args):
    params = {"limit": 1, "sort": "closest"}
    if args.date:
        params["closest"] = args.date
        params["from"] = str(int(args.date[:4]) - 1)
        params["to"] = str(int(args.date[:4]) + 1)
    else:
        params["closest"] = datetime.now().strftime("%Y%m%d")
    snaps = cdx_query(args.url, params)
    if not snaps:
        print(f"No snapshot found near that date for `{args.url}`.")
        return
    s = snaps[0]
    ts = s["timestamp"]
    print(f"## Closest Snapshot of `{args.url}`\n")
    print(f"- **Date:** {fmt_ts(ts)}")
    print(f"- **Status:** {s['statuscode']}")
    print(f"- **Type:** {s['mimetype']}")
    print(f"- **URL:** [{s['original']}]({archive_url(ts, s['original'])})")


def cmd_fetch(args):
    # First find the closest snapshot
    params = {"limit": 1, "sort": "closest"}
    if args.date:
        params["closest"] = args.date
        params["from"] = str(int(args.date[:4]) - 1)
        params["to"] = str(int(args.date[:4]) + 1)
    else:
        params["closest"] = datetime.now().strftime("%Y%m%d")
    snaps = cdx_query(args.url, params)
    if not snaps:
        print(f"No snapshot found for `{args.url}`.")
        return
    s = snaps[0]
    ts = s["timestamp"]
    fetch_url = f"{WEB_BASE}/{ts}id_/{s['original']}"  # id_ = raw content
    print(f"## Archived Content: `{args.url}` ({fmt_ts(ts)})\n")
    print(f"**Source:** [{s['original']}]({archive_url(ts, s['original'])})")
    print(f"**Status:** {s['statuscode']} | **Type:** {s['mimetype']}\n")
    print("---\n")
    try:
        req = urllib.request.Request(fetch_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8", errors="replace")
        text = strip_html(content)
        # Truncate if huge
        if len(text) > 8000:
            text = text[:8000] + "\n\n*[Content truncated at 8000 chars]*"
        print(text)
    except Exception as e:
        print(f"**Error fetching content:** {e}")


def main():
    parser = argparse.ArgumentParser(description="Wayback Machine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_snap = sub.add_parser("snapshots", help="List snapshots of a URL")
    p_snap.add_argument("url")
    p_snap.add_argument("--limit", type=int, default=10)
    p_snap.add_argument("--from", dest="from_year", type=int)
    p_snap.add_argument("--to", dest="to_year", type=int)

    p_close = sub.add_parser("closest", help="Find closest snapshot to a date")
    p_close.add_argument("url")
    p_close.add_argument("--date", default=None, help="YYYYMMDD")

    p_fetch = sub.add_parser("fetch", help="Fetch archived page content")
    p_fetch.add_argument("url")
    p_fetch.add_argument("--date", default=None, help="YYYYMMDD")

    args = parser.parse_args()
    {"snapshots": cmd_snapshots, "closest": cmd_closest, "fetch": cmd_fetch}[args.command](args)


if __name__ == "__main__":
    main()
