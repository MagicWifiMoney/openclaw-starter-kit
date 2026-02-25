---
name: Reddit Search
description: Search Reddit posts and comments using the public JSON API. Find discussions, ideas, and community insights across any subreddit.
metadata:
  emoji: 🤖
  requires:
    - python3
    - requests
---

# Reddit Search

Search Reddit's public API for posts, comments, and discussions — no authentication required.

## Usage

### Search posts
```bash
python3 scripts/reddit_search.py search "query" [--subreddit sr] [--sort relevance|hot|new|top] [--time hour|day|week|month|year|all] [--limit 10]
```

### Browse a subreddit
```bash
python3 scripts/reddit_search.py browse "subreddit" [--sort hot|new|top|rising] [--time day|week|month|year|all] [--limit 10]
```

### Get a post + top comments
```bash
python3 scripts/reddit_search.py get "url_or_id" [--comments 10]
```

## Output

Clean markdown with: title, score, subreddit, author, URL, selftext preview, comment count.

## Examples

```bash
# Search all of Reddit
python3 scripts/reddit_search.py search "micro saas ideas"

# Search within a subreddit
python3 scripts/reddit_search.py search "side project" --subreddit SideProject --sort top --time month

# Get top posts from a subreddit
python3 scripts/reddit_search.py browse "startups" --sort top --time week

# Fetch a specific post with comments
python3 scripts/reddit_search.py get "https://reddit.com/r/SaaS/comments/abc123/my_post" --comments 5
```
