#!/usr/bin/env python3
"""Reddit Search — query Reddit's public JSON API (no auth needed)."""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.parse
import html

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fetch_json(url):
    """Fetch JSON from a URL with Reddit-friendly headers."""
    # Use old.reddit.com to avoid blocks on cloud IPs
    url = url.replace("https://www.reddit.com/", "https://old.reddit.com/")
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)


def decode(text):
    """Decode HTML entities and clean up text."""
    if not text:
        return ""
    return html.unescape(text).replace("\n", " ").strip()


def format_post(post, index=None):
    """Format a single post as markdown."""
    d = post["data"] if "data" in post else post
    title = decode(d.get("title", "(no title)"))
    score = d.get("score", 0)
    sub = d.get("subreddit", "?")
    author = d.get("author", "[deleted]")
    permalink = d.get("permalink", "")
    url = f"https://reddit.com{permalink}" if permalink else d.get("url", "")
    selftext = decode(d.get("selftext", ""))
    preview = (selftext[:200] + "…") if len(selftext) > 200 else selftext
    comments = d.get("num_comments", 0)
    prefix = f"**{index}.** " if index else ""

    lines = [
        f"{prefix}**{title}**",
        f"   ⬆ {score} | r/{sub} | u/{author} | 💬 {comments}",
        f"   {url}",
    ]
    if preview:
        lines.append(f"   > {preview}")
    lines.append("")
    return "\n".join(lines)


def format_comment(comment, depth=0):
    """Format a comment with indentation for depth."""
    d = comment.get("data", comment)
    if d.get("body") is None:
        return ""
    author = d.get("author", "[deleted]")
    score = d.get("score", 0)
    body = decode(d.get("body", ""))
    preview = (body[:300] + "…") if len(body) > 300 else body
    indent = "  " * depth
    return f"{indent}**u/{author}** (⬆ {score})\n{indent}> {preview}\n"


def cmd_search(args):
    """Search Reddit posts."""
    params = {
        "q": args.query,
        "sort": args.sort,
        "t": args.time,
        "limit": str(args.limit),
        "restrict_sr": "",
        "type": "link",
    }
    if args.subreddit:
        base = f"https://www.reddit.com/r/{args.subreddit}/search.json"
        params["restrict_sr"] = "on"
    else:
        base = "https://www.reddit.com/search.json"

    url = f"{base}?{urllib.parse.urlencode(params)}"
    data = fetch_json(url)
    posts = data.get("data", {}).get("children", [])

    if not posts:
        print("No results found.")
        return

    q = args.query
    sub_info = f" in r/{args.subreddit}" if args.subreddit else ""
    print(f"## Reddit Search: \"{q}\"{sub_info}\n")
    for i, post in enumerate(posts, 1):
        print(format_post(post, i))


def cmd_browse(args):
    """Browse a subreddit's posts."""
    sort = args.sort
    params = {"limit": str(args.limit)}
    if sort == "top":
        params["t"] = args.time
    url = f"https://www.reddit.com/r/{args.subreddit}/{sort}.json?{urllib.parse.urlencode(params)}"
    data = fetch_json(url)
    posts = data.get("data", {}).get("children", [])

    if not posts:
        print("No posts found.")
        return

    print(f"## r/{args.subreddit} — {sort}\n")
    for i, post in enumerate(posts, 1):
        print(format_post(post, i))


def cmd_get(args):
    """Get a specific post + top comments."""
    url_or_id = args.url_or_id

    # Parse URL or construct one from ID
    if url_or_id.startswith("http"):
        # Strip trailing slash, add .json
        clean = url_or_id.rstrip("/")
        clean = re.sub(r'\.json$', '', clean)
        json_url = clean + ".json"
    else:
        # Assume it's a post ID (e.g., t3_abc123 or just abc123)
        pid = url_or_id.replace("t3_", "")
        json_url = f"https://www.reddit.com/comments/{pid}.json"

    data = fetch_json(json_url)

    if not isinstance(data, list) or len(data) < 1:
        print("Could not parse post data.")
        return

    # Post info
    post = data[0]["data"]["children"][0]
    d = post["data"]
    title = decode(d.get("title", ""))
    score = d.get("score", 0)
    sub = d.get("subreddit", "?")
    author = d.get("author", "[deleted]")
    selftext = decode(d.get("selftext", ""))
    permalink = d.get("permalink", "")
    post_url = f"https://reddit.com{permalink}"
    num_comments = d.get("num_comments", 0)

    print(f"## {title}\n")
    print(f"⬆ {score} | r/{sub} | u/{author} | 💬 {num_comments}")
    print(f"{post_url}\n")
    if selftext:
        print(f"{selftext[:1000]}\n")

    # Comments
    if len(data) >= 2:
        comments = data[1]["data"]["children"]
        limit = args.comments
        print(f"---\n### Top Comments ({min(limit, len(comments))})\n")
        count = 0
        for c in comments:
            if c.get("kind") != "t1":
                continue
            print(format_comment(c))
            count += 1
            if count >= limit:
                break


def main():
    parser = argparse.ArgumentParser(description="Reddit Search CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Search Reddit posts")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--subreddit", "-s", help="Restrict to subreddit")
    p_search.add_argument("--sort", default="relevance", choices=["relevance", "hot", "new", "top", "comments"])
    p_search.add_argument("--time", "-t", default="all", choices=["hour", "day", "week", "month", "year", "all"])
    p_search.add_argument("--limit", "-l", type=int, default=10)

    # browse
    p_browse = sub.add_parser("browse", help="Browse subreddit posts")
    p_browse.add_argument("subreddit", help="Subreddit name")
    p_browse.add_argument("--sort", default="hot", choices=["hot", "new", "top", "rising"])
    p_browse.add_argument("--time", "-t", default="week", choices=["hour", "day", "week", "month", "year", "all"])
    p_browse.add_argument("--limit", "-l", type=int, default=10)

    # get
    p_get = sub.add_parser("get", help="Get post + comments")
    p_get.add_argument("url_or_id", help="Reddit URL or post ID")
    p_get.add_argument("--comments", "-c", type=int, default=10)

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "browse":
        cmd_browse(args)
    elif args.command == "get":
        cmd_get(args)


if __name__ == "__main__":
    main()
