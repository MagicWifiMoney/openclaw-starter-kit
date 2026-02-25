# TOOLS.md — Integrations & Config Reference

Quick reference for all external tools and services. Update this file as integrations are configured during onboarding.

---

## Notion

**API Key:** [SETUP REQUIRED — add to `reference/keys.md`]
**Workspace:** {{YOUR_COMPANY}}

| Database | Purpose | ID |
|----------|---------|-----|
| Projects | Active projects, milestones, ownership | [SETUP REQUIRED] |
| Pipeline | Opportunities, leads, deals — qualify through close | [SETUP REQUIRED] |
| Contacts | Clients, partners, vendors, key relationships | [SETUP REQUIRED] |
| Knowledge Base | Company intel, processes, templates, reference material | [SETUP REQUIRED] |

**Usage:** Project management, pipeline tracking, knowledge storage. Notion is the record of what {{YOUR_COMPANY}} is pursuing and what it has delivered.

---

## Slack

**Workspace:** {{YOUR_COMPANY}}
**Bot Token:** [SETUP REQUIRED — add to `reference/keys.md`]

| Channel | Purpose | ID |
|---------|---------|-----|
| #general | Company-wide announcements, general comms | [SETUP REQUIRED] |
| #projects | Active project updates, deliverable tracking | [SETUP REQUIRED] |
| #alerts | Deadline reminders, opportunity flags, system notifications | [SETUP REQUIRED] |
| #research | Market research, competitive intel, industry news | [SETUP REQUIRED] |

**Usage:** {{AGENT_NAME}} posts to Slack for new opportunity alerts, deadline reminders (T-7, T-3, T-1 days), research summaries, and critical system notifications.

---

## GSuite / Google Drive

**Account:** [SETUP REQUIRED — service account or OAuth]
**Primary Drive Folder:** {{YOUR_COMPANY}} / [SETUP REQUIRED — folder ID]

| Folder | Purpose | ID |
|--------|---------|-----|
| Projects | Active project documents and deliverables | [SETUP REQUIRED] |
| Templates | Standard docs, forms, formatting templates | [SETUP REQUIRED] |
| Archive | Completed projects, historical records | [SETUP REQUIRED] |
| Admin | Contracts, legal, HR | [SETUP REQUIRED] |

**Usage:** Document storage for deliverables, templates, and company records. Source of truth for files that go into client-facing outputs.

---

## Email

**Provider:** [SETUP REQUIRED — Gmail, Outlook, Resend, etc.]
**Account:** [SETUP REQUIRED]

**Usage:** Draft emails for {{USER_NAME}}'s review. NEVER send without explicit approval. Drafts go to {{USER_NAME}} for review before sending.

---

## CRM

<!--
  Pick your CRM and fill in the details. Common options:
  - HubSpot (free tier available, good API)
  - Salesforce (enterprise, complex API)
  - Pipedrive (simple, sales-focused)
  - Close.com (startup-friendly)
  - Notion (DIY — using a Notion database as CRM)
  - Spreadsheet (Google Sheets — hey, it works)
-->

**Platform:** [SETUP REQUIRED — {{YOUR_CRM}}]
**API Key:** [SETUP REQUIRED — add to `reference/keys.md`]

| Entity | Purpose | Notes |
|--------|---------|-------|
| Contacts | People — leads, clients, partners | [SETUP REQUIRED] |
| Companies | Organizations — prospects, clients, vendors | [SETUP REQUIRED] |
| Deals / Opportunities | Pipeline — qualify through close | [SETUP REQUIRED] |
| Activities | Logged interactions — calls, emails, meetings | [SETUP REQUIRED] |

**Usage:** Pipeline management and relationship tracking. {{AGENT_NAME}} reads deal status and contacts from CRM to inform daily briefings, opportunity alerts, and competitive intelligence.

---

## Project Management

<!--
  If you use a separate project management tool (not just Notion), configure it here.
  Common options: Linear, Asana, Monday.com, Trello, Jira, ClickUp, GitHub Projects
-->

**Platform:** [SETUP REQUIRED — or "Using Notion" if Notion handles this]
**API Key:** [SETUP REQUIRED — add to `reference/keys.md`]

**Usage:** Task tracking, sprint planning, deliverable status. {{AGENT_NAME}} checks for overdue tasks, stale items, and blocked work.

---

## Design Tools

<!--
  If your team uses design tools for deliverables, presentations, or marketing.
  Common options: Figma, Canva, Adobe Creative Suite
-->

**Platform:** [SETUP REQUIRED — e.g., Figma, Canva]
**Account:** [SETUP REQUIRED]

**Usage:** When handing off content for design, always include section labels, character limits, and figure placeholders. {{AGENT_NAME}} generates content (markdown sections, structured text) that the team lays out in the design tool.

---

## Company Website

**URL:** {{YOUR_WEBSITE}}
**CMS / Platform:** [SETUP REQUIRED — e.g., WordPress, Webflow, Next.js, Squarespace]
**Usage:** Reference for company positioning, product descriptions, and public-facing content. Keep deliverable language consistent with website.

---

## Industry-Specific APIs

<!--
  Add data sources and APIs specific to your industry here.
  The format below shows how to document them. Delete the examples and add your own.

  EXAMPLES BY INDUSTRY:

  Government Contracting:
  - SAM.gov API (federal opportunities)
  - USASpending.gov API (past awards)
  - SBIR.gov (small business innovation)
  - GovWin IQ (opportunity intelligence)

  E-commerce:
  - Shopify API (store data)
  - Amazon SP-API (marketplace data)
  - Google Merchant Center API

  SaaS:
  - Stripe API (revenue data)
  - Mixpanel/Amplitude API (analytics)
  - Intercom API (customer data)

  Real Estate:
  - Zillow API / Redfin data
  - County records API
  - MLS API (if available)

  Marketing Agency:
  - Google Ads API
  - Meta Ads API
  - SEMrush / Ahrefs API
  - DataForSEO API
-->

### Industry Data Sources

| Source | Endpoint / URL | Auth | Notes |
|--------|---------------|------|-------|
| [SETUP REQUIRED] | [API endpoint] | [API Key / OAuth / None] | [What you use it for] |
| [SETUP REQUIRED] | [API endpoint] | [API Key / OAuth / None] | [What you use it for] |

### Paid Services (Recommended)

| Source | Cost | Notes |
|--------|------|-------|
| **Perplexity API** | $5/mo | Deep research with citations — competitive intel, market research. [OPTIONAL] |
| **Firecrawl** | Free tier available | Web scraping for sites without APIs. [OPTIONAL] |
| [SETUP REQUIRED] | [Cost] | [What you use it for] |

---

## Pre-Configured API Keys

These keys are ready to use:

| Service | Env Var | Notes |
|---------|---------|-------|
| [SETUP REQUIRED] | `[ENV_VAR_NAME]` | [Expiry date if applicable] |

**IMPORTANT:** Never hardcode credentials in scripts or memory files. All keys stored in: `reference/keys.md`

---

*Last updated: [SETUP REQUIRED — update during onboarding]*
