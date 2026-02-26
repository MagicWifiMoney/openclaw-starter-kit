# OpenClaw Starter Kit -- Setup Guide

## What's In This Kit
- `openclaw.json` -- Full config (secrets replaced with REPLACE_ME)
- `workspace/` -- Agent personality + operating instructions (the secret sauce)
- `skills-custom/` -- 47 custom skills for research, social, email, SEO, crypto, and more
- `reference/` -- Learnings and logging templates

## Step 1: Install OpenClaw
```bash
brew install openclaw/tap/openclaw
openclaw setup
```

## Step 2: Copy Config
```bash
cp openclaw.json ~/.openclaw/openclaw.json
```

## Step 3: Set Up Workspace
```bash
mkdir -p ~/clawd/memory ~/clawd/reference ~/clawd/scripts
cp workspace/* ~/clawd/
cp reference/* ~/clawd/reference/
```

## Step 4: Install Custom Skills
```bash
cp -r skills-custom/* ~/clawd/skills/
```

## Step 5: Get Your API Keys

Replace every `REPLACE_ME` in `~/.openclaw/openclaw.json` with real keys.

### Required (your agent won't work without these)

| # | Service | What For | Where to Get | Cost |
|---|---------|----------|-------------|------|
| 1 | **Anthropic** | Main AI brain (Claude Sonnet) | console.anthropic.com -> API Keys | Pay-as-you-go (~$10-30/mo typical) |
| 2 | **OpenAI** | Fallback model + Whisper transcription | platform.openai.com -> API Keys | Pay-as-you-go (~$5-15/mo) |
| 3 | **Google/Gemini** | Fast fallback + research | aistudio.google.com -> Get API Key | Free tier available |
| 4 | **Brave Search** | Web search for research | brave.com/search/api | Free tier: 2,000 queries/mo |

### Recommended (unlocks key features)

| # | Service | What For | Where to Get | Cost |
|---|---------|----------|-------------|------|
| 5 | **Notion** | Pipeline tracking, task management | notion.so/my-integrations -> New Integration | Free |
| 6 | **Slack** | Team notifications + alerts | api.slack.com -> Create App -> Bot Token | Free |
| 7 | **Resend** | Morning/evening summary emails | resend.com -> API Keys | Free tier: 100 emails/day |
| 8 | **GitHub PAT** | Code repos + version control | github.com/settings/tokens -> Fine-grained | Free |
| 9 | **Perplexity** | Deep research with citations | perplexity.ai -> API -> Generate Key | $5/mo (Pro includes API) |
| 10 | **Google OAuth** | Gmail + Calendar + Drive access | console.cloud.google.com -> Credentials | Free |

### Optional (nice to have)

| # | Service | What For | Where to Get | Cost |
|---|---------|----------|-------------|------|
| 11 | Vercel | Auto-deploy websites/tools | vercel.com/account/tokens | Free tier |
| 12 | ElevenLabs | Voice/text-to-speech | elevenlabs.io | Free tier |
| 13 | Firecrawl | Web scraping for competitor research | firecrawl.dev | Free tier: 500 pages/mo |
| 14 | Cloudflare | DNS management + tunnels | dash.cloudflare.com -> API Tokens | Free |
| 15 | Apify | Web scraping + data extraction | console.apify.com -> Settings -> API | Free tier: 30 actor runs/day |
| 16 | Webflow | Website management + CMS | webflow.com -> Account Settings -> API Access | Free with site plan |

### Chat Channel (pick ONE to start)

| Channel | Best For | Setup |
|---------|----------|-------|
| **Telegram** | Easiest to set up | BotFather -> /newbot -> copy token |
| **Discord** | Team channels | discord.com/developers -> New App -> Bot Token |
| **WhatsApp** | Personal/mobile | Requires WhatsApp bridge setup |
| **Slack** | Already using Slack | Same app from #6 above |

**Start with Telegram** -- it's literally 2 minutes to set up and you can always add more channels later.

### Quick Start Priority

If you want to get running fast, these 5 keys get 80% of the value:
1. **Anthropic** (the brain)
2. **Brave Search** (web access)
3. **Telegram bot token** (chat channel)
4. **Notion** (pipeline tracking)
5. **Resend** (email summaries)

## Step 5b: MCP Servers (Optional Power-Ups)

MCP (Model Context Protocol) servers give your agent direct access to tools without going through APIs. These are local processes that run alongside OpenClaw.

| MCP Server | What For | Install | Priority |
|------------|----------|---------|----------|
| **Notion MCP** | Direct Notion read/write (faster than API) | `npx @notionhq/notion-mcp` | High -- if using Notion for pipeline |
| **Slack MCP** | Richer Slack integration | `npx @anthropic/slack-mcp` | Medium -- skill already covers basics |
| **Filesystem MCP** | Safe file access for documents | `npx @anthropic/filesystem-mcp` | Medium -- useful for document drafts |
| **Google Drive MCP** | Direct Drive access for documents | `npx @anthropic/gdrive-mcp` | High -- if documents live in Drive |
| **Figma MCP** | Read Figma files for design handoff | `npx figma-mcp` | Low -- only if doing design work |
| **Browser MCP** | Headless browsing for deep research | `npx @anthropic/browser-mcp` | Low -- Brave search handles most research |

**Start with zero MCPs.** Add Notion + Google Drive later if your agent feels slow on those integrations. The built-in skills handle 90% of needs without MCPs.

## Step 5c: OAuth Setups

| Service | What For | Setup Steps |
|---------|----------|-------------|
| **Google OAuth** | Gmail, Calendar, Drive access | 1. console.cloud.google.com -> New Project -> Enable Gmail/Calendar/Drive APIs -> Create OAuth credentials -> Download JSON -> Place at `~/.config/gog/credentials.json` |
| **Slack App** | Bot token + incoming webhooks | 1. api.slack.com/apps -> Create New App -> Bot Token Scopes: `chat:write`, `channels:read`, `files:write` -> Install to Workspace -> Copy Bot Token |
| **Notion Integration** | Database access | 1. notion.so/my-integrations -> New -> Give it access to your workspace -> Copy Internal Integration Token -> Share target databases with the integration |

## Step 6: Personalize
1. Edit `~/clawd/USER.md` -- Tell the agent about yourself
2. Edit `~/clawd/SOUL.md` -- Define the agent's personality
3. Edit `~/clawd/IDENTITY.md` -- Name your agent
4. Edit `~/clawd/AGENTS.md` -- Operating instructions (this one's 90% ready to go)

## Step 7: Start
```bash
openclaw gateway start
```

## Pro Tips
- The `AGENTS.md` file is the brain -- it tells the agent HOW to operate
- The `SOUL.md` file is the personality -- it tells the agent WHO to be
- The `HEARTBEAT.md` file defines what happens on idle check-ins
- Custom skills in `skills/` extend capabilities (SEO, social, email, etc.)
- Start with 2-3 crons, scale up as you trust it
- Use `memory/YYYY-MM-DD.md` daily logs for continuity across sessions
