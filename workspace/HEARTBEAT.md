# HEARTBEAT.md — Scheduled Operations

{{AGENT_NAME}} runs periodic checks to keep your business on track. **These are configured automatically during onboarding — you just approve which ones you want.**

---

## How It Works

During onboarding, {{AGENT_NAME}} will offer to set up your "autopilot" — recurring jobs that run in the background. You pick which ones to activate. No terminal, no code, no commands.

Each job runs in an isolated background session so it never interrupts your active conversation.

**Timezone note:** All times below are in MST (America/Denver). {{AGENT_NAME}} will adjust to your timezone during setup. MST is UTC-7, so 7am MST = 2pm UTC.

---

## Essential Jobs (Recommended for Everyone)

These 5 jobs cover 90% of what a business operator needs. Start here.

### 1. Morning Briefing — 7:00 AM Weekdays

Your daily "here's what matters today" summary. Covers active deadlines, open tasks, new opportunities found overnight, and actions needed today. Posted to your preferred channel (Slack, chat, etc.) in a format you can scan in 60 seconds.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "morning-briefing",
  "message": "Deliver the morning briefing. Read memory/pipeline.md for active opportunities and deadline status. Read memory/active-tasks.md for open action items. Read yesterday's and today's memory/YYYY-MM-DD.md for recent context. Flag any deadlines within 7 days (urgent at 3 days, emergency at 1 day). Post a clean, scannable summary. Format: MORNING BRIEF — [Date] | DEADLINES | ACTIVE WORK | NEW OPPORTUNITIES | ACTIONS NEEDED. Keep it tight — {{USER_NAME}} should scan this in 60 seconds."
}
```

**Cron:** `0 14 * * 1-5`

---

### 2. Opportunity / Lead Scan — 6:00 AM Daily

Checks your configured data sources (web, industry sites, job boards, whatever applies) for new opportunities posted in the last 24 hours. Deduplicates against your existing pipeline and scores by relevance.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "daily-pipeline-scan",
  "message": "Run the daily pipeline and opportunity scan. Check all configured data sources for new leads, opportunities, or relevant listings posted in the last 24 hours. Cross-reference against memory/pipeline.md to deduplicate. Score and rank new findings by relevance to {{YOUR_COMPANY}}'s target market and capabilities. Write results to memory/scan-YYYY-MM-DD.md. If high-value opportunities are found, flag them for inclusion in the morning briefing."
}
```

**Cron:** `0 13 * * *`

---

### 3. Deadline Watch — Every 4 Hours

Monitors all tracked deadlines and escalates as they approach. 7 days out = logged. 3 days = urgent alert. 24 hours = direct message. Under 6 hours = emergency on all channels.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "deadline-watch",
  "message": "Check all tracked deadlines. Read memory/pipeline.md and memory/active-tasks.md for items with due dates. Calculate days remaining for each. Alert thresholds: 7 days — include in next morning briefing. 3 days — post to alerts with URGENT flag. 24 hours — alert plus direct message to {{USER_NAME}}. Under 6 hours — emergency alert on all channels. Skip items marked as Completed, Cancelled, or On Hold."
}
```

**Cron:** `0 13,17,21,1,5 * * *`

---

### 4. Weekly Review — Monday 8:30 AM

Every Monday, get a full picture: how many deals are in each stage, what went stale, what needs follow-up, and whether your pipeline is healthy enough to hit revenue targets.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "weekly-review",
  "message": "Run the weekly review. Count all opportunities and projects by stage: Prospecting, Qualifying, Active, Delivered, Won, Lost, Stalled. Flag any stale items (no status update in 7+ days). Check for completed projects that need follow-up. Review pipeline health: are there enough opportunities in early stages? Generate recommendations for the week. Post full summary to alerts."
}
```

**Cron:** `30 15 * * 1`

---

### 5. Night Cleanup — 2:00 AM Daily

Housekeeping that runs while you sleep. Archives old memory files, cleans temp files, checks API health, compacts memory if it's getting large, and makes sure everything is ready for tomorrow's morning briefing.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "night-cleanup",
  "message": "Run the night cleanup. (1) ARCHIVE — For memory files older than 30 days, extract key facts to MEMORY.md and compress to a one-line summary. (2) CLEANUP — Remove temp files older than 7 days and stale scan results older than 14 days. (3) API HEALTH — Ping configured APIs, log failures to memory/incidents.md. (4) MEMORY COMPACTION — If MEMORY.md exceeds 200 lines, compress oldest sections while preserving key facts. (5) Verify pipeline.md and active-tasks.md are current. Flag zombie tasks (in-progress with no update in 7+ days). Write brief health report to today's memory file."
}
```

**Cron:** `0 9 * * *`

---

## Advanced Jobs (Add When Ready)

These are powerful but optional. Add them once you're comfortable with the essentials.

### 6. Competitor Watch — Wednesday 2:00 PM

Weekly scan of competitor activity: news, announcements, hires, pricing changes, client wins.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "competitor-watch",
  "message": "Run the weekly competitor watch. Search for news and market activity from known competitors (check MEMORY.md for competitor list). Look for product launches, funding, key hires, pricing changes, or major client wins. Check industry news for trends. Log findings to memory/competitor-watch-YYYY-MM-DD.md and post highlights to research channel."
}
```

