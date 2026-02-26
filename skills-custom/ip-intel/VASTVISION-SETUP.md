# VastVision IP Intel - Setup Guide

Your site is built on Webflow with PostHog already installed. This is the fastest path.

## Step 1: Add the snippet to Webflow (5 min)

1. Log into Webflow
2. Go to **Site Settings** (the gear icon)
3. Click **Custom Code**
4. Scroll to **Footer Code**
5. Paste the entire contents of `webflow-snippet.html`
6. Click **Save Changes**
7. Publish the site

That's it. The next visitor will have their org data captured as a PostHog event.

## Step 2: Verify it's working

1. Open your site in a browser
2. Open PostHog → Events
3. Filter for event name: `ip_enriched`
4. You should see it within seconds with your own IP/org

## Step 3: View in PostHog

In PostHog, you can now:

**Filter sessions by org:**
- Insights → Filter by event property `ip_org` contains "Department"
- Insights → Filter by event property `ip_org` contains "Boeing" 
- Cohorts → Create "High-Value Visitors" cohort where `company_org` contains any target

**See the raw events:**
- Events → Search for `ip_enriched`
- Each event shows: org, ASN, city, country, page visited

## Step 4 (optional): Daily digest via OpenClaw

Get a daily summary of interesting company visitors in Discord:

```bash
# In ~/.openclaw/openclaw.json, add to env:
# "POSTHOG_API_KEY": "your-personal-api-key",  (Settings > Personal API Keys in PostHog)
# "POSTHOG_PROJECT_ID": "your-project-id",      (visible in PostHog URL)
# "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/..."

python3 skills-custom/ip-intel/scripts/digest.py --days 7 --alert
```

Or ask OpenClaw: "Show me VastVision visitor intel from the last week"

## What you'll catch

Your target buyers - defense contractors, energy companies, government agencies, logistics firms - almost always visit from **corporate networks**. When Lockheed Martin, Boeing, or a DoD agency visits your pricing page, you'll know.

Consumer users (home Comcast, AT&T mobile) are automatically filtered out.

## Notes

- **Rate limit:** ipapi.co free tier = 1,000 req/day. VastVision's traffic volume is fine.
- **Privacy:** IP enrichment is industry-standard for B2B sites. Include it in your privacy policy.
- **HTTPS:** The snippet is fully HTTPS-compatible with Webflow's SSL.
- **Performance:** The fetch call is async and non-blocking. Zero impact on page load.
