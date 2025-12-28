---
name: messaging
description: Add contacts and send messages across multiple platforms (Teams, WhatsApp, iMessage, Facebook Messenger). Use this skill when the user wants to "add contact", "add X as a contact", "new contact", "save contact" (ALWAYS auto-discover details first), OR "message someone", "text someone", "send a message", "chat with", "read messages from", "get message history", "what did X say", "recent messages with", "check messages", mentions messaging a known contact by name (like James, JD), or specifies a platform like Teams, WhatsApp, iMessage, or Messenger. CRITICAL FOR ADDING CONTACTS: Auto-discover phone numbers and usernames from macOS Contacts, WhatsApp, Teams, and Messenger using browser automation - NEVER ask the user for details that can be discovered automatically. NEVER edit contacts.yaml without auto-discovering first.
---

# Messaging Skill

Send and read messages across multiple platforms from Claude Code. By default, messages are **drafted** for you to review and send manually. You can also read message history for context.

---

## ⚠️ STOP - What Are You Doing?

```
User request
├── ADDING A CONTACT? ("add X", "new contact", "save contact")
│   └── GO TO: "Adding New Contacts" section below
│       ├── 1. Ask: relationship, platforms (AskUserQuestion)
│       ├── 2. Auto-discover from EACH platform (scripts + browser)
│       ├── 3. Show results to user
│       └── 4. THEN add to contacts.yaml
│
├── SENDING A MESSAGE? ("message X", "text X", "WhatsApp X")
│   └── GO TO: "Sending Messages" section below
│
└── READING MESSAGES? ("what did X say", "check messages")
    └── GO TO: "Reading Message History" section below
```

**CRITICAL:** When adding contacts, NEVER edit contacts.yaml directly without auto-discovering first. Always run discovery scripts and browser automation to find phone numbers, emails, and usernames automatically.

---

## Adding New Contacts

When user asks to "add X as a contact" or "new contact":

**🚨 AUTO-DISCOVER FIRST, ASK LATER.** Never ask the user for phone numbers, emails, or usernames that can be discovered automatically.

### Workflow Summary

| Step | Action | Details |
|------|--------|---------|
| 1 | **Ask only what can't be discovered** | Use AskUserQuestion for: relationship, platforms to add |
| 2 | **Auto-discover from each platform** | Run in parallel - see table below |
| 3 | **Show results** | "Found X: WhatsApp +61..., Messenger username..." |
| 4 | **Add to contacts.yaml** | Only after discovery completes |

### Auto-Discovery Methods (Step 2)

| Platform | Method | What to Extract |
|----------|--------|-----------------|
| iMessage | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/discover-contact.py --name "X"` | Phone from macOS Contacts |
| WhatsApp | Browser: search → click profile | Phone number |
| Teams | Browser: search → click profile | Work email |
| Messenger | Browser: search → click profile panel | Username (format: name.surname.12345) |

### Auto-Discovery Rules

1. **Search immediately** - Don't ask "Should I search?" - just do it
2. **Parallel when possible** - Run script + open browser tabs simultaneously
3. **Skip if not found** - If contact not found on a platform, skip silently
4. **Show results** - Display what was found before adding to contacts

### Example Flow

```
User: "Add Sarah to my contacts"

1. AskUserQuestion:
   - "What is your relationship with Sarah?" → "Personal friend"
   - "Which platforms?" → [WhatsApp, iMessage, Messenger]

2. Auto-discover (parallel):
   - discover-contact.py --name "Sarah" → phone: +61412345678
   - Browser → Messenger search → username: sarah.smith.12345

3. Show results:
   "Found Sarah:
    - Phone: +61412345678 (WhatsApp, iMessage)
    - Messenger: sarah.smith.12345"

4. Add to contacts.yaml
```

See "Contact Resolution" section below for detailed browser automation steps.

---

## Sending Messages (Quick Start)

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

### Platform Selection Logic

When sending a message, Claude determines the platform using this priority:

1. **Explicit platform** - If you say "WhatsApp James", use WhatsApp
2. **Content inference** - If the message mentions work keywords (John Holland, JHG, Databricks, pipeline, sprint), use the work platform (Teams)
3. **Ask user** - If unclear, prompt: "Should I message James on Teams (work) or WhatsApp (personal)?"

### How It Works

1. **Resolve Contact** - Look up recipient in @references/contacts.yaml
2. **Select Platform** - Use explicit platform, infer from content, or ask user
3. **Draft Message** - Open the platform and draft the message
4. **You Review & Send** - Message is ready for you to review and send

---

## Contact Resolution (Detailed Steps)

This section contains detailed steps for contact lookup and auto-discovery. Referenced by both "Adding New Contacts" and "Sending Messages" workflows.

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

### Step 3: Gather Contact Details via AskUserQuestion

Before adding a new contact, **always ask the user** to confirm or provide missing details:

#### Required Information

Use `AskUserQuestion` to gather:

1. **Full Name** (if only first name given):
   ```json
   {
     "question": "What is their full name (first and last)?",
     "header": "Full name",
     "options": [
       {"label": "<First> <guessed last>", "description": "If you can infer from context"},
       {"label": "Just <First>", "description": "No last name needed"}
     ]
   }
   ```

2. **Relationship**:
   ```json
   {
     "question": "What is your relationship with <Name>?",
     "header": "Relationship",
     "options": [
       {"label": "Personal friend", "description": "Someone you know personally"},
       {"label": "Work colleague (JHG)", "description": "John Holland Group colleague"},
       {"label": "3CC collaborator", "description": "ThreeCommasClub startup collaborator"},
       {"label": "WoodsWynne collaborator", "description": "WoodsWynne startup collaborator"},
       {"label": "Family member", "description": "Family relationship"}
     ]
   }
   ```

3. **Platforms to add**:
   ```json
   {
     "question": "Which platforms should I add <Name> to?",
     "header": "Platforms",
     "multiSelect": true,
     "options": [
       {"label": "Teams", "description": "Microsoft Teams (work)"},
       {"label": "WhatsApp", "description": "WhatsApp messaging"},
       {"label": "iMessage", "description": "Apple iMessage"},
       {"label": "Messenger", "description": "Facebook Messenger"}
     ]
   }
   ```

#### Example AskUserQuestion Flow

```
User: "Add Sarah to my contacts"

