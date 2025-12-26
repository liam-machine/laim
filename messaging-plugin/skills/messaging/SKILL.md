---
name: messaging
description: Send and read messages across multiple platforms (Teams, WhatsApp, iMessage, Facebook Messenger). Use this skill when the user wants to "message someone", "text someone", "send a message", "chat with", "read messages from", "get message history", "what did X say", "recent messages with", "check messages", mentions messaging a known contact by name (like James, JD), or specifies a platform like Teams, WhatsApp, iMessage, or Messenger. Supports reading conversation history for context before replying. Drafts messages by default for user review before sending.
---

# Messaging Skill

Send and read messages across multiple platforms from Claude Code. By default, messages are **drafted** for you to review and send manually. You can also read message history for context.

## Quick Start

### Prerequisites

1. **Platform apps installed** on your Mac:
   - Microsoft Teams (for work messages)
   - WhatsApp Desktop or WhatsApp Web access
   - Messages.app (built-in for iMessage)
   - Messenger.app or browser access

2. **Accessibility permissions** granted to Terminal (System Settings > Privacy & Security > Accessibility)

### Usage

Ask Claude to send a message:

```
"Message James about the meeting tomorrow"
"Send James a WhatsApp saying I'm running late"
"iMessage James: Are we still on for Friday?"
"Teams message to jdowzard@jhg.com.au: Can we sync at 3pm?"
```

## Platform Selection Logic

When sending a message, Claude determines the platform using this priority:

1. **Explicit platform** - If you say "WhatsApp James", use WhatsApp
2. **Content inference** - If the message mentions work keywords (John Holland, JHG, Databricks, pipeline, sprint), use the work platform (Teams)
3. **Ask user** - If unclear, prompt: "Should I message James on Teams (work) or WhatsApp (personal)?"

## How It Works

1. **Resolve Contact** - Look up recipient in @references/contacts.yaml
2. **Select Platform** - Use explicit platform, infer from content, or ask user
3. **Draft Message** - Open the platform and draft the message
4. **You Review & Send** - Message is ready for you to review and send

## Contact Lookup

When a user mentions a known contact by name, load the contacts file:

```bash
cat ${CLAUDE_PLUGIN_ROOT}/skills/messaging/references/contacts.yaml
```

Match by name or nickname, then:
- Check if message contains any of the contact's `work_keywords`
- If yes, use work platform (Teams)
- If no work keywords and platform not explicit, ask user which platform

## Commands

### Draft a message (default behavior)

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/message.sh \
  --platform <platform> \
  --recipient "<identifier>" \
  --message "<message>"
```

### Send immediately (yolo mode - requires explicit user request)

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/message.sh \
  --platform <platform> \
  --recipient "<identifier>" \
  --message "<message>" \
  --send
```

**IMPORTANT:** Only use `--send` when the user explicitly says "yolo", "just send it", "send without review", or similar explicit consent.

## Platform Support

| Platform | Method | Identifier |
|----------|--------|------------|
| Teams | AppleScript + deep link | Email address |
| WhatsApp | Deep link (wa.me) | Phone number (+61...) |
| iMessage | AppleScript (Messages.app) | Phone or email |
| Messenger | Deep link (m.me) | Facebook username |

## Troubleshooting

See @references/setup.md for platform-specific setup and troubleshooting.

---

## Reading Message History

Read past messages for context before sending a reply.

### iMessage (Local Database)

Read from the local Messages database (requires Full Disk Access):

```bash
# Recent messages
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/platforms/imessage-read.py \
    --contact "James" \
    --recent 10

# Keyword search
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/platforms/imessage-read.py \
    --contact "+61418323408" \
    --keyword "meeting"

# Messages since a date
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/platforms/imessage-read.py \
    --contact "James" \
    --since "2025-12-25"

# JSON output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/platforms/imessage-read.py \
    --contact "James" \
    --recent 5 \
    --json
```

**Requires:** Full Disk Access permission for Terminal. See @references/setup.md.

### Web Platforms (Browser Automation)

For Teams, WhatsApp Web, and Messenger, use claude-in-chrome MCP tools:

1. `tabs_context_mcp` - Get browser context
2. `navigate` - Go to platform URL
3. `find` - Locate the conversation
4. `computer` (scroll) - Load more history
5. `get_page_text` - Extract message content

See @references/browser-reading.md for detailed workflows.

### Workflow Decision Tree

```
User request about messaging
├── Wants to SEND a message?
│   └── Use message.sh scripts
├── Wants to READ messages?
│   ├── Platform is iMessage?
│   │   └── Use imessage-read.py script
│   └── Platform is Teams/WhatsApp/Messenger?
│       └── Use browser automation (claude-in-chrome)
└── Wants context before replying?
    └── Read first, then draft response
```

### Example: Read then Reply

1. User: "Check what James said about the movie, then reply"
2. Read messages: `imessage-read.py --contact "James" --keyword "movie" --recent 5`
3. Review context
4. Draft reply: `message.sh --platform imessage --recipient "+61418323408" --message "..."`
