# WhatsApp Web Browser Automation

This document describes the reliable approach for sending WhatsApp messages using browser automation (claude-in-chrome MCP tools).

## Why Browser Automation?

The deep link approach (`wa.me/?text=...`) has limitations:
- Cannot auto-send messages (security feature)
- Requires manual "Continue to WhatsApp Web" click
- Only drafts messages, never sends

For **yolo/send mode**, browser automation is required.

## Reliable WhatsApp Web Workflow

### Step 1: Navigate Directly to Chat

Use the direct send URL format:

```
https://web.whatsapp.com/send?phone=<phone_number_without_plus>
```

Example:
```javascript
navigate(url: "https://web.whatsapp.com/send?phone=61418323408", tabId)
wait(duration: 3)  // Wait for WhatsApp Web to load
```

**Important:**
- Remove the `+` from phone numbers
- WhatsApp Web must already be authenticated in the browser

### Step 2: Insert Message Text

WhatsApp uses a contenteditable div, NOT a standard input. Regular typing doesn't work.

**Use JavaScript execCommand:**

```javascript
javascript_tool({
  action: "javascript_exec",
  text: `
    const inputs = document.querySelectorAll('[contenteditable="true"]');
    let messageBox = null;
    for (let input of inputs) {
      if (input.getAttribute('data-tab') === '10' ||
          input.getAttribute('aria-placeholder')?.includes('message')) {
        messageBox = input;
        break;
      }
    }
    if (!messageBox) {
      messageBox = document.querySelector('footer [contenteditable="true"]');
    }
    if (messageBox) {
      messageBox.focus();
      document.execCommand('selectAll', false, null);
      document.execCommand('delete', false, null);
      document.execCommand('insertText', false, 'YOUR MESSAGE HERE');
      "Message inserted";
    } else {
      "Message box not found";
    }
  `,
  tabId
})
```

### Step 3: Click Send Button

The send button appears after text is entered. Find it by `data-icon` containing "send":

```javascript
javascript_tool({
  action: "javascript_exec",
  text: `
    // Wait a moment for send button to appear
    // WhatsApp uses different icon names: "send" or "wds-ic-send-filled"
    const sendIcon = document.querySelector('[data-icon*="send"]');
    if (sendIcon) {
      // Click the parent button element
      const sendButton = sendIcon.closest('button') || sendIcon.parentElement;
      sendButton.click();
      "Message sent";
    } else {
      "Send button not found - message may be empty";
    }
  `,
  tabId
})
```

### Step 4: Verify Message Sent

Take a screenshot and verify the message appears in the chat with checkmarks.

## Common Issues & Solutions

### Issue: Chat doesn't open
**Cause:** Phone number format incorrect or contact doesn't exist
**Solution:** Ensure phone is in international format without `+` (e.g., `61418323408`)

### Issue: Message not inserted
**Cause:** contenteditable div not found or not focused
**Solution:** Use the exact JavaScript pattern above with `execCommand`

### Issue: Send button not clickable
**Cause:** Message is empty or button not rendered yet
**Solution:** Wait 1-2 seconds after inserting text before clicking send

### Issue: Attachment menu opens instead
**Cause:** Clicked on Attach button (left side) instead of Send (right side)
**Solution:** Use `[data-icon="send"]` selector, not coordinate clicks

### Issue: Link preview blocks send
**Cause:** URL in message triggers preview popup
**Solution:** Wait for preview to load, then click send. The preview is included automatically.

## Complete Example Flow

```javascript
// 1. Get browser context
tabs_context_mcp({ createIfEmpty: true })

// 2. Create new tab
tabs_create_mcp()

// 3. Navigate to chat
navigate({
  url: "https://web.whatsapp.com/send?phone=61418323408",
  tabId
})

// 4. Wait for page load
wait({ duration: 4, tabId })

// 5. Insert message
javascript_tool({
  action: "javascript_exec",
  text: `
    const messageBox = document.querySelector('footer [contenteditable="true"]');
    if (messageBox) {
      messageBox.focus();
      document.execCommand('insertText', false, 'Hello! This is my message.');
      "done";
    }
  `,
  tabId
})

// 6. Wait for send button
wait({ duration: 1, tabId })

// 7. Click send
javascript_tool({
  action: "javascript_exec",
  text: `
    const sendIcon = document.querySelector('[data-icon*="send"]');
    if (sendIcon) {
      sendIcon.closest('button')?.click() || sendIcon.parentElement.click();
      "sent";
    }
  `,
  tabId
})

// 8. Verify with screenshot
screenshot({ tabId })
```