Claude uses AskUserQuestion:
Q1: "What is Sarah's full name?" → "Sarah Thompson"
Q2: "What is your relationship with Sarah?" → "Personal friend"
Q3: "Which platforms should I add Sarah to?" → ["WhatsApp", "iMessage"]

Then Claude auto-discovers from selected platforms (see Step 3b)
```

### Step 3b: Auto-Discover from Selected Platforms

After the user selects platforms, **automatically search each platform** to discover contact details. Do not ask for confirmation - just search.

| Platform Selected | Auto-Discovery Method | Data Extracted |
|-------------------|----------------------|----------------|
| Teams | Browser: Search Teams → Click profile | Work email |
| WhatsApp | Browser: Search contacts → Open profile | Phone number |
| iMessage | Script: `discover-contact.py` (macOS Contacts) | Phone number |
| Messenger | Browser: Search Messenger → Click profile | Username (from profile panel) |

#### Auto-Discovery Workflow

**For Teams** (work email):
```
1. Navigate to https://teams.microsoft.com
2. Click search bar, type contact name
3. Click matching profile (look for -JHG suffix)
4. Extract email from profile card
```
See @references/teams-browser.md for detailed steps.

**For WhatsApp** (phone number):
```
1. Navigate to https://web.whatsapp.com
2. Click search bar, type contact name
3. Click matching contact in results
4. Click contact name header to open profile
5. Extract phone number from profile panel
```
See @references/whatsapp-browser.md for detailed steps.

**For iMessage** (phone number):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/discover-contact.py --name "<name>"
```
Uses macOS Contacts app to find phone/email.

**For Messenger** (username):
```
1. Navigate to https://www.messenger.com
2. Click search bar, type contact name
3. Click matching contact in results
4. Username appears in profile panel on right (format: name.surname.12345)
```

#### Auto-Discovery Rules

1. **Search immediately** - Don't ask "Should I search?" - just do it
2. **Skip if not found** - If contact not found on a platform, skip it silently
3. **Show results** - After discovery, show what was found before adding to contacts
4. **Parallel when possible** - Search multiple platforms simultaneously

#### Example Auto-Discovery Flow

```
User selected: [Teams, WhatsApp]

1. Search Teams for "Sarah Thompson"
   → Found: sthompson@jhg.com.au

2. Search WhatsApp for "Sarah Thompson"
   → Found: +61412345678

3. Show results:
   "Found Sarah Thompson:
    - Teams: sthompson@jhg.com.au
    - WhatsApp: +61412345678
    Adding to contacts..."

4. Add to contacts.yaml
```

### Step 4: Add Contact to contacts.yaml

After gathering details, add them to contacts.yaml:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/add-contact.py \
  --name "<Full Name>" \
  --phone "<+61...>" \
  --email "<email>" \
  --messenger "<username>" \
  --context personal \
  --relationship "<description>"
```

Or directly edit `${CLAUDE_PLUGIN_ROOT}/skills/messaging/references/contacts.yaml`.

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

| Platform | Draft Mode | Send Mode (Yolo) | Identifier |
|----------|------------|------------------|------------|
| Teams | AppleScript + deep link | AppleScript | Email address |
| WhatsApp | Deep link (wa.me) | **Browser automation** | Phone number (+61...) |
| iMessage | AppleScript | AppleScript | Phone or email |
| Messenger | Deep link (m.me) | Browser automation | Facebook username |

### WhatsApp Send Mode (Browser Automation)

**IMPORTANT:** WhatsApp deep links cannot auto-send messages (security feature). For yolo/send mode, use browser automation via claude-in-chrome MCP tools.

#### Quick Reference

```javascript
// 1. Navigate directly to chat
navigate({ url: "https://web.whatsapp.com/send?phone=61418323408", tabId })
wait({ duration: 3, tabId })

// 2. Insert message using execCommand (regular typing doesn't work)
javascript_tool({
  action: "javascript_exec",
  text: `
    const msgBox = document.querySelector('footer [contenteditable="true"]');
    msgBox?.focus();
    document.execCommand('insertText', false, 'Your message here');
  `,
  tabId
})

// 3. Wait for send button to appear
wait({ duration: 1, tabId })

// 4. Click send button
javascript_tool({
  action: "javascript_exec",
  text: `
    const send = document.querySelector('[data-icon*="send"]');
    send?.closest('button')?.click() || send?.parentElement?.click();
  `,
  tabId
})
```

#### Key Insights

1. **Phone format**: Remove `+` from number (e.g., `61418323408` not `+61418323408`)
2. **Text input**: Use `document.execCommand('insertText', ...)` - regular typing fails on contenteditable
3. **Send button**: Find by `[data-icon*="send"]` selector (contains "send"), NOT coordinate clicks
4. **Link previews**: Wait for them to load before sending - they're included automatically

See @references/whatsapp-browser.md for detailed troubleshooting.

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
