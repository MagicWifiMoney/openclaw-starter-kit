#!/usr/bin/env python3
"""
IP Intel Digest - Query PostHog for enriched visitor data.
Filters out consumer ISPs, surfaces interesting orgs, optionally alerts to Discord.

Usage:
  python3 digest.py
  python3 digest.py --days 7
  python3 digest.py --output json

Requirements: pip install requests
Env vars:
  POSTHOG_API_KEY    - PostHog personal API key (Settings > Personal API Keys)
  POSTHOG_PROJECT_ID - Your project ID (in PostHog URL)
  DISCORD_WEBHOOK_URL - optional, for alerts
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime, timedelta, timezone
from collections import defaultdict

try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

# ─── Config ────────────────────────────────────────────────────────────────────

POSTHOG_API_KEY    = os.environ.get("POSTHOG_API_KEY", "")
POSTHOG_PROJECT_ID = os.environ.get("POSTHOG_PROJECT_ID", "")
POSTHOG_HOST       = os.environ.get("POSTHOG_HOST", "https://us.posthog.com")
DISCORD_WEBHOOK    = os.environ.get("DISCORD_WEBHOOK_URL", "")

# Consumer ISPs to filter out (noise)
CONSUMER_ISP_PATTERNS = [
    r"comcast", r"charter", r"spectrum", r"cox ", r"at&t", r"verizon",
    r"t-mobile", r"centurylink", r"lumen", r"frontier", r"optimum",
    r"xfinity", r"cablevision", r"mediacom", r"windstream", r"earthlink",
    r"sprint", r"boost", r"cricket", r"metro pcs",
    r"residential", r"broadband", r"fiber", r"dsl", r"cable",
    r"amazon ", r"aws", r"google llc", r"microsoft corp",  # cloud IPs, not companies
    r"digitalocean", r"linode", r"vultr", r"hetzner",
    r"cloudflare", r"fastly", r"akamai",
]

# High-value org signals for VastVision's ICP
HIGH_VALUE_SIGNALS = [
    # Defense / Gov
    r"department of", r"dept\.", r"federal", r"government", r"army", r"navy",
    r"air force", r"marine", r"pentagon", r"dod", r"defense", r"intelligence",
    r"nasa", r"noaa", r"usgs", r"nist",
    # Defense contractors
    r"lockheed", r"boeing", r"raytheon", r"northrop", r"general dynamics",
    r"l3harris", r"bae systems", r"leidos", r"saic", r"booz allen",
    r"mitre", r"rand corp",
    # Energy
    r"energy", r"utility", r"electric", r"nuclear", r"solar", r"grid",
    r"chevron", r"exxon", r"bp ", r"shell ", r"schlumberger",
    # Research / Universities
    r"university", r"college", r"institute", r"laboratory", r"research",
    r"mit ", r"stanford", r"johns hopkins",
    # Industrial / Supply chain
    r"logistics", r"supply chain", r"warehouse", r"manufacturing",
    r"caterpillar", r"honeywell", r"ge ", r"siemens", r"abb ",
]


def is_consumer(org: str) -> bool:
    org_lower = org.lower()
    return any(re.search(pat, org_lower) for pat in CONSUMER_ISP_PATTERNS)


def is_high_value(org: str) -> bool:
    org_lower = org.lower()
    return any(re.search(pat, org_lower) for pat in HIGH_VALUE_SIGNALS)


def fetch_posthog_events(days: int) -> list:
    if not POSTHOG_API_KEY or not POSTHOG_PROJECT_ID:
        print("ERROR: Set POSTHOG_API_KEY and POSTHOG_PROJECT_ID env vars")
        sys.exit(1)

    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    url   = f"{POSTHOG_HOST}/api/projects/{POSTHOG_PROJECT_ID}/events/"
    headers = {"Authorization": f"Bearer {POSTHOG_API_KEY}"}
    params  = {
        "event": "ip_enriched",
        "after": since,
        "limit": 1000,
    }

    all_events = []
    while url:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        all_events.extend(data.get("results", []))
        url = data.get("next")
        params = {}  # next URL already has params

    return all_events


def build_org_summary(events: list) -> dict:
    """Group events by org, track pages visited, first/last seen."""
    orgs = defaultdict(lambda: {
        "org": "",
        "asn": "",
        "city": "",
        "country": "",
        "visit_count": 0,
        "pages": set(),
        "first_seen": None,
        "last_seen": None,
        "high_value": False,
    })

    for ev in events:
        props = ev.get("properties", {})
        org   = props.get("ip_org", "Unknown")
        if not org or org == "Unknown":
            continue
        if is_consumer(org):
            continue

        rec = orgs[org]
        rec["org"]       = org
        rec["asn"]       = props.get("ip_asn", "")
        rec["city"]      = props.get("ip_city", "")
        rec["country"]   = props.get("ip_country", "")
        rec["visit_count"] += 1
        rec["pages"].add(props.get("page_path", "/"))
        rec["high_value"] = is_high_value(org)

        ts = ev.get("timestamp") or ev.get("created_at")
        if ts:
            if not rec["first_seen"] or ts < rec["first_seen"]:
                rec["first_seen"] = ts
            if not rec["last_seen"] or ts > rec["last_seen"]:
                rec["last_seen"] = ts

    # Convert sets to sorted lists
    for org in orgs:
        orgs[org]["pages"] = sorted(orgs[org]["pages"])

    return dict(orgs)


def format_digest(summary: dict, days: int) -> str:
    if not summary:
        return f"No identifiable org traffic in last {days} days."

    high_value = {k: v for k, v in summary.items() if v["high_value"]}
    regular    = {k: v for k, v in summary.items() if not v["high_value"]}

    lines = [f"**IP Intel Digest - Last {days} days**", ""]

    if high_value:
        lines.append(f"**High-Value Visitors ({len(high_value)})**")
        for org, rec in sorted(high_value.items(), key=lambda x: -x[1]["visit_count"]):
            pages = ", ".join(rec["pages"][:3])
            lines.append(f"  - **{org}** ({rec['city']}, {rec['country']}) - {rec['visit_count']} visits - Pages: {pages}")
        lines.append("")

    if regular:
        lines.append(f"**Other Orgs ({len(regular)})**")
        for org, rec in sorted(regular.items(), key=lambda x: -x[1]["visit_count"])[:20]:
            lines.append(f"  - {org} ({rec['city']}) - {rec['visit_count']} visits")
        lines.append("")

    lines.append(f"Total unique orgs: {len(summary)} | High-value: {len(high_value)}")
    return "\n".join(lines)


def send_discord(message: str):
    if not DISCORD_WEBHOOK:
        return
    # Discord has a 2000 char limit per message
    chunks = [message[i:i+1900] for i in range(0, len(message), 1900)]
    for chunk in chunks:
        requests.post(DISCORD_WEBHOOK, json={"content": chunk}, timeout=10)


def main():
    parser = argparse.ArgumentParser(description="IP Intel digest from PostHog")
    parser.add_argument("--days",   type=int, default=7,       help="Days to look back (default: 7)")
    parser.add_argument("--output", choices=["text","json"],   default="text")
    parser.add_argument("--alert",  action="store_true",       help="Send to Discord webhook")
    args = parser.parse_args()

    print(f"Fetching ip_enriched events from PostHog (last {args.days} days)...")
    events  = fetch_posthog_events(args.days)
    print(f"  Got {len(events)} events")

    summary = build_org_summary(events)

    if args.output == "json":
        print(json.dumps(summary, indent=2, default=str))
        return

    digest = format_digest(summary, args.days)
    print(digest)

    if args.alert and DISCORD_WEBHOOK:
        send_discord(digest)
        print("Sent to Discord.")


if __name__ == "__main__":
    main()
