---
name: grants-gov
description: Search federal grant opportunities on Grants.gov. Use when looking for federal grants, cooperative agreements, or funding opportunity announcements (FOAs) relevant to R&D, energy, defense, or infrastructure. Complements SAM.gov for non-contract funding.
---

# Grants.gov — Federal Grant Opportunities

Search for federal grants, cooperative agreements, and funding opportunities. Complements SAM.gov (which focuses on contracts) with grant-based funding.

## API Details

- **Base URL:** `https://api.grants.gov/v1/api/`
- **Auth:** API key via header `X-Api-Key` (or works without for basic searches)
- **Docs:** https://api.grants.gov/
- **Note:** If you have a Grants.gov API key, add it to TOOLS.md. Basic search works without one.

## Search Opportunities

### By Keyword

```bash
curl -s -X POST "https://api.grants.gov/v1/api/search2" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "RFID sensor infrastructure",
    "oppStatuses": "forecasted|posted",
    "sortBy": "openDate|desc",
    "rows": 25,
    "startRecordNum": 0
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for opp in data.get('hits', data.get('oppHits', [])):
    print(f\"  {opp.get('title', opp.get('oppTitle', 'N/A'))}\")
    print(f\"    Agency: {opp.get('agency', opp.get('agencyName', 'N/A'))}\")
    print(f\"    Number: {opp.get('number', opp.get('oppNumber', 'N/A'))}\")
    print(f\"    Close: {opp.get('closeDate', opp.get('oppCloseDate', 'N/A'))}\")
    print(f\"    URL: https://grants.gov/search-results-detail/{opp.get('oppId', opp.get('id', ''))}\")
    print()
"
```

### By Agency

```bash
# DOE opportunities (example agency search)
curl -s -X POST "https://api.grants.gov/v1/api/search2" \
  -H "Content-Type: application/json" \
  -d '{
    "agencies": "DOE",
    "oppStatuses": "posted",
    "sortBy": "openDate|desc",
    "rows": 25,
    "startRecordNum": 0
  }' | python3 -m json.tool | head -80
```

### By CFDA/Assistance Listing Number

```bash
# Search by specific program
curl -s -X POST "https://api.grants.gov/v1/api/search2" \
  -H "Content-Type: application/json" \
  -d '{
    "cfdas": "81.049",
    "oppStatuses": "posted",
    "rows": 25
  }' | python3 -m json.tool | head -80
```

## Example Priority Searches (customize for your company)

### Keywords
- `RFID` / `radio frequency identification`
- `magnetoelastic sensor` / `passive sensor`
- `asset tracking` / `asset management`
- `infrastructure monitoring` / `critical infrastructure`
- `energy infrastructure` / `grid monitoring`
- `wireless sensor` / `IoT sensor`
- `non-destructive evaluation` / `NDE`

### Priority Agencies
| Agency | Code | Why |
|--------|------|-----|
| Department of Energy | `DOE` | Energy R&D funding |
| Department of Defense | `DOD` | Defense logistics, asset tracking |
| Dept of Homeland Security | `DHS` | Critical infrastructure protection |
| National Science Foundation | `NSF` | Fundamental sensor research |
| NASA | `NASA` | Extreme environment sensing |
| ARPA-E | (under DOE) | Advanced energy tech |

### Relevant CFDA Numbers
- `81.049` — DOE Office of Science Financial Assistance
- `81.086` — Conservation R&D
- `81.089` — Fossil Energy R&D
- `81.135` — Advanced Research Projects Agency - Energy
- `12.431` — DoD Basic Scientific Research
- `12.800` — Air Force Defense Research Sciences
- `97.077` — DHS S&T Homeland Security Research

## Daily Scan Script

```bash
#!/bin/bash
# grants-scan.sh — Run daily, check for new opportunities

KEYWORDS=("RFID sensor" "magnetoelastic" "asset tracking" "infrastructure monitoring" "passive sensor" "wireless sensor")
AGENCIES=("DOE" "DOD" "DHS" "NSF" "NASA")

echo "=== Grants.gov Daily Scan — $(date +%Y-%m-%d) ==="

for KW in "${KEYWORDS[@]}"; do
  RESULTS=$(curl -s -X POST "https://api.grants.gov/v1/api/search2" \
    -H "Content-Type: application/json" \
    -d "{\"keyword\": \"$KW\", \"oppStatuses\": \"posted\", \"rows\": 5, \"startRecordNum\": 0}")
  
  COUNT=$(echo "$RESULTS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('hitCount', json.load(sys.stdin).get('numberOfHits', 0)))" 2>/dev/null || echo "0")
  
  if [ "$COUNT" != "0" ]; then
    echo "  [$KW] — $COUNT results"
    echo "$RESULTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for opp in data.get('hits', data.get('oppHits', []))[:3]:
    title = opp.get('title', opp.get('oppTitle', 'N/A'))
    agency = opp.get('agency', opp.get('agencyName', 'N/A'))
    close = opp.get('closeDate', opp.get('oppCloseDate', 'N/A'))
    print(f\"    • {title[:70]} | {agency} | Close: {close}\")
" 2>/dev/null
  fi
done
```

## Grant vs Contract Decision

| Factor | Grant (Grants.gov) | Contract (SAM.gov) |
|--------|--------------------|--------------------|
| Funding style | Cost reimbursement, milestone-based | Fixed price or cost-plus |
| IP ownership | Usually retained by performer | Often government-owned |
| Competition | Peer-reviewed, merit-based | Lowest price or best value |
| Best for | R&D, proof of concept, Phase I | Production, services, Phase III |
| Company fit | R&D, new applications | Production, deployments |

## Tips
- Grants.gov posts many DOE FOAs (Funding Opportunity Announcements) that don't appear on SAM.gov
- ARPA-E opportunities are high-value, high-risk — great for breakthrough technology
- Many grants allow teaming with national labs — leverage any existing relationships
- Check both `forecasted` and `posted` statuses — forecasted gives early warning to prepare
