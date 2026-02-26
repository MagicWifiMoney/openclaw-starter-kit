---
name: wayback
description: "Search and retrieve archived web pages from the Wayback Machine. Use when: checking how a website looked in the past, finding old versions of pages, comparing website changes over time, retrieving content from deleted pages, researching website history. DON'T use when: browsing current/live websites (use browser), checking if a site is currently down (use web_fetch)."
user-invocable: true
disable-model-invocation: false
allowed-tools: ["Bash(python3 ~/clawd/skills/wayback/scripts/wayback.py *)"]
---

# Wayback Machine

Query the Internet Archive's Wayback Machine to find archived snapshots of any URL. Uses the free CDX API (no authentication required).

## Commands

### List Snapshots
Get a list of archived snapshots for a URL over time:
```bash
python3 ~/clawd/skills/wayback/scripts/wayback.py snapshots "example.com" --limit 10 --from 2020 --to 2024
```

### Closest Snapshot
Find the snapshot nearest to a specific date:
```bash
python3 ~/clawd/skills/wayback/scripts/wayback.py closest "example.com" --date 20240101
```

### Fetch Archived Content
Retrieve and extract text content from an archived page:
```bash
python3 ~/clawd/skills/wayback/scripts/wayback.py fetch "example.com" --date 20240101
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--limit N` | Max number of snapshots to return | 10 |
| `--from YYYY` | Start year filter | (none) |
| `--to YYYY` | End year filter | (none) |
| `--date YYYYMMDD` | Target date for closest/fetch | today |

## Output

All output is clean markdown. Snapshots include timestamp, archived URL, HTTP status code, and MIME type. Fetch mode additionally extracts readable text content from the archived page.

## Examples

- "How did producthunt.com look in 2015?" → `snapshots "producthunt.com" --from 2015 --to 2015`
- "Get the oldest snapshot of ycombinator.com" → `snapshots "ycombinator.com" --limit 1`
- "What was on example.com on Jan 1 2020?" → `fetch "example.com" --date 20200101`
