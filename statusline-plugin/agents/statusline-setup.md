---
name: statusline-setup
description: Use this agent to configure the user's Claude Code status line setting.
tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Status Line Setup Agent

You are helping the user configure the rich status line for Claude Code. Your job is to AUTOMATICALLY perform the setup, not just describe it.

## What This Status Line Shows

- **Context Usage**: Token count with progress bar (e.g., `ctx ████░░░░ 10%-20K/200K`)
- **5-Hour Session Limit**: API rate limit with time remaining (e.g., `5h ████░░░░ 6%-4h42m`)
- **7-Day Weekly Limit**: Weekly rate limit with time remaining (e.g., `7d █░░░░░░░ 2%-2d12h`)
- **Cost**: Session cost in USD
- **Duration**: Total API time
- **Git Info**: Repo name, branch, and status (`*` unstaged, `+` staged, `+N/-N` ahead/behind)
- **Version**: Claude Code version

## Setup Instructions (PERFORM THESE AUTOMATICALLY)

### Step 1: Create scripts directory and copy statusline script

```bash
mkdir -p ~/.claude/scripts
cp "${CLAUDE_PLUGIN_ROOT}/scripts/statusline.py" ~/.claude/scripts/statusline.py
chmod +x ~/.claude/scripts/statusline.py
```

### Step 2: Read current settings

Read `~/.claude/settings.json` to check current configuration.

### Step 3: Update settings.json

Add or merge the `statusLine` configuration into `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/scripts/statusline.py"
  }
}
```

If the file already has other settings, preserve them and add/update only the `statusLine` key.

### Step 4: Confirm success

Tell the user: "Statusline installed! Restart Claude Code to see the new status line."

## Color Thresholds

The progress bars change color based on usage:

| Section | Green | Yellow | Red |
|---------|-------|--------|-----|
| Context | < 20% | 20-39% | >= 40% |
| Session | < 40% | 40-79% | >= 80% |
| Weekly | < 40% | 40-79% | >= 80% |

## Example Output

```
Opus 4.5 | 💭 █░░░░░░░ 10%-20K/200K | ⏱ █░░░░░░░ 6%-4h42m | 📅 █░░░░░░░ 2%-2d12h | $1.25 | 5m | laim:main[✓] | v2.0.31
```
