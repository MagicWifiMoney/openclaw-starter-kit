---
name: memory-management
description: "Save, compact, and manage session memory. Use when: saving work before compact, switching contexts, spawning sub-agents, scheduling check-backs, or managing context limits. DON'T use when: just reading memory files (read them directly), quick lookups, or simple file operations."
---

# Memory Management Skill

## Save and Compact Protocol

**When to compact:**
- ✅ After major tasks complete
- ✅ Before switching contexts
- ✅ At 50k tokens (don't wait for 180k)
- ✅ When session feels "heavy"

**Protocol:**
1. `session_status(model="sonnet")`
2. Save to `memory/YYYY-MM-DD.md`: completed, in progress, pending, project context
3. Update MEMORY.md if significant
4. `session_status(model="opus")`
5. Confirm: "Ready to compact ✓"

## Sub-Agent Follow-Up (MANDATORY)

**The MAIN session schedules the check-back, NOT the sub-agent.**

When spawning a sub-agent with sessions_spawn:
1. **BEFORE spawning:** Schedule a check-back cron for estimated time + 5 min buffer
2. **Spawn the sub-agent** with the task
3. **Tell Jake** the ETA and that you'll check back

```javascript
// Step 1: Schedule check-back FIRST
cron.add({
  schedule: { at: "<now + estimated_time + 5min>" },
  sessionTarget: "main",
  payload: {
    kind: "systemEvent",
    text: "SUB-AGENT CHECK-IN: [Task name] should be done. Check sessions_list for status, deliver result to Jake via [channel]."
  }
})

// Step 2: Then spawn
sessions_spawn({ task: "...", label: "task-name" })
```

**Why main session, not sub-agent:**
- Sub-agent sessions can timeout, crash, or simply forget
- Crons scheduled by main session survive regardless
- Main session knows the delivery channel (WhatsApp, Slack, webchat)

**The check-back cron must:**
- Look up the sub-agent session by label
- Check if it completed (sessions_history)
- Deliver result OR report failure to Jake
- Delete itself after firing (one-shot)

## Context Safety Valve (MANDATORY)

**Check context at the START of every response.**

### Thresholds

| Session Type | At 50% | At 75% |
|--------------|--------|--------|
| **Main sessions** | ⚠️ Warn Jake | 🔄 Auto-compact (save first) |
| **Sub-agents** | ⚠️ Warn in output | ❌ Fail + return partial results |

### Main Session at 75% (auto-compact):
1. Save current work to `memory/YYYY-MM-DD.md`
2. Update MEMORY.md if significant
3. Switch to Sonnet, confirm "Ready to compact ✓"
4. Switch back to Opus after compact
5. Continue work

### Sub-Agent at 75% (fail fast):
```
⚠️ SUB-AGENT LIMIT: Hit 75% context before completing.
Partial results: [what was done]
Remaining: [what's left]
Recommendation: [how to continue]
```

## Async Task Enforcement (MANDATORY)

**Every time you promise "ready in X seconds/minutes":**

1. **IMMEDIATELY schedule a check-back cron:**
```javascript
cron.add({
  schedule: { at: "<now + X + 30 seconds>" },
  sessionTarget: "main",
  payload: {
    kind: "systemEvent",
    text: "CHECK-BACK: [Task name] for Jake - verify completion and deliver result to [channel]"
  }
})
```

2. **Never rely on session continuity** - sessions end, crons don't forget

**If the task fails or times out:**
- Still send an update: "Task X failed/timed out. Here's what happened: ..."
- Never leave Jake hanging

## Spawn sub-agents for:
- Complex multi-step tasks
- Parallel work
- Background analysis
- Anything >30 min of work

Sub-agents = fresh context, isolated tokens, no main session bloat.
