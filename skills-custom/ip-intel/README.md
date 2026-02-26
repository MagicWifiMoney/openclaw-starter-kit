# IP Intel

Turn anonymous website traffic into named companies — for free. No API keys required.

## What It Does

Identifies which **organizations and companies** are visiting your website by enriching visitor IP addresses with public registry data. Filters out consumer ISPs (Comcast, AT&T, etc.) and surfaces the interesting stuff — defense contractors, government agencies, universities, energy companies.

**Example output:**
```
High-Value Visitors (3)
  - Boeing Company (Seattle, US) - 4 visits - Pages: /products/rfid-solutions, /contact-us
  - US Department of Energy (Washington, US) - 2 visits - Pages: /industries/defense
  - Northrop Grumman (VA, US) - 1 visit - Pages: /products/magtag

Other Orgs (12)
  - MIT Lincoln Laboratory - 3 visits
  - Meehan Group LLC - 2 visits
  ...
```

## How It Works

```
Visitor lands on your site
  → Snippet fires async fetch to ipapi.co (HTTPS, free, no key)
  → Gets back: org name, city, country, ASN
  → Stores it in PostHog as an ip_enriched event (linked to session)
  → Digest script queries PostHog, filters noise, surfaces leads
```

**~20-40% of B2B traffic is identifiable this way** (corporate networks, gov, universities). Consumer home internet always comes back as Comcast/AT&T and gets filtered out automatically.

## Setup

### Option A: PostHog site (recommended)

If your site already has PostHog installed:

**1. Add the Webflow/HTML snippet**

Paste `webflow-snippet.html` into your site's `<body>` (Webflow: Site Settings → Custom Code → Footer Code).

Works with any HTML site — just include it before `</body>`.

**2. Verify in PostHog**

Visit your site → check PostHog Events for `ip_enriched` events. Should appear within seconds.

**3. Run digests**

```bash
pip install requests

export POSTHOG_API_KEY="phx_..."          # PostHog Settings > Personal API Keys
export POSTHOG_PROJECT_ID="12345"         # visible in your PostHog URL
export DISCORD_WEBHOOK_URL="https://..."  # optional: get alerts in Discord

python3 scripts/digest.py --days 7
python3 scripts/digest.py --days 30 --alert
```

### Option B: No PostHog (standalone)

Enrich a list of IPs directly:

```bash
# Single IP
python3 scripts/enrich.py --ip 205.1.255.1

# From file
cat access.log | awk '{print $1}' | sort -u > ips.txt
python3 scripts/enrich.py --file ips.txt --no-consumers --output results.json

# From stdin
echo "205.1.255.1" | python3 scripts/enrich.py
```

## Files

| File | What it does |
|------|-------------|
| `webflow-snippet.html` | Drop into any site's footer HTML. Captures + enriches visitor IP client-side. |
| `scripts/digest.py` | Queries PostHog for `ip_enriched` events, filters noise, outputs human-readable report. |
| `scripts/enrich.py` | Standalone enricher — pipe IPs in, get enriched JSON out. No PostHog needed. |
| `scripts/test_enrich.py` | Sanity check. Run after setup to confirm enrichment is working. |
| `VASTVISION-SETUP.md` | Step-by-step setup guide for Webflow + PostHog sites. |

## APIs Used (all free, no signup)

| API | Protocol | Limit | Used for |
|-----|----------|-------|---------|
| [ipapi.co](https://ipapi.co) | HTTPS | 1,000/day | Client-side enrichment in snippet |
| [ip-api.com](https://ip-api.com) | HTTP | 1,000/hr | Server-side batch enrichment |
| [RDAP (ARIN/RIPE)](https://rdap.arin.net) | HTTPS | No limit | Fallback org lookup |

> **Note:** ip-api.com is HTTP only — fine for server-side scripts, but the browser snippet uses ipapi.co (HTTPS) to avoid mixed-content warnings on SSL sites.

## Consumer ISP Filter

The digest automatically drops noise from residential and cloud IPs:

- Home internet: Comcast, Charter, Spectrum, AT&T, Verizon, T-Mobile...
- Cloud infra: AWS, Google Cloud, Azure, DigitalOcean, Cloudflare...

What's left: actual companies worth knowing about.

## Requirements

```bash
pip install requests  # only needed for digest.py
```

`enrich.py` and the snippet use zero external dependencies (stdlib + fetch).

## Privacy

IP enrichment is standard practice for B2B websites (used by Clearbit, Leadfeeder, etc.). Recommend adding a note to your privacy policy:

> *We may use IP address data to identify the organization associated with visitor traffic for analytics and sales purposes.*
