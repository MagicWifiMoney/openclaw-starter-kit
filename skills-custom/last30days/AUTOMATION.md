# last30days - Automation Setup

## Weekly Pain Point Digest

**Recommended Schedule**: Sunday 3:00 PM CST  
**Purpose**: Scan niches for buildable problems, post high-priority opportunities to Slack

### Setup Cron

```json
{
  "name": "Weekly Pain Point Digest",
  "schedule": {
    "kind": "cron",
    "expr": "0 15 * * 0",
    "tz": "America/Chicago"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Run the pain point tracker and post results to Slack #botti-systems:\n\n1. Execute: node /home/ec2-user/clawd/scripts/pain-point-tracker.js\n2. Read the generated report from /home/ec2-user/clawd/memory/pain-point-reports/[today].md\n3. Extract high-priority opportunities\n4. Post summary to Slack channel C0AB08A0YAJ with:\n   - Top 3 trending niches\n   - High-priority opportunities (alerts)\n   - Links to full report\n\nFormat the Slack message as a digestible summary with clear action items.",
    "timeoutSeconds": 180
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce",
    "channel": "slack",
    "to": "C0AB08A0YAJ"
  },
  "enabled": true
}
```

### To Install:
```bash
# Save above JSON to file
cat > /tmp/weekly-digest-cron.json << 'EOF'
[paste JSON above]
EOF

# Add via OpenClaw
openclaw cron add --file /tmp/weekly-digest-cron.json
```

## Daily Dashboard Integration

Add pain point discovery to Tia's morning dashboard (or create new dashboard):

```javascript
// In dashboard script
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function getDailyPainPoints() {
  try {
    // Quick scan of top niches
    const niches = ['SaaS founders', 'GoHighLevel users', 'Next.js developers'];
    const results = await Promise.all(
      niches.map(async (niche) => {
        const { stdout } = await execPromise(
          `cd /home/ec2-user/clawd/skills/last30days && python3 scripts/hn_search.py "${niche}" --days 7 --limit 10`
        );
        return { niche, discussions: JSON.parse(stdout) };
      })
    );
    
    // Filter for high engagement
    return results
      .map(r => ({
        niche: r.niche,
        top: r.discussions
          .sort((a, b) => (b.points + b.comments) - (a.points + a.comments))
          .slice(0, 3)
      }))
      .filter(r => r.top.length > 0);
  } catch (error) {
    console.error('Error fetching pain points:', error);
    return [];
  }
}

// In dashboard output
const painPoints = await getDailyPainPoints();
if (painPoints.length > 0) {
  message += '\n\n🔍 **Trending Pain Points**\n';
  painPoints.forEach(({ niche, top }) => {
    message += `\n${niche}:\n`;
    top.forEach(d => {
      message += `• [${d.points}pts] ${d.title}\n`;
    });
  });
}
```

## Manual Research Shortcuts

Add these to `.bashrc` or `.zshrc`:

```bash
# Quick pain point search
alias pain='bash /home/ec2-user/clawd/scripts/research-pain-points.sh'

# Competitor intel
alias compete='bash /home/ec2-user/clawd/scripts/research-competitors.sh'

# Content validation
alias content='bash /home/ec2-user/clawd/scripts/research-content-ideas.sh'

# Full tracker run
alias track-pain='node /home/ec2-user/clawd/scripts/pain-point-tracker.js'
```

### Usage:
```bash
pain "SaaS founders analytics"
compete "Cursor IDE"
content "AI coding tools"
track-pain
```

## Notion Integration

Create a "Research Insights" database to store findings:

### Database Schema:
- **Title** (Title): Auto-generated from niche + date
- **Niche** (Select): Categorize by niche
- **Source** (Select): HN, SO, Reddit, etc.
- **Engagement** (Number): Average points + comments
- **Pain Signals** (Number): Count of problem-related discussions
- **Trending** (Checkbox): High engagement flag
- **Top Discussions** (Text): Top 3 links
- **Buildable Ideas** (Text): Specific opportunities identified
- **Date** (Date): When research was conducted

