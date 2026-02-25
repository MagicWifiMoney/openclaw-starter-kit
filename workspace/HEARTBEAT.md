# HEARTBEAT.md — Scheduled Operations

{{AGENT_NAME}} runs periodic checks to keep the business pipeline current, surface opportunities, and protect against missed deadlines. **These cron jobs are configured automatically during onboarding — {{USER_NAME}} does not need a terminal or command line.**

---

## How Cron Setup Works

During onboarding, {{AGENT_NAME}} will configure all recurring jobs using the built-in cron tool. {{USER_NAME}} approves which jobs to activate; {{AGENT_NAME}} does the rest. No commands to run, no terminal required.

Each job uses `agentTurn` payload type with `sessionTarget: "isolated"` so it runs in a clean, background session without interrupting active conversations.

**Timezone note:** All times below are in MST (America/Denver). Adjust the UTC cron expressions to match your timezone. The formula: `UTC hour = your local hour + offset from UTC`. MST is UTC-7, so 7am MST = 2pm UTC (14:00).

---

## Scheduled Jobs

### 1. Morning Briefing — 7:00 AM MST (Weekdays)

**Cron expression:** `0 14 * * 1-5` (UTC equivalent of 7am MST, Mon-Fri)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "morning-briefing",
  "message": "Deliver the morning briefing. Read memory/pipeline.md for active opportunities and deadline status. Read memory/active-tasks.md for open action items. Read yesterday's and today's memory/YYYY-MM-DD.md for recent context. Flag any deadlines within 7 days (urgent at 3 days, emergency at 1 day). Post a clean, scannable summary to Slack #alerts. Format: MORNING BRIEF — [Date] | DEADLINES | ACTIVE WORK | NEW OPPORTUNITIES | ACTIONS NEEDED. Keep it tight — {{USER_NAME}} should scan this in 60 seconds."
}
```

---

### 2. Pipeline / Opportunity Scan — 6:00 AM MST Daily

**Cron expression:** `0 13 * * *` (UTC equivalent of 6am MST)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "daily-pipeline-scan",
  "message": "Run the daily pipeline and opportunity scan. Check all configured data sources for new leads, opportunities, or relevant listings posted in the last 24 hours. Cross-reference against memory/pipeline.md to deduplicate. Score and rank new findings by relevance to {{YOUR_COMPANY}}'s target market and capabilities. Write results to memory/scan-YYYY-MM-DD.md. If high-value opportunities are found, flag them for inclusion in the morning briefing."
}
```

---

### 3. Deadline Watch — Every 4 Hours (6 AM-10 PM MST)

**Cron expression:** `0 13,17,21,1,5 * * *` (UTC: covers 6am-10pm MST)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "deadline-watch",
  "message": "Check all tracked deadlines. Read memory/pipeline.md and memory/active-tasks.md for items with due dates. Calculate days remaining for each. Alert thresholds: 7 days out — log to daily file and include in next morning briefing. 3 days out — post to Slack #alerts with URGENT flag. 24 hours out — post to Slack #alerts AND send direct message to {{USER_NAME}}. Under 6 hours — emergency alert on all channels. Skip items marked as Completed, Cancelled, or On Hold."
}
```

---

### 4. Weekly Review — Monday 8:30 AM MST

**Cron expression:** `30 15 * * 1` (UTC equivalent of 8:30am MST Monday)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "weekly-review",
  "message": "Run the weekly review. Count all opportunities and projects by stage: Prospecting, Qualifying, Active, Delivered, Won, Lost, Stalled. Flag any stale items (no status update in 7+ days). Check for completed projects that need follow-up or lessons-learned capture. Review pipeline health: are there enough opportunities in early stages to sustain revenue targets? Generate recommendations for the week based on gaps. Post full summary to Slack #alerts."
}
```

---

### 5. System Health — 11:00 PM MST Daily

**Cron expression:** `0 6 * * *` (UTC equivalent of 11pm MST)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "system-health",
  "message": "Run system health check. Verify workspace disk usage is under 80%. Confirm today's memory/YYYY-MM-DD.md exists and is writable. Confirm memory/active-tasks.md and memory/pipeline.md are accessible. Ping all configured APIs (check reference/keys.md for the list) for availability — log any failures to memory/incidents.md. Archive any temp files older than 7 days. Log a brief health summary to today's daily memory file."
}
```

---

### 6. Knowledge Freshness — Sunday 9:00 AM MST

**Cron expression:** `0 16 * * 0` (UTC equivalent of 9am MST Sunday)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "knowledge-freshness",
  "message": "Run the weekly knowledge freshness check. Review MEMORY.md last-updated date — flag if stale (not updated in 14+ days). Check the contacts list for people not touched in 90+ days and suggest re-engagement. Check all tracked certifications, licenses, and registrations for upcoming renewals (alert if within 60 days). Review API key expiry tracking table — alert if any key expires within 30 days. Based on recent patterns, suggest any certifications or registrations worth pursuing. Log findings to today's memory file."
}
```

