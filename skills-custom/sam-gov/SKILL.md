---
name: sam-gov
description: Search federal contract opportunities on SAM.gov. Use when looking for RFPs, solicitations, pre-solicitations, sources sought, or any federal contracting opportunity. Supports filtering by NAICS code, agency, state, set-aside type, and date range.
---

# SAM.gov Opportunities Search

Search the federal government's official contract opportunities database.

## API Details

- **Base URL:** `https://api.sam.gov/opportunities/v2/search`
- **Auth:** API key as query parameter `api_key`
- **API Key:** Read from TOOLS.md or use env var `SAM_GOV_API_KEY`
- **Rate Limit:** 10,000 requests/day (non-federal)
- **Key expiry tracked in:** MEMORY.md → API Key Expiry Tracking

## Search Opportunities

```bash
# Basic search — last 30 days, your company's NAICS codes
curl -s "https://api.sam.gov/opportunities/v2/search?api_key=SAM_API_KEY&postedFrom=MM/dd/yyyy&postedTo=MM/dd/yyyy&ncode=NAICS_CODE&limit=25&offset=0" | python3 -m json.tool
```

### Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `api_key` | SAM.gov API key (required) | `${SAM_GOV_API_KEY}` |
| `postedFrom` | Start date MM/dd/yyyy (required) | `01/01/2026` |
| `postedTo` | End date MM/dd/yyyy (required) | `02/20/2026` |
| `ncode` | NAICS code (up to 6 digits) | `334515` |
| `ptype` | Procurement type (see below) | `o` (solicitation) |
| `title` | Keyword in title | `RFID` |
| `state` | Place of performance state | `NM` |
| `typeOfSetAside` | Set-aside type | `SBA` (small business) |
| `organizationName` | Agency name | `Department of Energy` |
| `limit` | Results per page (max 1000) | `25` |
| `offset` | Pagination offset | `0` |

### Procurement Types (ptype)

| Code | Type |
|------|------|
| `o` | Solicitation |
| `p` | Pre-solicitation |
| `k` | Combined Synopsis/Solicitation |
| `r` | Sources Sought |
| `s` | Special Notice |
| `a` | Award Notice |
| `u` | Justification (J&A) |
| `g` | Sale of Surplus Property |

### Default NAICS Codes (customize for your company)

Always search these unless the user specifies otherwise:
- `334515` — Instrument Manufacturing for Measuring/Testing Electricity
- `334519` — Other Measuring and Controlling Device Manufacturing
- `541330` — Engineering Services
- `541715` — R&D in Physical, Engineering, and Life Sciences
- `541712` — R&D in Physical Sciences and Engineering

### Example: Daily RFP Scan

```bash
# Search last 7 days across all company NAICS codes
API_KEY="${SAM_GOV_API_KEY}"
FROM=$(date -d "7 days ago" +%m/%d/%Y)
TO=$(date +%m/%d/%Y)

for NAICS in 334515 334519 541330 541715 541712; do
  echo "=== NAICS $NAICS ==="
  curl -s "https://api.sam.gov/opportunities/v2/search?api_key=$API_KEY&postedFrom=$FROM&postedTo=$TO&ncode=$NAICS&limit=10&offset=0" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for opp in data.get('opportunitiesData', []):
    print(f\"  {opp.get('title', 'N/A')}\")
    print(f\"    Solicitation: {opp.get('solicitationNumber', 'N/A')}\")
    print(f\"    Agency: {opp.get('fullParentPathName', 'N/A')}\")
    print(f\"    Type: {opp.get('type', 'N/A')}\")
    print(f\"    Posted: {opp.get('postedDate', 'N/A')}\")
    print(f\"    Response Deadline: {opp.get('responseDeadLine', 'N/A')}\")
    print(f\"    URL: https://sam.gov/opp/{opp.get('noticeId', '')}/view\")
    print()
"
done
```

### Response Fields

Key fields in each opportunity:
- `title` — Opportunity title
- `solicitationNumber` — Solicitation number
- `fullParentPathName` — Agency hierarchy
- `type` — Procurement type
- `postedDate` — When posted
- `responseDeadLine` — Submission deadline
- `noticeId` — Use for SAM.gov URL: `https://sam.gov/opp/{noticeId}/view`
- `description` — Full description (may contain HTML)
- `naicsCode` — NAICS classification
- `classificationCode` — Product/service code
- `setAside` — Set-aside type if applicable
- `placeOfPerformance` — Location details

### Scoring an Opportunity

After fetching, score against Go/No-Go matrix in `onboarding/RFP-PLAYBOOK.md`:
1. Technical fit (NAICS match, capability alignment)
2. Past performance relevance
3. Set-aside eligibility
4. Timeline feasibility
5. Competition level
6. Contract value vs effort

Log promising opportunities to `memory/rfp-pipeline.md` with status: Identified.
