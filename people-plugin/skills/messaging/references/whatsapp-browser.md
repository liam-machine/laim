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

The send button appears after text is entered. Find it by `data-icon="send"`:

```javascript
javascript_tool({
  action: "javascript_exec",
  text: `
    // Wait a moment for send button to appear
    const sendIcon = document.querySelector('[data-icon="send"]');
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
    const sendIcon = document.querySelector('[data-icon="send"]');
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
