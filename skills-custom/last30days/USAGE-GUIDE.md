# last30days - Usage Guide

## What It Does

**last30days** searches community discussions from the past 30 days to surface:
- Real pain points and problems
- Feature requests and complaints
- Trending topics and sentiment
- Technical challenges and solutions
- Competitor intelligence
- Content validation (is anyone talking about this?)

**vs web_search**: web_search finds facts, documentation, and general info. last30days finds **what people are actually saying**, weighted by engagement (upvotes, comments).

## When to Use It

### ✅ Perfect For:
- **Pain point mining**: "What are real estate agents complaining about with their CRM?"
- **Content validation**: "Is anyone discussing X? What angle resonates?"
- **Competitor research**: "What do people say about [competitor]?"
- **Trend spotting**: "What's trending in [niche]?"
- **Technical debugging**: "What issues are people having with [technology]?"

### ❌ NOT For:
- Facts or definitions (use web_search)
- Official documentation (use web_search)
- Historical data >30 days old
- Topics with no community discussion

## Source Breakdown

| Source | Best For | Speed | API Key Required | Quality (1-10) |
|--------|----------|-------|------------------|----------------|
| **Hacker News** | Tech/startup trends, developer sentiment | ⚡ Fast | ❌ No | 9/10 |
| **Stack Overflow** | Technical pain points, common errors | ⚡ Fast | ❌ No | 8/10 |
| **Reddit** | Consumer sentiment, niche communities | 🐌 Slow | ✅ OpenAI | 7-9/10 (variable) |
| **Dev.to** | Developer tutorials, trending topics | ⚡ Fast | ❌ No | 6/10 |
| **Lobsters** | Curated tech discussions | ⚡ Fast | ❌ No | 7/10 |

### Source Notes:

**Hacker News** (ALWAYS USE)
- FREE, fast, high signal-to-noise
- Best for: Tech products, startups, developer tools
- Engagement-weighted (points + comments)
- 30-day filter works perfectly

**Stack Overflow** (GREAT FOR TECHNICAL)
- FREE, technical depth
- Best for: Common errors, implementation challenges
- Note: May return results older than 30 days (API limitation)
- Use for: "What problems are developers having with X?"

**Reddit** (HIGH QUALITY BUT SLOW)
- Requires OpenAI API key
- **⚠️ SLOW** - Can timeout 50%+ of the time (see Gotchas)
- Best for: Consumer sentiment, emotional pain points, niche communities
- When it works: 9/10 quality, engagement-weighted
- Fallback: If timeout, use HN + SO for 90% of research value

**Dev.to** (INCONSISTENT)
- FREE but results can be spotty
- Best for: Tutorial trends, beginner content
- May return empty for some queries

**Lobsters** (NICHE)
- FREE, curated tech community
- Smaller but high-quality discussions
- Good supplement to HN

## Query Optimization

### Sweet Spot Pattern:
`[specific niche] + [general problem]`

### Examples:

✅ **Good Queries:**
- "real estate agents CRM challenges"
- "freelance developers invoicing pain"
- "Shopify store owners email marketing"
- "Next.js hydration errors"

❌ **Too Broad:**
- "small business software" (too much noise)
- "web development" (no focus)

❌ **Too Specific:**
- "Next.js 15.0.3 hydration error in production with Tailwind" (no results)

### Pro Tips:
1. Start with niche + problem pattern
2. If no results → broaden the problem part
3. Include tool/technology name when relevant
4. Avoid version numbers unless debugging specific issue

## Example Workflows

### 1. Pain Point Mining
```bash
# Find buildable problems
python3 scripts/hn_search.py "SaaS founders analytics" --days 30 --limit 30
```

Look for:
- Repeated complaints
- High engagement (points + comments)
- Specific feature requests
- "I wish X existed" patterns

### 2. Competitor Intelligence
```bash
# What are people saying about competitor?
python3 scripts/last30days.py "Competitor Name" --quick --emit=compact
```

Extract:
- Common complaints
- Feature gaps
- Pricing frustrations
- Integration requests

### 3. Content Validation
```bash
# Is this topic worth writing about?
python3 scripts/hn_search.py "topic keyword" --days 30
```

Validate:
- Recent discussions (last 30 days)
- Engagement level (points + comments)
- Unanswered questions
- Trending angles

### 4. Trend Spotting
```bash
# What's trending in niche?
python3 scripts/last30days.py "AI coding tools" --emit=json
```

Identify:
- Emerging tools/techniques
- Shifting sentiment
- New use cases
- Community reactions

## Integration Examples

### Morning Dashboard Cron
Add pain point discovery to daily dashboard:

```javascript
// In morning dashboard script
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function getTrendingPainPoints() {
  try {
    const { stdout } = await execPromise(
      'cd /home/ec2-user/clawd/skills/last30days && python3 scripts/hn_search.py "SaaS founders" --days 7 --limit 10'
    );
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Pain point search failed:', error);
    return [];
  }
}
```

### Content Research
Find what's resonating before creating content:

```bash
# Research before writing
cd /home/ec2-user/clawd/skills/last30days

# Check if topic is trending
python3 scripts/hn_search.py "your topic" --days 30

# Find unanswered questions
bash scripts/community_search.sh "your topic" stackoverflow

# Validate with Reddit (if you have time)
python3 scripts/last30days.py "your topic" --sources=reddit --quick
```

