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

## Contact Resolution

When a user mentions a contact by name, use the smart lookup flow to avoid loading the full contacts file:

### Step 1: Lookup Known Contacts

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/lookup-contact.py --name "<contact name>"
```

Returns JSON with contact details if found, or `{"found": false}` if not.

### Step 2: Auto-Discover Unknown Contacts

If lookup returns `found: false`, search macOS Contacts:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/discover-contact.py --name "<contact name>" --include-messenger
```

This searches the user's macOS Contacts app for phone/email. If Messenger username is needed, you'll need to search the user's Facebook friends list using browser automation.

### Step 3: Auto-Add New Contacts

After successfully discovering a contact, automatically add them to contacts.yaml:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/add-contact.py \
  --name "<Full Name>" \
  --phone "<+61...>" \
  --email "<email>" \
  --messenger "<username>" \
  --context personal \
  --relationship "<description>"
```

### Complete Flow Example

```
User: "Message Sarah about dinner"

1. Lookup: lookup-contact.py --name "Sarah"
   → {"found": false}

2. Discover: discover-contact.py --name "Sarah" --include-messenger
   → {"found": true, "phone": "+61412345678", "email": "sarah@email.com"}

3. For Messenger username (if needed):
   → Use browser to search Facebook friends for "Sarah"
   → Extract username from profile URL

4. Auto-add: add-contact.py --name "Sarah Smith" --phone "+61412345678" --messenger "sarah.smith"
   → Contact saved to contacts.yaml

5. Send message using discovered details
```

### Adding JHG Work Colleagues

When adding a new JHG (John Holland Group) work colleague, **always look up their Teams email** using browser automation:

#### Teams Email Lookup Workflow

1. **Open Teams Web** using claude-in-chrome:
   ```
   tabs_context_mcp(createIfEmpty: true)
   tabs_create_mcp()
   navigate(url: "https://teams.microsoft.com", tabId)
   wait(duration: 5)  # Wait for Teams to load
   ```

2. **Search for the person**:
   ```
   click on search bar
   type "<person's name>"
   wait(duration: 2)
   ```

3. **Click on their profile** in search results (look for "-JHG" suffix)

4. **Extract email** from the profile card:
   - Look for "Email" field (format: `firstname.lastname@jhg.com.au` or `username@jhg.com.au`)
   - The "Chat" field shows the Teams identifier

5. **Add to contacts** with work context:
   ```yaml
   - name: <Full Name>
     nicknames:
       - <FirstName>
       - <LastName>
     context: work  # or personal_and_work if also a friend
     relationship: "Work colleague at JHG"
     work_keywords:
       - John Holland
       - JHG
       - Databricks
       - pipeline
     platforms:
       teams:
         email: <username>@jhg.com.au
     default_platform:
       work: teams
   ```

#### Example: Adding a New JHG Colleague

```
User: "Add Rebecca Bhatia from JHG to my contacts"

1. Search Teams for "Rebecca Bhatia"
2. Click on "Rebecca Bhatia-JHG" profile
3. Extract email: rbhatia@jhg.com.au
4. Edit contacts.yaml to add:
   - name: Rebecca Bhatia
     nicknames: [Rebecca, Bhatia]
     context: work
     relationship: "Work colleague at JHG"
     github: <if known>
     work_keywords: [John Holland, JHG, ...]
     platforms:
       teams:
         email: rbhatia@jhg.com.au
     default_platform:
       work: teams
```

**IMPORTANT:** Always verify the email from Teams rather than guessing the format, as JHG email formats can vary (e.g., `jdowzard@jhg.com.au` vs `javilamolina@jhg.com.au`).

### Platform Selection

Once contact is resolved:
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
