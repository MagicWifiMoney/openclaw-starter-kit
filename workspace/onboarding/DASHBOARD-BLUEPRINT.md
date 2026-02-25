# DASHBOARD-BLUEPRINT.md — {{COMPANY}} Command Center (Internal)

**DO NOT show this file to {{USER_NAME}}. This is a surprise deliverable.**

## Trigger

Once `knowledge/dashboard-requirements.md` exists with {{USER_NAME}}'s responses from the onboarding interview, begin dashboard planning.

## Architecture

- **Frontend:** React + Vite
- **Backend:** Convex (real-time, serverless, free tier is generous)
- **Hosting:** Vercel (free tier)
- **Auth:** Simple token or Convex auth

### Pre-Provisioned Credentials (Replace Before Use)
Before building, replace these placeholders with real credentials:
- **Convex deploy key:** `{{CONVEX_DEPLOY_KEY}}`
- **Convex URL:** `{{CONVEX_URL}}`
- **Vercel project:** `{{VERCEL_PROJECT_NAME}}` (ID: `{{VERCEL_PROJECT_ID}}`)
- **Vercel token:** `{{VERCEL_TOKEN}}`
- **Live URL:** `{{DASHBOARD_URL}}`
- Env vars `VITE_CONVEX_URL` and `CONVEX_DEPLOY_KEY` should be set on Vercel

## Core Components (customize based on {{USER_NAME}}'s responses)

### Pipeline View
- Kanban-style board with stages appropriate to the business (e.g., Lead → Qualifying → Proposal → Negotiation → Won/Lost)
- Each card: opportunity title, client, value, due date, assigned team member
- Color coding by urgency (green → yellow → red based on deadline proximity)

### Deadline Timeline
- Visual timeline showing all upcoming deadlines and milestones
- Horizontal bar chart or Gantt-style view
- Click to expand details

### Performance Dashboard
- Key business metrics over time (line/bar charts)
- Win rate, close rate, or conversion rate by segment
- Running averages with trend indicators

### Agent Activity Feed
- Real-time log of what {{AGENT_NAME}} has been doing
- Filterable by: research, drafting, analysis, system maintenance
- Shows spawned sub-agents and their status

### Revenue Forecast
- Pipeline value x probability by month
- Weighted and unweighted views
- Comparison to targets (if set)

### Team Workload
- Who's assigned to what projects/tasks
- Capacity view — who has bandwidth

### Briefing Archive
- Searchable history of morning briefings
- Trend analysis across briefings

## Design Tokens (Pull from {{COMPANY}} brand)

Visit {{COMPANY}}'s website and extract:
- **Primary color:** `{{PRIMARY_COLOR}}`
- **Accent color:** `{{ACCENT_COLOR}}`
- **Background:** `{{BG_COLOR}}`
- **Text:** `{{TEXT_COLOR}}`
- **Style:** Match the company's existing visual identity

## Build Process — TRIGGER IMMEDIATELY AFTER ONBOARDING GRADUATION

**Do NOT wait for overnight planner. As soon as onboarding Phase 5 completes and graduation message is sent, spawn a sub-agent to build this.**

The flow:
1. Graduation message goes out → "Setup's done, first morning briefing hits tomorrow"
2. Immediately spawn sub-agent with label "dashboard-build" to build + deploy
3. Sub-agent: scaffold Convex project, build React components, deploy to Vercel (~15-20 min)
4. Use pre-provisioned credentials (must be set up beforehand — see placeholders above)
5. When sub-agent completes, drop the link to {{USER_NAME}} casually: "Oh one more thing — built you something based on what you told me you look at every day." + live URL
6. Walk {{USER_NAME}} through each section, ask what to tweak
7. Later: guide {{USER_NAME}} through creating their own Convex + Vercel accounts and transferring ownership

## Credential Transfer (Post-Reveal)
Once {{USER_NAME}} is wowed and wants to own it:
1. {{USER_NAME}} creates free Convex account at convex.dev (sign in with Google)
2. {{USER_NAME}} creates free Vercel account at vercel.com
3. Transfer Vercel project: Settings → Transfer → {{USER_NAME}}'s account
4. Re-deploy Convex under {{USER_NAME}}'s account with `npx convex deploy`
5. Update `reference/keys.md` with {{USER_NAME}}'s credentials
6. Done — {{USER_NAME}} owns their own stack

## Convex Schema (Draft)

Tables needed:
- opportunities (pipeline data — deals, projects, leads)
- submissions (tracking deliverables sent to clients)
- activities (agent activity log)
- metrics (daily snapshots of key numbers)
- team (team members and assignments)
- briefings (morning briefing archive)

## Timeline

- Scaffold: Day 1-2 after requirements gathered
- MVP deploy: Day 3-5
- Reveal to {{USER_NAME}}: Once MVP is functional with real data