### Weekly Competitor Audit
Monitor what people say about competitors:

```bash
#!/bin/bash
# weekly-competitor-audit.sh

COMPETITORS=("competitor1" "competitor2" "competitor3")

for comp in "${COMPETITORS[@]}"; do
  echo "=== $comp ==="
  python3 scripts/hn_search.py "$comp" --days 7 --limit 20
  echo ""
done
```

## Gotchas & Limitations

### Reddit Timeouts (CRITICAL)
- **Problem**: Reddit searches via OpenAI frequently timeout (50%+ failure rate)
- **Cause**: OpenAI web search is slow when fetching full thread details
- **Solution**: Use HN + SO for 90% of research value, only use Reddit when consumer sentiment is critical
- **Fallback**: If Reddit times out, proceed with HN + SO results
- **When to use**: Allow 60+ seconds, only for high-value consumer insights

### Stack Overflow Date Range
- API doesn't perfectly filter to 30 days
- May return older but highly relevant results
- Still useful for common pain points

### Dev.to / Lobsters
- Smaller communities = fewer results
- Good for niche topics but may return empty
- Don't rely on these as primary sources

### API Keys
- **Required**: OPENAI_API_KEY for Reddit
- **Optional**: XAI_API_KEY for Twitter/X (not yet implemented)
- **Free**: HN, SO, Dev.to, Lobsters always work

### Query Specificity
- Too specific = no results
- Too broad = too much noise
- Aim for 2-4 word focused queries

## Command Reference

### last30days.py (Reddit + Twitter)
```bash
cd /home/ec2-user/clawd/skills/last30days

# Quick research (fewer results, faster)
python3 scripts/last30days.py "topic" --quick --emit=compact

# Deep research (comprehensive)
python3 scripts/last30days.py "topic" --deep --emit=json

# Reddit only (when consumer sentiment matters)
python3 scripts/last30days.py "topic" --sources=reddit --quick

# Twitter only (when XAI key available)
python3 scripts/last30days.py "topic" --sources=x
```

### hn_search.py (Hacker News)
```bash
# Standard search (30 days, 20 results)
python3 scripts/hn_search.py "topic" --days 30 --limit 20

# Recent trends (7 days)
python3 scripts/hn_search.py "topic" --days 7 --limit 50

# Output JSON for processing
python3 scripts/hn_search.py "topic" --days 30 --limit 20 > results.json
```

### community_search.sh (SO, Dev.to, Lobsters)
```bash
# All sources
bash scripts/community_search.sh "topic" all

# Stack Overflow only
bash scripts/community_search.sh "topic" stackoverflow

# Dev.to only
bash scripts/community_search.sh "topic" devto

# Lobsters only
bash scripts/community_search.sh "topic" lobsters
```

## Recommended Workflow

### For Most Research Tasks:
1. **Start with HN** (fast, high quality, always works)
   ```bash
   python3 scripts/hn_search.py "topic" --days 30 --limit 30
   ```

2. **Add SO for technical depth**
   ```bash
   bash scripts/community_search.sh "topic" stackoverflow
   ```

3. **Only add Reddit if:**
   - You need consumer/SMB sentiment
   - You have 60+ seconds to wait
   - HN + SO didn't provide enough context

### Source Selection by Use Case:

| Use Case | Primary | Secondary | Skip |
|----------|---------|-----------|------|
| Tech product validation | HN | SO, Reddit | Dev.to |
| Pain point mining | HN | SO | Lobsters |
| Consumer sentiment | Reddit | HN | Dev.to |
| Technical debugging | SO | HN | Dev.to |
| Content ideas | HN | Reddit | All others |
| Competitor intel | HN | Reddit | SO |

## Success Metrics

Good research provides:
- ✅ 10+ relevant discussions with engagement
- ✅ Specific pain points you can quote
- ✅ Clear sentiment (positive/negative/mixed)
- ✅ Actionable insights (build X, write about Y)

If you're getting:
- ❌ <5 results → Query too specific, broaden it
- ❌ No engagement → Topic not discussed, pivot
- ❌ All old results → Use web_search for facts instead
- ❌ Noise/spam → Add more specific niche qualifier

## Integration Checklist

Before using in production:
- [ ] Understand timeout behavior (Reddit is slow)
- [ ] Have fallback logic (HN + SO if Reddit fails)
- [ ] Set reasonable timeouts (60s minimum for Reddit)
- [ ] Handle empty results gracefully
- [ ] Weight HN results higher than others
- [ ] Cache results when possible (API calls aren't free)

## Quick Decision Tree

```
Need research? → last30days or web_search?
├─ Facts/docs/definitions → web_search
├─ "What are people saying?" → last30days
   ├─ Tech/startup/dev → Start with HN
   ├─ Consumer/SMB → Start with HN, add Reddit if time
   ├─ Technical issue → Start with SO
   └─ Content validation → HN → assess engagement
```

---

**Last updated**: Feb 6, 2026
**Maintained by**: Botti
**Location**: `/home/ec2-user/clawd/skills/last30days/`
