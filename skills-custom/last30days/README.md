# last30days

Research what people are saying about any topic across Reddit, X/Twitter, Hacker News, and developer communities from the last 30 days.

## What It Does

This skill searches multiple platforms to surface real community conversations, opinions, and sentiment:

- **Reddit** — Threads, comments, upvotes, community reactions
- **X/Twitter** — Real-time pulse, viral discussions
- **Hacker News** — Tech-savvy audience, substantive discussions
- **Stack Overflow** — Technical questions and answers
- **Dev.to** — Developer blog posts and articles
- **Lobsters** — Curated tech discussions

Results are weighted by engagement (upvotes, comments, points) to surface the most valuable signal.

## Setup

### Quick Start (Free Sources Only)

No setup needed! HN, Stack Overflow, Dev.to, and Lobsters work without API keys.

### Full Setup (Reddit + X)

Create `~/.config/last30days/.env`:

```bash
mkdir -p ~/.config/last30days
cat > ~/.config/last30days/.env << 'EOF'
# OpenAI API key (enables Reddit search via web browsing)
OPENAI_API_KEY=sk-...

# xAI API key (enables X/Twitter search via Grok)
XAI_API_KEY=xai-...
EOF
```

**Getting API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- xAI: https://console.x.ai/

## Usage

Ask natural questions like:

- "What are people saying about Cursor IDE?"
- "Research Claude vs GPT-4 for coding"
- "What's trending in AI agents?"
- "Community sentiment on React Server Components"
- "Best practices for prompting code assistants"

## Source Breakdown

| Source | API Key | Signal Type |
|--------|---------|-------------|
| Reddit | OpenAI (optional) | Community discussions, upvote-weighted |
| X/Twitter | xAI (optional) | Real-time, viral content |
| Hacker News | None | Tech discussions, points-weighted |
| Stack Overflow | None | Technical Q&A |
| Dev.to | None | Developer articles |
| Lobsters | None | Curated tech links |

## Scripts

### Main Research Script
```bash
python3 scripts/last30days.py "AI agents" --emit=json
```

### Hacker News Only
```bash
python3 scripts/hn_search.py "Cursor" --days 30
```

### Community Sources Only
```bash
./scripts/community_search.sh "React" all
```

## Output Example

```markdown
## Research: Cursor IDE (Last 30 Days)

### Key Themes
1. Tab completion is "magic" — multiple sources praise predictive editing
2. Claude integration preferred over GPT-4 for coding tasks
3. Composer feature getting mixed reviews (powerful but learning curve)

### Sentiment: Mostly Positive
- Praise: Speed, AI quality, tab completion
- Criticism: Price, occasional context loss, learning curve

### Top Discussions

**Reddit** (12 posts, 2.3k total upvotes)
- "Cursor vs Copilot after 30 days" — 847 upvotes

**Hacker News** (8 posts, 1.2k total points)
- "Cursor raises $60M Series A" — 342 points, 289 comments
```

## Credits

Based on [last30days-skill](https://github.com/mvanhorn/last30days-skill) by [@mvanhorn](https://github.com/mvanhorn).

## License

MIT
