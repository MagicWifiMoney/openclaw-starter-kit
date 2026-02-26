# OpenClaw Starter Kit

> A fully configured AI chief of staff for your business, built on [OpenClaw](https://openclaw.ai).
> Agent codename: **{{AGENT_NAME}}**

```
 ============================================================

   ___  ___  ___ _ __   ___| | __ ___      __
  / _ \/ _ \/ _ \ '_ \ / __| |/ _` \ \ /\ / /
 | (_) |  _/  __/ | | | (__| | (_| |\ V  V /
  \___/| |  \___|_| |_|\___|_|\__,_| \_/\_/

  Your AI operator for research, ops & business intelligence

 ============================================================
```

---

## What's In Here

```
.
├── README.md                  <- You are here
├── SETUP-GUIDE.md             <- API keys, OAuth, MCP setup instructions
├── openclaw.json              <- Main config (model, skills, channels, crons)
│
├── workspace/                 <- Agent brain files (copy to ~/.openclaw/workspace/)
│   ├── SOUL.md                <- Personality & tone — who your agent is
│   ├── USER.md                <- Your profile, company, working style
│   ├── IDENTITY.md            <- Agent name, emoji, avatar
│   ├── AGENTS.md              <- Operating instructions, workflows, protocols
│   ├── CONVENTIONS.md         <- Formatting rules, checklists, standards
│   ├── TOOLS.md               <- API keys, Notion DBs, Slack channels, service configs
│   ├── MEMORY.md              <- Long-term memory (clients, partners, lessons learned)
│   ├── HEARTBEAT.md           <- 15 scheduled cron jobs (see below)
│   └── onboarding/
│       ├── ONBOARDING.md      <- 5-phase conversational setup (no terminal needed)
│       ├── PLAYBOOK.md        <- Decision frameworks, response templates, strategies
│       ├── KNOWLEDGE-INTAKE.md<- 9-category knowledge gathering guide
│       └── DASHBOARD-BLUEPRINT.md <- (Internal) Command center build spec
│
├── skills-custom/             <- 47 skills (6 industry-specific, 41 general)
│   ├── perplexity/            <- Deep research with citations
│   ├── arxiv/                 <- Academic paper search
│   ├── better-notion/         <- Full Notion CRUD
│   ├── typefully/             <- Social media posting
│   ├── resend/                <- Transactional email
│   ├── seo-dataforseo/        <- Keyword research & SERP analysis
│   └── ... and 28 more        <- See full list below
│
└── reference/
    ├── learnings.md           <- Tool gotchas & operational lessons
    └── mc-logging.md          <- Mission Control logging protocol
```

---

## Skills Overview

Skills are organized into three tiers: **Core** (general-purpose, useful for any business), **Utility** (specialized but broadly applicable), and **Industry-Specific** (optional modules for particular verticals).

---

### Core Skills

These power the fundamental capabilities every agent needs.

#### Research & Intelligence
| Skill | Description |
|-------|-------------|
| `perplexity` | Deep research with citations |
| `research` | Multi-source background research via Gemini |
| `arxiv` | Academic paper search |
| `deep-research` | Extended research sessions |
| `brave-images` | Image search |

#### Productivity & Project Management
| Skill | Description |
|-------|-------------|
| `better-notion` | Full Notion CRUD |
| `planner` | Multi-task project planning |
| `memory-management` | Session memory save/compact |
| `self-improving-agent` | Learning capture & verification |
| `clawddocs` | OpenClaw documentation expert |
| `claude-code-usage` | Claude Code usage tracking |
| `last30days` | Recent activity analysis |

#### Communication
| Skill | Description |
|-------|-------------|
| `resend` | Transactional email (send, receive, audiences) |
| `agentmail` | AI agent email inboxes |
| `typefully` | Social media posting (Twitter, LinkedIn, etc.) |
| `bird` | Twitter/X reading & engagement |

---

### Utility Skills

Specialized tools that extend your agent's reach.

#### Development & Automation
| Skill | Description |
|-------|-------------|
| `frontend-design` | Production-grade UI components |
| `browser-use` | Cloud browser automation |
| `remotion` | Video creation in React |
| `veo` | AI video generation (Google Veo) |
| `video-subtitles` | Subtitle generation & translation |
| `youtube-transcript` | YouTube video transcription |
| `schematron` | HTML->JSON web extraction |
| `qmd` | Local search/indexing CLI |
| `wayback` | Wayback Machine archive access |

#### SEO & Marketing
| Skill | Description |
|-------|-------------|
| `seo-dataforseo` | Keyword research & SERP analysis |
| `reddit-search` | Reddit post/comment search |
| `reddit-cli` | Reddit CLI operations |
| `upload-post` | Media upload & posting |

#### Voice & Media
| Skill | Description |
|-------|-------------|
| `elevenlabs-stt` | Speech-to-text |
| `agents` | ElevenLabs voice AI agents |

#### Crypto & Payments
| Skill | Description |
|-------|-------------|
| `authenticate-wallet` | Base wallet authentication |
| `fund` | Wallet funding (USDC onramp) |
| `send-usdc` | USDC transfers |
| `trade` | Token swaps on Base |
| `x402` | Paid API protocol |
| `search-for-service` | x402 marketplace search |
| `pay-for-service` | x402 paid API calls |
| `monetize-service` | Create paid API endpoints |
| `query-onchain-data` | Base blockchain SQL queries |

#### Data
| Skill | Description |
|-------|-------------|
| `polymarket` | Prediction market queries |

---

## 15 Scheduled Cron Jobs

Your agent configures these automatically during onboarding. No terminal required.

```
    Timeline (Weekday)
    ===================================

    6:00 AM  | Daily Opportunity Scan
             |   Search configured sources for new
             |   opportunities, leads, or updates overnight
             |
    7:00 AM  | Morning Briefing -> Slack
             |   Deadlines, pipeline status, new items
             |
    7:15 AM  | Morning Summary Email
             |   Scannable brief to your inbox
             |
    8:00 AM  | Deadline Watch (every 4hrs)
    - - - -  | - - until 10pm - - - - - - - -
             |
    8:30 AM  | Weekly Pipeline Review (Mon only)
             |   Win rates, stale items, growth suggestions
             |
   12:00 PM  | Noon Proactive Ideas
             |   Only fires if genuinely actionable
             |   (silence = nothing worth your time)
             |
    2:00 PM  | Competitor Watch (Wed only)
             |   Who's winning, new entrants, trends
             |
    5:30 PM  | Evening Summary Email
             |   Day recap, tomorrow's priorities
             |
    8:00 PM  | Cron Doctor (every 2hrs)
    - - - -  | - - self-heals failed jobs - - -
             |
   10:00 PM  | Self-Learning Review
             |   Extract preferences, log gotchas
             |
   11:00 PM  | System Health Check
             |   APIs, disk, workspace integrity
             |
    2:00 AM  | Night Health Audit & Cleanup
             |   Archive old memory, temp cleanup
             |
    - - - -  | - - - - - - - - - - - - - - - -

    WEEKLY
    ===================================
    Sunday   | Knowledge Freshness Check
     9am     |   Stale contacts, expiring accounts,
             |   certification recommendations
             |
    Friday   | Self-Improvement Review
     4pm     |   Slowest tasks, cron value audit,
             |   unused skills, new capabilities
             |
    MONTHLY
    ===================================
    1st      | Win/Loss Analysis
     9am     |   Success rate, patterns, systemic issues
```

---

## Workspace Files Explained

| File | Purpose | When It's Read |
|------|---------|---------------|
| **SOUL.md** | Your agent's personality, tone, decision filters | Every session start |
| **USER.md** | Your profile, company details, working style | Every session start |
| **IDENTITY.md** | Agent name & avatar | Display only |
| **AGENTS.md** | Operating procedures, workflows, channel routing, memory protocol | Every session start |
| **CONVENTIONS.md** | Document structures, compliance checklists, review standards, ask-vs-decide thresholds | When producing deliverables |
| **TOOLS.md** | API keys, Notion DB IDs, Slack channel IDs, service configs | When using integrations |
| **MEMORY.md** | Long-term memory: clients, partners, strategies, competitor intel, lessons learned | Every session start |
| **HEARTBEAT.md** | All 15 cron job definitions with payloads | Heartbeat intervals |

---

## Onboarding Flow

Your agent runs a 5-phase conversational onboarding -- no terminal, no CLI, just chat:

```
Phase 1: Welcome & Identity
   --> Confirm company details, set preferences

Phase 2: Skills Showcase
   --> Live demo of core skills (research, Notion, email, etc.)

Phase 3: Tool Connections
   --> Connect Notion, Slack, email, calendar

Phase 4: Knowledge Intake
   --> 9-category deep dive into your business
       (products, competitors, clients, processes, etc.)

Phase 5: Activate Systems
   --> Turn on cron jobs, set alert preferences
   --> First opportunity scan runs immediately
```

---

## Playbook (Built-In)

The `onboarding/PLAYBOOK.md` includes a ready-made decision framework:

**Scoring Matrix** -- Multi-criteria evaluation scale:
- Strategic fit, feasibility, competition, timeline, revenue potential...
- Hard no-go triggers (resource conflicts, misaligned scope, etc.)

**Response Templates** -- Section-by-section with your win themes baked in

**Tracking Checklist** -- Map every requirement to a response and owner

---

## Setup

See **[SETUP-GUIDE.md](./SETUP-GUIDE.md)** for the full API key checklist:

| Priority | Keys |
|----------|------|
| Required | Anthropic, OpenAI, Gemini, Brave Search |
| Recommended | Notion, Slack, Resend, GitHub, Perplexity |
| Optional | Vercel, ElevenLabs, Cloudflare, Apify |

---

## Model Configuration

```
Default:  anthropic/claude-sonnet-4-6  (fast, cost-effective)
Fallbacks: sonnet-4-6 -> gpt-4o -> gemini-flash
```

All cron jobs and sub-agents run on Sonnet. Override to Opus for complex reasoning when needed.

---

## License

Private repository. Built by [OpenClaw](https://openclaw.ai).
