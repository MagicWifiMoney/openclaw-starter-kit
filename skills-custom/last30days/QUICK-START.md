# last30days Skill - Quick Start Cheat Sheet

**Status:** Production Ready ✅  
**Quality:** ⭐⭐⭐⭐ 8/10

---

## 30-Second Start

```bash
# Find pain points in any niche
/home/ec2-user/clawd/scripts/research-pain-points.sh "your niche here"

# Research competitors
/home/ec2-user/clawd/scripts/research-competitors.sh "competitor name"

# Validate content topics
/home/ec2-user/clawd/scripts/research-content-ideas.sh "topic"
```

---

## When to Use

| ✅ Use last30days for | ❌ Use web_search for |
|----------------------|---------------------|
| Community sentiment | Facts & definitions |
| Pain point discovery | Company information |
| Trend detection | Recent news (<24hrs) |
| Competitor research | Documentation |
| Content validation | Historical info (>30 days) |

---

## Data Sources

| Source | Quality | API Key? | Best For |
|--------|---------|----------|----------|
| **Hacker News** | ⭐⭐⭐⭐⭐ 10/10 | ❌ Free | Tech trends, AI tools |
| **Reddit** | ⭐⭐⭐⭐⭐ 9/10 | ✅ OpenAI | Sentiment, pain points |
| **Stack Overflow** | ⭐⭐⭐⭐ 8/10 | ❌ Free | Technical issues |
| **Dev.to** | ⭐⭐ 4/10 | ❌ Free | ⚠️ BROKEN - skip |
| **Lobsters** | ⭐ 2/10 | ❌ Free | ⚠️ BROKEN - skip |

---

## Example Queries

### Pain Point Research
```bash
research-pain-points.sh "small business owners"
research-pain-points.sh "real estate agents"
research-pain-points.sh "freelance developers"
```

### Competitor Intelligence
```bash
research-competitors.sh "GoHighLevel"
research-competitors.sh "Cursor IDE"
research-competitors.sh "Vercel"
```

### Content Validation
```bash
research-content-ideas.sh "AI automation"
research-content-ideas.sh "local SEO"
research-content-ideas.sh "Next.js"
```

---

## Direct Access (Advanced)

```bash
# Hacker News only (fastest)
cd /home/ec2-user/clawd/skills/last30days
python3 scripts/hn_search.py "Claude AI" --days 30 --limit 20

# Reddit only (requires OPENAI_API_KEY)
python3 scripts/last30days.py "topic" --sources=reddit --emit=json

# All sources
python3 scripts/last30days.py "topic" --emit=json
```

---

## Query Tips

### ✅ Good Queries
- Specific niche + general pain: "real estate agents task management"
- Natural language: "What are people saying about Cursor?"
- Product names: "GoHighLevel complaints"

### ❌ Bad Queries
- Too broad: "tech" or "small business"
- Too narrow: "Next.js 15.0.3 hydration error in production with SSR"
- Old topics: Anything >30 days (not the skill's purpose)

---

## Top Findings

**Best Opportunity Discovered:**
- **AI Search Visibility for Local Businesses** (9/10 build score)
- Market: $5-10B TAM
- Competition: Greenfield 🟢
- Pain: 92% of local businesses invisible in AI search results

See `PAIN-POINTS-ANALYSIS.md` for full details.

---

## Automation

**Weekly Research Digest**
- Runs: Sunday 2pm (cron)
- Output: `/tmp/weekly-research-digest-YYYY-MM-DD.md`
- Topics: AI agents, local SEO, small business automation, Next.js, Claude AI, GoHighLevel alternatives

---

## File Locations

**Helper Scripts:**
- `/home/ec2-user/clawd/scripts/research-pain-points.sh`
- `/home/ec2-user/clawd/scripts/research-competitors.sh`
- `/home/ec2-user/clawd/scripts/research-content-ideas.sh`
- `/home/ec2-user/clawd/scripts/weekly-research-digest.sh`

**Documentation:**
- `USAGE-GUIDE.md` - Full how-to guide
- `TEST-RESULTS.md` - Data source quality
- `PAIN-POINTS-ANALYSIS.md` - Research findings
- `INTEGRATION-COMPLETE.md` - Final summary
- `QUICK-START.md` - This file

**Core Scripts:**
- `/home/ec2-user/clawd/skills/last30days/scripts/hn_search.py`
- `/home/ec2-user/clawd/skills/last30days/scripts/last30days.py`
- `/home/ec2-user/clawd/skills/last30days/scripts/community_search.sh`

---

## Setup API Keys (Optional)

For Reddit access, create `~/.config/last30days/.env`:

```bash
OPENAI_API_KEY=sk-your-key-here
```

Without this, you'll still have Hacker News + Stack Overflow (plenty of value!).

---

## Common Use Cases

**Before building anything:**
```bash
# Validate the pain exists
research-pain-points.sh "target niche"

# Check existing solutions
research-competitors.sh "competitor"
```

**Weekly content planning:**
```bash
research-content-ideas.sh "blog topic"
```

**Competitor monitoring:**
```bash
research-competitors.sh "competitor" | tee /tmp/competitor-weekly.txt
```

**Pre-meeting research:**
```bash
research-pain-points.sh "meeting topic/client industry"
```

---

## Troubleshooting

**No results?**
- Try broader query
- Check if topic discussed in last 30 days
- Try different phrasing

**Old results (>30 days)?**
- Known issue with Stack Overflow
- Focus on HN/Reddit instead

**API errors?**
- Check `~/.config/last30days/.env` exists
- Verify OPENAI_API_KEY is set
- Fall back to free sources (HN, SO)

---

## Next Steps

1. **Try it now** - Pick a topic and run a helper script
2. **Add to workflow** - Integrate into morning routine
3. **Validate ideas** - Use before building anything new

**Questions?** See `USAGE-GUIDE.md` for comprehensive details.

---

*Last updated: 2026-02-06*