**Cron:** `0 21 * * 3`

---

### 7. Self-Learning Review — 10:00 PM Daily

Reviews the day's conversations and extracts preferences, tool issues, and patterns to get smarter over time.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "self-learning-review",
  "message": "Run the daily self-learning review. Read today's memory file. Extract: (1) NEW PREFERENCES — Did {{USER_NAME}} express corrections or opinions? Update SOUL.md or USER.md. (2) TOOL GOTCHAS — Document any tool failures or workarounds in reference/learnings.md. (3) PATTERNS — Track recurring task types that could be automated. (4) KNOWLEDGE GAPS — Note questions you couldn't answer in memory/knowledge-gaps.md. Write a brief Day in Review section to today's memory file."
}
```

**Cron:** `0 5 * * *`

---

### 8. Monthly Performance — 1st of Month, 9:00 AM

Analyzes 90 days of pipeline data to show win rates, patterns in wins vs losses, and systemic issues.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "monthly-performance",
  "message": "Run the monthly performance analysis. Pull opportunities and projects from the past 90 days. Calculate win rate. Identify patterns: which types, segments, and value ranges perform best vs worst. Note common themes in wins vs losses. Update performance metrics in MEMORY.md. Generate a concise monthly report. Flag systemic issues (losing on price, slow response, specific competitor winning)."
}
```

**Cron:** `0 16 1 * *`

---

### 9. Cron Doctor — Every 2 Hours

Self-healing monitor that watches all other cron jobs for failures and attempts automatic fixes before escalating to you.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "cron-doctor",
  "message": "Run the Cron Doctor. Review cron logs for failed or missed jobs. For each failure: diagnose (timeout? bad payload? API down?), attempt fix, log to memory/incidents.md. Track attempts — after 3 failed fixes on the same job, escalate to {{USER_NAME}} with plain-language explanation. Do NOT alert for transient failures already fixed."
}
```

**Cron:** `0 15,17,19,21,23,1,3 * * *`

---

### 10. Self-Improvement Review — Friday 4:00 PM

Weekly audit of what's working, what's not, and what to improve. Reviews slowest tasks, repeated corrections, cron value, and unused skills.

```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "self-improvement-review",
  "message": "Run the weekly self-improvement review. Analyze the past 7 days: (1) SLOWEST TASKS — What took longest? Could it be automated? (2) REPETITIONS — Did {{USER_NAME}} have to repeat or correct anything? Close the gap. (3) CRON VALUE — Which jobs produced actionable output? Which were empty? Recommend adjustments. (4) UNUSED SKILLS — Disable overhead, suggest missing ones. (5) NEW CAPABILITY — What one addition would have the highest ROI? Present concise bullet-point recommendations to {{USER_NAME}}."
}
```

**Cron:** `0 23 * * 5`

---

## Schedule Summary

| # | Job | Schedule | Tier |
|---|-----|---------|------|
| 1 | Morning Briefing | 7:00 AM weekdays | Essential |
| 2 | Opportunity Scan | 6:00 AM daily | Essential |
| 3 | Deadline Watch | Every 4h | Essential |
| 4 | Weekly Review | Monday 8:30 AM | Essential |
| 5 | Night Cleanup | 2:00 AM daily | Essential |
| 6 | Competitor Watch | Wednesday 2:00 PM | Advanced |
| 7 | Self-Learning | 10:00 PM daily | Advanced |
| 8 | Monthly Performance | 1st of month 9:00 AM | Advanced |
| 9 | Cron Doctor | Every 2h | Advanced |
| 10 | Self-Improvement | Friday 4:00 PM | Advanced |

**Start with the 5 Essential jobs. Add Advanced jobs as you get comfortable.**

---

## Notes for {{AGENT_NAME}}

- All crons use `sessionTarget: "isolated"` — they run in background, never interrupt active chat
- Log each cron run to `memory/YYYY-MM-DD.md`
- If a job fails, log to `memory/incidents.md` and mention in next morning briefing
- Do not re-alert on the same item more than once per threshold
- {{AGENT_NAME}} configures these during onboarding — {{USER_NAME}} approves, {{AGENT_NAME}} activates
- Pipeline scan only flags a message if there are genuinely relevant new findings — silence is valid
