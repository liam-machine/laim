# Browser-Based Message Reading

For web platforms (Teams, WhatsApp Web, Messenger), use claude-in-chrome MCP tools to read message history.

## Prerequisites

1. User must be **logged into** the web platform
2. Browser tab group must be initialized via `tabs_context_mcp`

---

## Microsoft Teams

### URL
```
https://teams.microsoft.com
```

### Workflow

1. **Initialize browser context**
   ```
   mcp__claude-in-chrome__tabs_context_mcp(createIfEmpty: true)
   ```

2. **Create a new tab and navigate to Teams**
   ```
   mcp__claude-in-chrome__tabs_create_mcp()
   mcp__claude-in-chrome__navigate(url: "https://teams.microsoft.com", tabId: <id>)
   ```

3. **Wait for Teams to load**
   ```
   mcp__claude-in-chrome__computer(action: "wait", duration: 5, tabId: <id>)
   ```

4. **Find the conversation**
   ```
   mcp__claude-in-chrome__find(query: "chat with James", tabId: <id>)
   ```
   Or use `read_page` to see the chat list and find by name.

5. **Click to open the conversation**
   ```
   mcp__claude-in-chrome__computer(action: "left_click", ref: "<ref_id>", tabId: <id>)
   ```

6. **Scroll up to load more history**
   ```
   mcp__claude-in-chrome__computer(action: "scroll", scroll_direction: "up", scroll_amount: 5, tabId: <id>)
   ```
   Repeat as needed to load more messages.

7. **Extract messages**
   ```
   mcp__claude-in-chrome__get_page_text(tabId: <id>)
   ```
   Or use `read_page` for structured element data.

### Tips
- Teams loads messages dynamically - scroll up multiple times for older history
- Search feature can help find specific conversations: look for search input
- If user has many chats, use the search bar to filter

---

## WhatsApp Web

### URL
```
https://web.whatsapp.com
```

### Workflow

1. **Initialize and navigate**
   ```
   mcp__claude-in-chrome__tabs_context_mcp(createIfEmpty: true)
   mcp__claude-in-chrome__tabs_create_mcp()
   mcp__claude-in-chrome__navigate(url: "https://web.whatsapp.com", tabId: <id>)
   ```

2. **Wait for QR code scan / session restore**
   ```
   mcp__claude-in-chrome__computer(action: "wait", duration: 5, tabId: <id>)
   ```
   User may need to scan QR code if not already logged in.

3. **Find contact in chat list**
   ```
   mcp__claude-in-chrome__find(query: "James", tabId: <id>)
   ```
   Or use the search bar at top of chat list.

4. **Click to open conversation**
   ```
   mcp__claude-in-chrome__computer(action: "left_click", ref: "<ref_id>", tabId: <id>)
   ```

5. **Scroll up for history**
   ```
   mcp__claude-in-chrome__computer(action: "scroll", scroll_direction: "up", scroll_amount: 5, tabId: <id>)
   ```

6. **Extract messages**
   ```
   mcp__claude-in-chrome__get_page_text(tabId: <id>)
   ```

### Tips
- WhatsApp Web requires phone to be connected
- Messages include timestamps - useful for context
- Media messages show as placeholders in text extraction

---

## Facebook Messenger

### URL
```
https://messenger.com
```

### Workflow

1. **Initialize and navigate**
   ```
   mcp__claude-in-chrome__tabs_context_mcp(createIfEmpty: true)
   mcp__claude-in-chrome__tabs_create_mcp()
   mcp__claude-in-chrome__navigate(url: "https://messenger.com", tabId: <id>)
   ```

2. **Wait for login / session restore**
   ```
   mcp__claude-in-chrome__computer(action: "wait", duration: 5, tabId: <id>)
   ```

3. **Find conversation**
   ```
   mcp__claude-in-chrome__find(query: "James Dowzard", tabId: <id>)
   ```
   Use full name for more accurate matching.

4. **Click to open conversation**
   ```
   mcp__claude-in-chrome__computer(action: "left_click", ref: "<ref_id>", tabId: <id>)
   ```

5. **Scroll up for history**
   ```
   mcp__claude-in-chrome__computer(action: "scroll", scroll_direction: "up", scroll_amount: 5, tabId: <id>)
   ```

6. **Extract messages**
   ```
   mcp__claude-in-chrome__get_page_text(tabId: <id>)
   ```

### Tips
- Messenger uses display names, not usernames for conversation list
- Group chats appear with group name
- Search bar can filter conversations

---

## Keyword Search in Browser

For keyword-based searches, use the platform's built-in search:

### Teams
1. Click in the search bar at top
2. Type the keyword
3. Look for "Messages" section in results
4. Filter by person if needed

### WhatsApp Web
1. Open the conversation first
2. Click the 3-dot menu → Search
3. Type keyword to highlight matches

### Messenger
1. Click in search bar
2. Type keyword
3. Results show matching conversations

---

## Troubleshooting

### "Page not loaded" or timeout
- Increase wait duration
- Check if user is logged in
- Try refreshing the page

### Can't find conversation
- Try exact name match
- Use search functionality
- Scroll down in chat list if many conversations

### Messages not extracting properly
- Use `read_page` instead of `get_page_text` for structured data
- Some messages may be images/media - will show as placeholders
- Very long conversations may need multiple scroll + extract cycles

### Rate limiting
- Add delays between actions
- Don't scroll too aggressively
- Platforms may block rapid automated access
