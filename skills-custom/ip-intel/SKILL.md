# IP Intelligence Skill

Turn anonymous web traffic into named companies and organizations — for free.

## What it does

1. **Captures** visitor IPs client-side via a Webflow snippet
2. **Enriches** with organization name, ISP, and location via ip-api.com (no API key, no cost)
3. **Stores** enriched data in PostHog as custom events (if PostHog is installed) or via standalone collector
4. **Digests** interesting visitors — filters out consumer ISPs, surfaces companies, gov agencies, defense contractors, universities
5. **Alerts** on high-value hits via Discord webhook or file output

## Stack detected: VastVision.io

- Site builder: **Webflow** (no server-side code)
- Analytics already installed: **PostHog** + GA4 + Clarity
- Strategy: PostHog-first (piggyback on existing install)

## Setup (5 minutes)

### Step 1: Drop the Webflow snippet

In Webflow: **Site Settings → Custom Code → Footer Code**

Paste the contents of `webflow-snippet.html`

That's it for data capture. Enriched org data will appear in PostHog as `ip_enriched` events within minutes of the next visitor.

### Step 2 (optional): Pull digests via OpenClaw

Set your PostHog API key:

```bash
export POSTHOG_API_KEY="phc_..."         # your PostHog personal API key (not project key)
export POSTHOG_PROJECT_ID="your_project_id"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."  # optional
```

Run a digest:

```bash
python3 skills-custom/ip-intel/scripts/digest.py
```

Or use OpenClaw agent:

```
/run ip-intel digest
```

## How enrichment works

```
Visitor hits Webflow site
  → Webflow loads PostHog (already there)
  → Our snippet fires fetch() to ip-api.com
  → Gets back: org name, ISP, ASN, city, country
  → Calls posthog.capture("ip_enriched", { org, isp, city, ... })
  → PostHog stores it linked to the session/person
```

ip-api.com: no key, no account, 1000 req/hour, HTTP only.
For HTTPS (needed on Webflow), uses ipapi.co free tier fallback (1000/day, no key).

## What you'll see in PostHog

Each `ip_enriched` event has:
- `org` - e.g. "AS7922 Comcast Cable" or "AS1916 Boeing Company"
- `isp` - ISP name
- `city` / `country`
- `page` - which page they were on
- `ip` - raw IP (PostHog already captures this; we surface it for easy filtering)

Filter PostHog events by `org` contains "Department" or "Boeing" or "Lockheed" to find warm leads instantly.

## Consumer ISP filter

The digest script filters out noise automatically:
- Comcast, Charter, Cox, AT&T, Verizon, T-Mobile, Spectrum, CenturyLink
- Generic residential/mobile ASNs

What's left: corporate networks, gov agencies, universities, research orgs.

## Files

| File | Purpose |
|------|---------|
| `webflow-snippet.html` | Drop into Webflow custom code footer |
| `scripts/digest.py` | Query PostHog, filter, surface interesting visitors |
| `scripts/enrich.py` | Standalone enricher (if not using PostHog) |
| `scripts/test_enrich.py` | Test enrichment with a sample IP |

## No PostHog? Standalone mode

If the site doesn't have PostHog, use `scripts/enrich.py` which:
- Reads IPs from a text file or stdin
- Enriches via ip-api.com + RDAP fallback
- Writes enriched JSON
- Optionally sends Discord alert for interesting orgs
