# Overnight Content Generation Workflow

## When to Use
Batch content generation while Jake sleeps. Triggered by "overnight work", "batch content", or scheduled crons.

## Steps

### 1. Gather Requirements
- Which sites need content?
- Content types (blog posts, product pages, landing pages)
- Keywords/topics to target
- Affiliate tags to include (fifti00-20 for Fifti-Fifti)

### 2. Spawn Sub-Agents (Parallel)
For each site/content batch:
```javascript
// Schedule check-back FIRST
cron.add({
  schedule: { at: "<6am next morning>" },
  sessionTarget: "main",
  payload: { kind: "systemEvent", text: "OVERNIGHT CHECK: Review sub-agent results, compile report for Jake" }
})

// Then spawn per-site agents
sessions_spawn({ task: "...", label: "overnight-<site>-<date>" })
```

### 3. Sub-Agent Contract
Each sub-agent MUST:
- Write all content to `projects/<site>/output/`
- Create `manifest.md` listing all files
- Create `status.md` with completion state
- Include word counts, affiliate links, internal links in manifest

### 4. Morning Report
At 6am, compile results:
- Total content produced (word count, pages)
- Affiliate links inserted
- Any failures + what to retry
- Deliver to Jake via WhatsApp

## Success Criteria
- All sub-agents write to correct output dirs
- manifest.md created for each batch
- Morning report delivered by 6:30am
- No orphan files in /tmp or wrong directories