---

### 7. Competitor Watch — Wednesday 2:00 PM MST

**Cron expression:** `0 21 * * 3` (UTC equivalent of 2pm MST Wednesday)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "competitor-watch",
  "message": "Run the weekly competitor watch. Search for news, announcements, and market activity from known competitors (check MEMORY.md for competitor list). Look for new product launches, funding announcements, key hires, pricing changes, or major client wins. Check industry news sources for trends affecting {{YOUR_COMPANY}}'s market. Cross-reference with known competitive positioning in MEMORY.md. Log findings to memory/competitor-watch-YYYY-MM-DD.md and post highlights to Slack #research."
}
```

---

### 8. Monthly Performance — 1st of Month, 9:00 AM MST

**Cron expression:** `0 16 1 * *` (UTC equivalent of 9am MST on 1st of month)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "monthly-performance",
  "message": "Run the monthly performance analysis. Pull all opportunities and projects from the past 90 days via memory/pipeline.md and daily memory files. Calculate win rate (won / total pursued). Identify patterns: which types of opportunities, which segments, which value ranges are performing best vs worst. Note any common themes in wins vs losses (if lessons have been logged). Update performance metrics in MEMORY.md. Generate a concise monthly performance report and post to Slack #alerts. Flag any systemic issues (e.g., consistently losing on price, slow response times, particular competitor winning repeatedly)."
}
```

---

### 9. Cron Doctor — Every 2 Hours, 8:00 AM-10:00 PM MST

**Cron expression:** `0 15,17,19,21,23,1,3 * * *` (UTC: covers 8am-10pm MST)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "cron-doctor",
  "message": "Run the Cron Doctor health sweep. Review the cron run log in memory/cron-runs.md (or today's daily memory file) and identify any jobs that have failed, timed out, or not run at their expected time. For each failed job: (1) Diagnose the failure — timeout? bad payload? API unavailable? parsing error? (2) Attempt a fix: if timeout, increase timeout parameter; if bad payload, correct the JSON; if API is down, log the outage to memory/incidents.md and set a flag to retry next cycle; if parsing error, fix the payload format. (3) Log the fix attempt to memory/incidents.md with timestamp, job name, error, and action taken. (4) Track attempt count per incident — if the same job has failed and been fixed 3 times without recovery, escalate to {{USER_NAME}} with a plain-language explanation of what's broken and why you can't fix it automatically. Do NOT alert {{USER_NAME}} for transient failures you've already fixed. Stay quiet unless truly stuck after 3 attempts."
}
```

---

### 10. Self-Learning Review — Daily 10:00 PM MST

**Cron expression:** `0 5 * * *` (UTC equivalent of 10pm MST)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "self-learning-review",
  "message": "Run the daily self-learning review. Read today's memory/YYYY-MM-DD.md (use actual today's date) and any conversation logs from the day. Extract and act on the following: (1) NEW PREFERENCES — Did {{USER_NAME}} express any preferences, corrections, or strong opinions today? If yes, update SOUL.md or USER.md with those preferences. Flag the update in today's memory file. (2) TOOL GOTCHAS — Did any tool fail in an unexpected way, or produce output that required a workaround? Document the gotcha in reference/learnings.md with: tool name, what went wrong, and the fix. (3) PATTERNS — What types of tasks did {{USER_NAME}} ask for today? Track patterns across days to identify recurring work that could be automated or templated. Note patterns in today's memory file. (4) KNOWLEDGE GAPS — Were there any questions you couldn't answer, data you couldn't access, or research you had to skip? Note these as intake priorities in memory/knowledge-gaps.md (create if doesn't exist). (5) Write a structured 'Day in Review' section to today's memory/YYYY-MM-DD.md. (6) If any finding is durable (recurring pattern, important preference, new contact), also update MEMORY.md."
}
```

---

### 11. Night Cleanup — Daily 2:00 AM MST

