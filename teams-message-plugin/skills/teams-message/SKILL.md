---
name: teams-message
description: Draft and send Microsoft Teams messages to colleagues on macOS. Use this skill when the user wants to "send a Teams message", "message someone on Teams", "draft a Teams message", "Teams chat", or mentions sending messages to colleagues via Microsoft Teams. This skill opens the Teams app, navigates to the correct chat, and drafts the message for the user to review before sending.
---

# Teams Message Skill

Draft Microsoft Teams messages directly from Claude Code. The message is drafted in Teams for you to review and click Send.

## Quick Start

### Prerequisites

1. **Microsoft Teams** must be installed on your Mac
2. **Accessibility permissions** must be granted to Terminal (System Settings > Privacy & Security > Accessibility)

### Usage

Ask Claude to send a Teams message:

```
"Send a Teams message to john@company.com saying I'll be 10 minutes late"
"Message sarah@company.com on Teams about the project update"
"Draft a Teams message to the team lead about tomorrow's meeting"
```

Claude will execute:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/teams-message/scripts/teams-message.sh "recipient@email.com" "Your message here"
```

## How It Works

1. **Opens Teams** - Activates Microsoft Teams on your Mac
2. **Navigates to Chat** - Uses the `msteams://` deep link to open the correct chat
3. **Drafts Message** - Copies message to clipboard and pastes into compose box
4. **You Review & Send** - Message is ready for you to review and click Send

## Common Patterns

### Quick Message to Colleague
```
"Teams message to jdowzard@jhg.com.au: Can we sync up at 3pm?"
```

### Meeting Follow-up
```
"Send James a Teams message saying thanks for the meeting, I'll send the notes shortly"
```

### Status Update
```
"Message the team on Teams that the deployment is complete"
```

## Troubleshooting

### "osascript is not allowed to send keystrokes"

Grant Accessibility permissions:
1. Open System Settings > Privacy & Security > Accessibility
2. Click the lock icon to make changes
3. Add Terminal (or your terminal app) and toggle ON

### Teams doesn't open the correct chat

Verify the recipient email is correct and matches their Microsoft account.

### Message doesn't appear in compose box

1. Increase the delay in the AppleScript (edit `teams_draft_message.scpt`)
2. Ensure Teams is fully loaded before the paste action

## Configuration

No configuration required. The skill uses the recipient's email address to open the correct chat via Teams deep links.

## Limitations

- **macOS only** - Uses AppleScript which is macOS-specific
- **Teams desktop app required** - Does not work with Teams in browser
- **Manual send required** - By design, you must click Send to deliver the message
