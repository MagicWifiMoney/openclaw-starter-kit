---
name: gov-intel
description: Government competitive intelligence — combines SAM.gov, USASpending, SBIR, and Grants.gov data for market analysis, competitor tracking, and opportunity scoring. Use when doing competitive research, market sizing, win/loss analysis, or building pipeline reports.
---

# Government Competitive Intelligence

Combines all government data sources into actionable intelligence for your company's BD pipeline. This is the "connect the dots" skill.

## Quick Commands

### Who's winning in our space?

```bash
# Top 10 winners in your company's NAICS codes (last 12 months)
FROM=$(date -d "12 months ago" +%Y-%m-%d)
TO=$(date +%Y-%m-%d)

curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_category/recipient/" \
  -H "Content-Type: application/json" \
  -d "{
    \"filters\": {
      \"time_period\": [{\"start_date\": \"$FROM\", \"end_date\": \"$TO\"}],
      \"naics_codes\": {\"require\": [\"334515\", \"334519\", \"541715\"]}
    },
    \"limit\": 10
  }" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Top recipients by award amount:')
for r in data.get('results', []):
    name = r.get('name', 'Unknown')
    amount = r.get('amount', 0)
    count = r.get('count', 0)
    print(f'  {name}: \${amount:,.0f} ({count} awards)')
"
```

### What's the total market size?

```bash
# Total spending by NAICS (last fiscal year)
curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_category/naics/" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "time_period": [{"start_date": "2025-01-01", "end_date": "2026-02-20"}],
      "naics_codes": {"require": ["334515", "334519", "541330", "541715", "541712"]}
    },
    "limit": 10
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
total = sum(r.get('amount', 0) for r in data.get('results', []))
print(f'Total addressable market (gov contracts): \${total:,.0f}')
for r in data.get('results', []):
    print(f'  NAICS {r.get(\"code\", \"?\")}: \${r.get(\"amount\", 0):,.0f} ({r.get(\"count\", 0)} awards)')
"
```

### Which agencies spend the most?

```bash
curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_category/awarding_agency/" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "time_period": [{"start_date": "2025-01-01", "end_date": "2026-02-20"}],
      "naics_codes": {"require": ["334515", "334519", "541715"]}
    },
    "limit": 10
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Top awarding agencies:')
for r in data.get('results', []):
    print(f'  {r.get(\"name\", \"Unknown\")}: \${r.get(\"amount\", 0):,.0f} ({r.get(\"count\", 0)} awards)')
"
```

### Deep dive on a competitor

```bash
COMPETITOR="COMPANY_NAME"

echo "=== $COMPETITOR — Federal Footprint ==="

# Recent contracts
echo "--- Recent Contract Awards ---"
curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_award/" \
  -H "Content-Type: application/json" \
  -d "{
    \"filters\": {
      \"time_period\": [{\"start_date\": \"2024-01-01\", \"end_date\": \"2026-02-20\"}],
      \"award_type_codes\": [\"A\", \"B\", \"C\", \"D\"],
      \"recipient_search_text\": [\"$COMPETITOR\"]
    },
    \"fields\": [\"Award ID\", \"Recipient Name\", \"Award Amount\", \"Awarding Agency\", \"Description\", \"Start Date\"],
    \"sort\": \"Start Date\",
    \"order\": \"desc\",
    \"limit\": 10,
    \"page\": 1
  }" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', []):
    print(f'  \${r.get(\"Award Amount\", 0):,.0f} — {r.get(\"Awarding Agency\", \"N/A\")}')
    print(f'    {r.get(\"Description\", \"N/A\")[:100]}')
"

# SBIR awards — use web search (SBIR.gov API retired)
echo "--- SBIR Awards ---"
echo "Use web_search: site:sbir.gov \"$COMPETITOR\" award"
echo "Or browse: https://www.sbir.gov/award/all and search by company name"
```

## Weekly Intelligence Report Template

The agent generates this every Wednesday (Competitor Watch cron):

```markdown
# Competitive Intelligence — Week of [DATE]

## New Contract Awards (company NAICS)
| Winner | Amount | Agency | Description |
|--------|--------|--------|-------------|
| ... | ... | ... | ... |

## New SBIR/STTR Awards (in your NAICS codes)
| Company | Phase | Amount | Agency | Topic |
|---------|-------|--------|--------|-------|
| ... | ... | ... | ... | ... |

## New Opportunities Identified
| Source | Title | Agency | Deadline | Score |
|--------|-------|--------|----------|-------|
| SAM.gov | ... | ... | ... | /27 |
| Grants.gov | ... | ... | ... | /27 |
| SBIR.gov | ... | ... | ... | /27 |

## Market Trends
- Total awards this week in our NAICS: $X
- Top winning companies: A, B, C
- Agency spending trends: [up/down/stable]

## Actionable Recommendations
1. [Specific action based on data]
2. [Specific action based on data]
```

## Scoring Integration

Every opportunity found gets scored against the Go/No-Go matrix in `onboarding/RFP-PLAYBOOK.md`:
- Score ≥ 20/27 → Alert immediately, recommend pursuit
- Score 15-19/27 → Flag for user review
- Score < 15/27 → Log but don't alert

## Data Freshness

| Source | Update Frequency | Best For |
|--------|-----------------|----------|
| SAM.gov | Daily | Active solicitations, deadlines |
| USASpending | ~Monthly lag | Historical awards, market sizing |
| SBIR.gov | Weekly | Innovation funding, competitor R&D |
| Grants.gov | Daily | Grant FOAs, cooperative agreements |

**Tip:** USASpending data lags 1-3 months. Don't rely on it for "what just happened" — use SAM.gov award notices for recent wins.
