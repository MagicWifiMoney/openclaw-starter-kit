---
name: usaspending
description: Search federal contract awards and spending data on USASpending.gov. Use when researching competitors, finding who's winning contracts in specific NAICS codes, analyzing agency spending patterns, or tracking contract award values. No API key required.
---

# USASpending.gov — Federal Spending Data

Track who's winning federal contracts, how much agencies are spending, and where the money flows. **No API key needed.**

## API Details

- **Base URL:** `https://api.usaspending.gov/api/v2/`
- **Auth:** None required (public API)
- **Docs:** https://api.usaspending.gov/
- **Rate Limit:** Generous but undocumented; be respectful

## Key Endpoints

### 1. Search Contract Awards

Find who's winning contracts in your company's NAICS codes.

```bash
curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_award/" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "time_period": [{"start_date": "2025-01-01", "end_date": "2026-02-20"}],
      "award_type_codes": ["A", "B", "C", "D"],
      "naics_codes": {"require": ["334515", "334519", "541715"]},
      "place_of_performance_locations": [{"country": "USA", "state": "NM"}]
    },
    "fields": [
      "Award ID", "Recipient Name", "Award Amount", 
      "Awarding Agency", "Award Type", "Start Date",
      "Description", "NAICS Code"
    ],
    "sort": "Award Amount",
    "order": "desc",
    "limit": 25,
    "page": 1
  }' | python3 -m json.tool | head -100
```

### Award Type Codes
| Code | Type |
|------|------|
| `A` | BPA Call |
| `B` | Purchase Order |
| `C` | Delivery Order |
| `D` | Definitive Contract |
| `IDV_A` | GWAC |
| `IDV_B` | IDC |
| `IDV_B_A` | IDC / GWAC |
| `IDV_B_B` | IDC / BOA |
| `IDV_B_C` | IDC / BPA |
| `IDV_E` | FSS |

### 2. Search by Keyword

```bash
curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_award/" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "time_period": [{"start_date": "2025-01-01", "end_date": "2026-02-20"}],
      "award_type_codes": ["A", "B", "C", "D"],
      "keywords": ["RFID tracking", "magnetoelastic sensor", "asset tracking"]
    },
    "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Description"],
    "sort": "Award Amount",
    "order": "desc",
    "limit": 25,
    "page": 1
  }' | python3 -m json.tool
```

### 3. Agency Spending Overview

See how much an agency spends on relevant categories.

```bash
# Top agencies by spending in NAICS 334515
curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_category/awarding_agency/" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "time_period": [{"start_date": "2025-01-01", "end_date": "2026-02-20"}],
      "naics_codes": {"require": ["334515", "334519", "541715"]}
    },
    "limit": 10
  }' | python3 -m json.tool
```

### 4. Recipient (Competitor) Lookup

```bash
# Search for a specific company's awards
curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_award/" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "time_period": [{"start_date": "2024-01-01", "end_date": "2026-02-20"}],
      "award_type_codes": ["A", "B", "C", "D"],
      "recipient_search_text": ["COMPETITOR_NAME"]
    },
    "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Description", "NAICS Code"],
    "sort": "Award Amount",
    "order": "desc",
    "limit": 25,
    "page": 1
  }' | python3 -m json.tool
```

### 5. New Awards Feed (for Competitor Watch cron)

```bash
# Awards in last 7 days for your company NAICS codes
FROM=$(date -d "7 days ago" +%Y-%m-%d)
TO=$(date +%Y-%m-%d)

curl -s -X POST "https://api.usaspending.gov/api/v2/search/spending_by_award/" \
  -H "Content-Type: application/json" \
  -d "{
    \"filters\": {
      \"time_period\": [{\"start_date\": \"$FROM\", \"end_date\": \"$TO\"}],
      \"award_type_codes\": [\"A\", \"B\", \"C\", \"D\"],
      \"naics_codes\": {\"require\": [\"334515\", \"334519\", \"541330\", \"541715\", \"541712\"]}
    },
    \"fields\": [\"Award ID\", \"Recipient Name\", \"Award Amount\", \"Awarding Agency\", \"Description\", \"Start Date\"],
    \"sort\": \"Start Date\",
    \"order\": \"desc\",
    \"limit\": 50,
    \"page\": 1
  }" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', []):
    print(f\"  {r.get('Recipient Name', 'N/A')} — \${r.get('Award Amount', 0):,.0f}\")
    print(f\"    Agency: {r.get('Awarding Agency', 'N/A')}\")
    print(f\"    {r.get('Description', 'N/A')[:120]}\")
    print()
"
```

## Competitor Watch

Known competitors to track (update as you identify more):
- [Add during onboarding Phase 1 → Knowledge Intake]

## Analysis Patterns

1. **Market sizing:** Sum award amounts by NAICS over 12 months → total addressable market
2. **Incumbent mapping:** Group awards by recipient → who owns which agency relationships
3. **Trend spotting:** Compare YoY spending by NAICS → growing or shrinking sectors
4. **Win rate benchmarking:** Track your company proposals submitted vs awards won over time
5. **Agency targeting:** Rank agencies by spend in your company's NAICS → prioritize BD efforts
