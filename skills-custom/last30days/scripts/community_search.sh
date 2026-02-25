#!/bin/bash
#
# community_search.sh - Search community sources for recent discussions
#
# Usage:
#   ./community_search.sh "AI agents" [source]
#
# Sources: stackoverflow, devto, lobsters, all (default)
#
# Outputs JSON for each source to stdout.

set -e

TOPIC="${1:-}"
SOURCE="${2:-all}"

if [ -z "$TOPIC" ]; then
    echo "Usage: $0 <topic> [source]" >&2
    echo "Sources: stackoverflow, devto, lobsters, all" >&2
    exit 1
fi

# URL encode the topic
ENCODED_TOPIC=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TOPIC'))")

# Stack Overflow search
search_stackoverflow() {
    local url="https://api.stackexchange.com/2.3/search?order=desc&sort=activity&intitle=${ENCODED_TOPIC}&site=stackoverflow&pagesize=20&filter=withbody"
    
    local response
    response=$(curl -s --compressed -H "Accept: application/json" "$url" 2>/dev/null || echo '{"items":[]}')
    
    # Parse and format results
    echo "$response" | python3 -c '
import json
import sys
from datetime import datetime

try:
    data = json.load(sys.stdin)
    items = data.get("items", [])
    results = []
    for item in items[:20]:
        creation_date = item.get("creation_date", 0)
        date_str = datetime.utcfromtimestamp(creation_date).strftime("%Y-%m-%d") if creation_date else ""
        results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "score": item.get("score", 0),
            "answers": item.get("answer_count", 0),
            "views": item.get("view_count", 0),
            "author": item.get("owner", {}).get("display_name", ""),
            "date": date_str,
            "tags": item.get("tags", []),
            "source": "stackoverflow"
        })
    print(json.dumps(results, indent=2))
except Exception as e:
    print("[]")
'
}

# Dev.to search
search_devto() {
    local url="https://dev.to/api/articles?per_page=20&tag=${ENCODED_TOPIC}"
    
    local response
    response=$(curl -s -H "Accept: application/json" "$url" 2>/dev/null || echo '[]')
    
    # Parse and format results
    echo "$response" | python3 -c '
import json
import sys

try:
    data = json.load(sys.stdin)
    if not isinstance(data, list):
        data = []
    results = []
    for item in data[:20]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "reactions": item.get("positive_reactions_count", 0),
            "comments": item.get("comments_count", 0),
            "author": item.get("user", {}).get("name", ""),
            "date": item.get("published_at", "")[:10] if item.get("published_at") else "",
            "tags": item.get("tag_list", []),
            "reading_time": item.get("reading_time_minutes", 0),
            "source": "devto"
        })
    print(json.dumps(results, indent=2))
except Exception as e:
    print("[]")
'
}

# Lobsters search (via RSS/JSON - Lobsters doesn't have a search API, so we use tags)
search_lobsters() {
    # Lobsters uses tags, try to find relevant tag
    local tag=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | head -c 20)
    local url="https://lobste.rs/t/${tag}.json"
    
    local response
    response=$(curl -s -H "Accept: application/json" "$url" 2>/dev/null || echo '[]')
    
    # Parse and format results
    echo "$response" | python3 -c '
import json
import sys

try:
    data = json.load(sys.stdin)
    if not isinstance(data, list):
        data = []
    results = []
    for item in data[:20]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", "") or item.get("comments_url", ""),
            "score": item.get("score", 0),
            "comments": item.get("comment_count", 0),
            "author": item.get("submitter_user", {}).get("username", ""),
            "date": item.get("created_at", "")[:10] if item.get("created_at") else "",
            "tags": item.get("tags", []),
            "lobsters_url": item.get("comments_url", ""),
            "source": "lobsters"
        })
    print(json.dumps(results, indent=2))
except Exception as e:
    print("[]")
'
}

# Output wrapper
output_source() {
    local source_name="$1"
    local data="$2"
    echo "{"
    echo "  \"source\": \"$source_name\","
    echo "  \"results\": $data"
    echo "}"
}

# Main execution
case "$SOURCE" in
    stackoverflow|so)
        search_stackoverflow
        ;;
    devto|dev)
        search_devto
        ;;
    lobsters|lob)
        search_lobsters
        ;;
    all)
        echo "{"
        echo "  \"stackoverflow\": $(search_stackoverflow),"
        echo "  \"devto\": $(search_devto),"
        echo "  \"lobsters\": $(search_lobsters)"
        echo "}"
        ;;
    *)
        echo "Unknown source: $SOURCE" >&2
        echo "Available: stackoverflow, devto, lobsters, all" >&2
        exit 1
        ;;
esac