## Draft vs Send Mode

| Mode | Approach | Auto-sends? |
|------|----------|-------------|
| Draft (default) | Deep link via `whatsapp.sh` | No - user reviews |
| Send (yolo) | Browser automation | Yes - sends immediately |

## Important Notes

1. **Authentication required**: WhatsApp Web must be logged in already
2. **Tab group**: Use existing WhatsApp tab if available to avoid re-auth
3. **Rate limiting**: Don't send too many messages rapidly
4. **Privacy**: Messages sent via automation are indistinguishable from manual

---

## Contact Phone Extraction

When adding a new contact, extract their phone number from WhatsApp if they're already in your WhatsApp contacts.

### Phone Extraction Workflow

#### Step 1: Navigate to WhatsApp and Search

```javascript
// Navigate to WhatsApp Web
navigate({ url: "https://web.whatsapp.com", tabId })
wait({ duration: 3, tabId })

// Click search bar
find({ query: "search bar", tabId })
computer({ action: "left_click", ref: searchRef, tabId })

// Type contact name
computer({ action: "type", text: "Sarah", tabId })
wait({ duration: 2, tabId })
```

#### Step 2: Click on Contact

```javascript
// Find and click matching contact in search results
find({ query: "Sarah in contact list", tabId })
computer({ action: "left_click", ref: contactRef, tabId })
wait({ duration: 1, tabId })
```

#### Step 3: Open Contact Profile

Click on the contact name in the chat header to open their profile:

```javascript
// Click contact name header to open profile panel
find({ query: "contact name header at top of chat", tabId })
computer({ action: "left_click", ref: headerRef, tabId })
wait({ duration: 1, tabId })
```

#### Step 4: Extract Phone Number

The phone number is displayed in the profile panel:

```javascript
javascript_tool({
  action: "javascript_exec",
  text: `
    // Phone number appears in profile panel
    // Look for the phone section or extract from profile text
    const profilePanel = document.querySelector('[data-testid="contact-info-drawer"]')
      || document.querySelector('span[dir="auto"]');

    // Search for phone number pattern in profile
    const text = document.body.innerText;
    const phoneMatch = text.match(/\\+?\\d{1,3}[\\s-]?\\d{3,4}[\\s-]?\\d{3,4}[\\s-]?\\d{3,4}/);

    if (phoneMatch) {
      // Normalize to +61 format
      let phone = phoneMatch[0].replace(/[\\s-]/g, '');
      if (phone.startsWith('04')) {
        phone = '+61' + phone.slice(1);
      } else if (!phone.startsWith('+')) {
        phone = '+' + phone;
      }
      phone;
    } else {
      "Phone not found";
    }
  `,
  tabId
})
```

### Complete Phone Extraction Example

```javascript
// 1. Get browser context
tabs_context_mcp({ createIfEmpty: true })

// 2. Use existing WhatsApp tab or create new
const existingTab = availableTabs.find(t => t.url.includes('whatsapp'));
const tabId = existingTab?.tabId || (await tabs_create_mcp()).tabId;

// 3. Navigate to WhatsApp
navigate({ url: "https://web.whatsapp.com", tabId })
wait({ duration: 3, tabId })

// 4. Screenshot to see current state
computer({ action: "screenshot", tabId })

// 5. Click search bar (top left area)
computer({ action: "left_click", coordinate: [260, 83], tabId })
wait({ duration: 0.5, tabId })

// 6. Type contact name
computer({ action: "type", text: "Sarah Thompson", tabId })
wait({ duration: 2, tabId })

// 7. Screenshot to see search results
computer({ action: "screenshot", tabId })

// 8. Click on matching contact in results
computer({ action: "left_click", coordinate: [contactCoords], tabId })
wait({ duration: 1, tabId })

// 9. Click contact header to open profile
computer({ action: "left_click", coordinate: [headerCoords], tabId })
wait({ duration: 1, tabId })

// 10. Extract phone from profile
javascript_tool({
  action: "javascript_exec",
  text: `
    const text = document.body.innerText;
    const phone = text.match(/\\+61\\d{9}/);
    phone ? phone[0] : null;
  `,
  tabId
})
```

### Troubleshooting Phone Extraction

#### Issue: Contact not found in search
**Solution**: The contact may not be in your WhatsApp contacts. Skip this platform.

#### Issue: Profile panel doesn't show phone
**Solution**: Some contacts hide their phone. Try scrolling the profile panel.

#### Issue: Multiple phone numbers shown
**Solution**: Extract the first mobile number (starts with +614 for Australian)
