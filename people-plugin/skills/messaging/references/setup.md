# Messaging Skill Setup Guide

## Prerequisites

### 1. Platform Applications

Install the apps you want to use:

| Platform | Installation |
|----------|-------------|
| Teams | `brew install --cask microsoft-teams` or App Store |
| WhatsApp | `brew install --cask whatsapp` or use WhatsApp Web |
| iMessage | Built-in (Messages.app) |
| Messenger | `brew install --cask messenger` or use browser |

### 2. Accessibility Permissions

AppleScript automation requires Accessibility permissions for Teams and iMessage.

1. Open **System Settings > Privacy & Security > Accessibility**
2. Click the lock icon to make changes
3. Add your terminal app (Terminal, iTerm2, Warp, etc.)
4. Ensure the toggle is **ON**

### 3. Full Disk Access (for reading iMessage history)

To read iMessage history, your terminal needs Full Disk Access to query `~/Library/Messages/chat.db`.

1. Open **System Settings > Privacy & Security > Full Disk Access**
2. Click the **+** button
3. Navigate to your terminal app:
   - Terminal: `/Applications/Utilities/Terminal.app`
   - iTerm: `/Applications/iTerm.app`
   - Warp: `/Applications/Warp.app`
4. Enable the toggle
5. **Restart your terminal** for changes to take effect

**Test it works:**
```bash
sqlite3 ~/Library/Messages/chat.db "SELECT COUNT(*) FROM message"
```

If you see a number (message count), FDA is working. If you get "operation not permitted", the permission isn't active yet.

### 4. Sign Into Platforms

Ensure you're signed into each platform before using the skill.

---

## Platform-Specific Setup

### Microsoft Teams

- **Requirement:** Desktop app (not browser)
- **Account:** Must be signed into your work account
- **Test:** Run this in terminal to verify deep links work:
  ```bash
  open "msteams://teams.microsoft.com/l/chat/0/0?users=test@company.com"
  ```
- **Troubleshooting:** If Teams doesn't open, reinstall from `brew install --cask microsoft-teams`

### WhatsApp

- **Method:** Uses wa.me deep links (opens in browser or desktop app)
- **Phone format:** International format with country code (e.g., +61412345678)
- **Limitation:** Cannot auto-send - must click Send manually
- **Test:**
  ```bash
  open "https://wa.me/61412345678?text=Test%20message"
  ```

### iMessage

- **App:** Built-in Messages.app
- **Identifier:** Phone number OR Apple ID email
- **Setup:** Ensure iMessage is enabled in Messages > Settings > iMessage
- **Permissions:** Terminal needs Accessibility permission to type in Messages
- **Test:**
  ```bash
  osascript -e 'tell application "Messages" to activate'
  ```

### Facebook Messenger

- **Method:** Uses m.me deep links
- **Identifier:** Facebook username (not display name)
- **Finding username:** Go to your friend's profile, the URL shows their username
- **Limitation:** Message is copied to clipboard - paste with Cmd+V
- **Test:**
  ```bash
  open "https://m.me/zuck"
  ```

---

## Adding Contacts

Edit the contacts file at:
```
${CLAUDE_PLUGIN_ROOT}/skills/messaging/references/contacts.yaml
```

Example entry:

```yaml
- name: Jane Smith
  nicknames:
    - Jane
    - JS
  context: work
  relationship: "Project manager at Company"
  work_keywords:
    - project
    - deadline
    - meeting
  platforms:
    teams:
      email: jsmith@company.com
    whatsapp:
      phone: "+61400000000"
  default_platform:
    work: teams
    personal: whatsapp
```

---

## Troubleshooting

### "osascript is not allowed to send keystrokes"

**Solution:** Re-grant Accessibility permissions to your terminal app:
1. System Settings > Privacy & Security > Accessibility
2. Remove your terminal app
3. Add it back and enable the toggle

### Message doesn't appear in Teams

**Solution:** Increase the delay in `teams.scpt`:
- Open the script and change `delay 3` to `delay 5`

### WhatsApp opens but shows wrong number

**Solution:** Ensure phone number includes country code with + prefix:
- Correct: `+61412345678`
- Incorrect: `0412345678`

### iMessage opens but recipient not found

**Solution:**
- Verify the phone/email is registered with iMessage
- Try using their Apple ID email instead of phone number

### Messenger doesn't show the right person

**Solution:** Use the Facebook username, not display name:
- Go to their profile
- Username is in the URL: facebook.com/**username**

---

## Testing the Skill

Test the main router script:

```bash
# Test Teams
bash ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/message.sh \
  --platform teams \
  --recipient "jdowzard@jhg.com.au" \
  --message "Test message from Claude"

# Test WhatsApp (replace with real number)
bash ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/message.sh \
  --platform whatsapp \
  --recipient "+61412345678" \
  --message "Test message"

# Test iMessage
bash ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/message.sh \
  --platform imessage \
  --recipient "+61412345678" \
  --message "Test message"

# Test Messenger
bash ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/message.sh \
  --platform messenger \
  --recipient "username" \
  --message "Test message"
```

---

## Testing Message Reading

Test the iMessage reader (requires Full Disk Access):

```bash
# Test with phone number
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/platforms/imessage-read.py \
  --contact "+61418323408" \
  --recent 5

# Test with contact name (resolves from contacts.yaml)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/platforms/imessage-read.py \
  --contact "James" \
  --recent 5

# Test keyword search
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/platforms/imessage-read.py \
  --contact "James" \
  --keyword "movie"

# Test JSON output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/platforms/imessage-read.py \
  --contact "James" \
  --recent 3 \
  --json
```

If you get "Cannot access iMessage database", grant Full Disk Access (see section 3 above).
