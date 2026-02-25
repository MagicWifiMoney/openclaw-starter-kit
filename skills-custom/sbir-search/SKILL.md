---
name: sbir-search
description: Search SBIR/STTR opportunities and past awards. Use when looking for Small Business Innovation Research or Small Business Technology Transfer funding, checking past SBIR winners, or finding Phase I/II/III opportunities relevant to your company's technology areas.
---

# SBIR/STTR Opportunity Search

Search for Small Business Innovation Research (SBIR) and Small Business Technology Transfer (STTR) opportunities. These are the bread and butter for small tech companies.

## Access Methods

The SBIR.gov legacy JSON API has been retired. Use these approaches instead:

### Method 1: Web Search (Recommended)
Use Brave Search or web_fetch to search SBIR.gov directly:

```bash
# Search for open SBIR solicitations via web
# Use web_search tool with queries like:
#   "site:sbir.gov RFID sensor open solicitation"
#   "site:sbir.gov magnetoelastic 2026"
#   "site:sbir.gov DOE asset tracking"
```

### Method 2: SAM.gov SBIR Filter
Many SBIR/STTR solicitations are cross-posted to SAM.gov. Use the sam-gov skill with set-aside filter:

```bash
# SBIR opportunities on SAM.gov
API_KEY="${SAM_GOV_API_KEY}"
FROM=$(date -d "30 days ago" +%m/%d/%Y)
TO=$(date +%m/%d/%Y)

curl -s "https://api.sam.gov/opportunities/v2/search?api_key=$API_KEY&postedFrom=$FROM&postedTo=$TO&typeOfSetAside=SBIR&limit=25&offset=0" | python3 -m json.tool
```

### Method 3: Agency-Specific Portals
- **DOE SBIR:** https://science.osti.gov/sbir — DOE posts topics here first
- **DoD SBIR:** https://www.dodsbirsttr.mil/topics-app/ — Searchable topic database
- **NASA SBIR:** https://sbir.nasa.gov/solicitations — NASA-specific topics
- **NSF SBIR:** https://seedfund.nsf.gov/ — NSF SEED Fund (formerly SBIR)

### Method 4: SBIR.gov Award Search (Browser)
For past awards research, use the browser tool to search:
- https://www.sbir.gov/award/all — searchable award database
- Filter by company, keyword, agency, phase, year

### Example Priority Search Terms (customize for your company)
- `RFID` / `radio frequency identification`
- `magnetoelastic` / `passive sensor`
- `asset tracking` / `asset management`
- `infrastructure monitoring`
- `UHF` / `wireless sensor`
- `non-destructive evaluation`

## SBIR Strategy Template

### Priority Agencies (customize based on your past performance)
1. **DOE** — Energy-related R&D
2. **DoD** — Defense applications
3. **DHS** — Critical infrastructure monitoring
4. **NASA** — Sensor technology for extreme environments

### Phase Strategy
- **Phase I** ($50K-275K, 6-12 months): Proof of concept.
- **Phase II** ($500K-1.75M, 2 years): Prototype development.
- **Phase III** (no SBIR funding, commercial): Commercialization.

### Competitive Intelligence

```bash
# What has your company won before?
curl -s "https://www.sbir.gov/api/awards.json?company=YOUR_COMPANY_NAME&rows=50" | python3 -m json.tool

# What are competitors winning?
for COMPETITOR in "CompetitorA" "CompetitorB"; do
  echo "=== $COMPETITOR ==="
  curl -s "https://www.sbir.gov/api/awards.json?company=$COMPETITOR&rows=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
total = sum(a.get('award_amount', 0) for a in data if isinstance(a.get('award_amount'), (int, float)))
print(f\"  Awards found: {len(data)}, Total value: \${total:,.0f}\")
for a in data[:5]:
    print(f\"    {a.get('award_year', '?')} Phase {a.get('phase', '?')} — \${a.get('award_amount', 0):,.0f} — {a.get('award_title', 'N/A')[:60]}\")
"
done
```

## Cron Integration

The daily RFP scan (6am MST) should include SBIR checks:
1. Search open solicitations for all company keywords
2. Compare against `memory/rfp-pipeline.md` to avoid re-alerting
3. Score new finds against Go/No-Go matrix
4. Flag high-scoring opportunities to Slack #rfps