### Automation Script:
```javascript
// research-to-notion.js
const { Client } = require('@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_API_KEY });

async function saveResearchToNotion(niche, results, analysis) {
  const databaseId = 'YOUR_DATABASE_ID';
  
  await notion.pages.create({
    parent: { database_id: databaseId },
    properties: {
      'Title': {
        title: [{ text: { content: `${niche} - ${new Date().toISOString().split('T')[0]}` } }]
      },
      'Niche': {
        select: { name: niche }
      },
      'Engagement': {
        number: analysis.avgEngagement
      },
      'Pain Signals': {
        number: analysis.painSignals
      },
      'Trending': {
        checkbox: analysis.trending
      },
      'Date': {
        date: { start: new Date().toISOString().split('T')[0] }
      }
    },
    children: [
      {
        object: 'block',
        type: 'heading_2',
        heading_2: {
          rich_text: [{ type: 'text', text: { content: 'Top Discussions' } }]
        }
      },
      ...analysis.topDiscussions.map(d => ({
        object: 'block',
        type: 'bulleted_list_item',
        bulleted_list_item: {
          rich_text: [{
            type: 'text',
            text: { content: `[${d.points}pts, ${d.comments}cmt] ` }
          }, {
            type: 'text',
            text: { content: d.title, link: { url: d.hn_url } }
          }]
        }
      }))
    ]
  });
}
```

## Slack Alerts

Set up alerts for high-priority opportunities:

```javascript
// alert-high-priority.js
const { WebClient } = require('@slack/web-api');
const slack = new WebClient(process.env.SLACK_BOT_TOKEN);

async function alertHighPriority(alerts) {
  if (alerts.length === 0) return;
  
  const blocks = [
    {
      type: 'header',
      text: {
        type: 'plain_text',
        text: '🚨 High Priority Pain Points Detected'
      }
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `Found ${alerts.length} opportunities with high engagement or multiple pain signals:`
      }
    },
    ...alerts.map(alert => ({
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*${alert.niche}*\n• ${alert.reason}\n• ${alert.engagement} avg engagement\n• ${alert.painSignals} pain signals`
      }
    }))
  ];
  
  await slack.chat.postMessage({
    channel: 'C0AB08A0YAJ', // #botti-systems
    blocks
  });
}
```

## Example Workflows

### 1. Before Building a Product
```bash
# Validate the niche has active discussions
pain "your niche here"

# Check competitors
compete "competitor name"

# See if content about this topic resonates
content "your topic"
```

### 2. Weekly Research Routine
```bash
# Run full tracker (8 niches)
track-pain

# Review report
cat /home/ec2-user/clawd/memory/pain-point-reports/$(date +%Y-%m-%d).md

# Follow up on high-priority items
# (manually investigate HN threads, read discussions, validate ideas)
```

### 3. Content Planning
```bash
# Find trending topics
content "AI tools"

# Validate specific angle
pain "developers struggle with X"

# Check if anyone's written about it
compete "existing solution"
```

## Monitoring & Maintenance

### Check Report History:
```bash
ls -lh /home/ec2-user/clawd/memory/pain-point-reports/
```

### Review Recent Trends:
```bash
# Last 7 days of reports
tail -n 50 /home/ec2-user/clawd/memory/pain-point-reports/*.md
```

### Archive Old Reports (monthly):
```bash
# Create archives directory
mkdir -p /home/ec2-user/clawd/memory/pain-point-reports/archive

# Move reports older than 60 days
find /home/ec2-user/clawd/memory/pain-point-reports -name "*.md" -mtime +60 -exec mv {} /home/ec2-user/clawd/memory/pain-point-reports/archive/ \;
```

---

**Last updated**: Feb 6, 2026  
**Maintained by**: Botti