**Cron expression:** `0 9 * * *` (UTC equivalent of 2am MST)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "night-cleanup",
  "message": "Run the night cleanup and health audit. Work through this checklist: (1) ARCHIVE OLD MEMORY — List all files in memory/ matching YYYY-MM-DD.md. For any file older than 30 days: read it, extract the 3-5 most important durable facts (lessons, decisions, milestones, contacts), append those facts to MEMORY.md under a dated section, then compress the original file to a one-line summary (keeping file in place for reference). (2) TEMP CLEANUP — Remove or archive any temp files older than 7 days. Remove stale scan result files (scan-*.md older than 14 days). Delete any orphaned drafts that haven't been touched in 30+ days and aren't tracked in pipeline.md. (3) API HEALTH — Ping each configured API (check reference/keys.md) to verify it still works. Log failures to memory/incidents.md. (4) DISK USAGE — Check workspace disk usage. If over 80%, identify the largest files/folders and log a cleanup recommendation. (5) MEMORY COMPACTION — Check MEMORY.md line count. If over 200 lines, identify the oldest or least-referenced sections and compress them while preserving key facts. (6) MORNING READINESS — Verify memory/pipeline.md is current and accessible. Verify memory/active-tasks.md has no zombie tasks (tasks marked in-progress with no update in 7+ days — flag them). Confirm the morning scan cron will have fresh API access. (7) Write a brief health report to today's memory/YYYY-MM-DD.md."
}
```

---

### 12. Self-Improvement Review — Friday 4:00 PM MST

**Cron expression:** `0 23 * * 5` (UTC equivalent of 4pm MST Friday)

**Payload:**
```json
{
  "type": "agentTurn",
  "sessionTarget": "isolated",
  "label": "self-improvement-review",
  "message": "Run the weekly self-improvement review. Analyze the past 7 days of memory files (memory/YYYY-MM-DD.md for Mon-Fri) and cron logs. Answer each question and produce a structured report: (1) SLOWEST TASKS — What tasks took the longest this week? Could any be templated, pre-computed, or automated via a new cron? Propose specific changes. (2) REPETITION GAPS — Did {{USER_NAME}} have to repeat an instruction, correct an output, or re-ask for something this week? Each repetition is a learning gap. Identify the gap and propose how to close it (update SOUL.md, update AGENTS.md, add to learnings.md, or build a template). (3) CRON VALUE AUDIT — Which cron jobs produced actionable output this week? Which ran but produced nothing useful (empty briefings, scans with no results, health checks with no findings)? Recommend: keep, adjust, reduce frequency, or disable. (4) UNUSED SKILLS — Which installed skills went unused this week? Should any be disabled to reduce overhead? Are there skills not installed that would have helped? (5) NEW CAPABILITIES — Based on this week's work, what new capability would have the highest ROI? (new skill, new cron, new template, new integration). (6) Write the full findings to today's memory/YYYY-MM-DD.md. Then present a CONCISE summary to {{USER_NAME}} with specific, actionable recommendations — not a wall of text. Format: bullet points, each recommendation with a single clear ask ('Want me to X?'). Lead with the highest-impact finding."
}
```

---

## Cron Schedule Summary

| # | Job | Schedule | Cron Expression (UTC) |
|---|-----|---------|----------------------|
| 1 | Morning Briefing | 7:00 AM MST weekdays | `0 14 * * 1-5` |
| 2 | Pipeline / Opportunity Scan | 6:00 AM MST daily | `0 13 * * *` |
| 3 | Deadline Watch | Every 4h, 6am-10pm MST | `0 13,17,21,1,5 * * *` |
| 4 | Weekly Review | Monday 8:30 AM MST | `30 15 * * 1` |
| 5 | System Health | 11:00 PM MST daily | `0 6 * * *` |
| 6 | Knowledge Freshness | Sunday 9:00 AM MST | `0 16 * * 0` |
| 7 | Competitor Watch | Wednesday 2:00 PM MST | `0 21 * * 3` |
| 8 | Monthly Performance | 1st of month, 9:00 AM MST | `0 16 1 * *` |
| 9 | Cron Doctor | Every 2h, 8am-10pm MST | `0 15,17,19,21,23,1,3 * * *` |
| 10 | Self-Learning Review | Daily 10:00 PM MST | `0 5 * * *` |
| 11 | Night Cleanup | Daily 2:00 AM MST | `0 9 * * *` |
| 12 | Self-Improvement Review | Friday 4:00 PM MST | `0 23 * * 5` |

**All times default to Mountain Standard Time (MST / America/Denver). Adjust UTC cron expressions to match your timezone.** The agent adjusts automatically for daylight saving if applicable.

---

## Notes for {{AGENT_NAME}}

- All crons use `sessionTarget: "isolated"` — they run in background, never interrupt {{USER_NAME}}'s active chat
- Log each cron run start/end to `memory/YYYY-MM-DD.md`
- If a job fails, log to `memory/incidents.md` and notify {{USER_NAME}} in next morning briefing
- Do not re-alert on the same item more than once per threshold (track in pipeline.md)
- {{AGENT_NAME}} configures these during onboarding — {{USER_NAME}} approves, {{AGENT_NAME}} activates
- Cron Doctor is self-healing — it monitors and fixes other cron failures automatically before escalating
- Pipeline scan only flags a message if there are genuinely relevant new findings — silence is valid
