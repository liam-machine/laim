# Teams Browser Automation

This document describes how to extract contact emails from Microsoft Teams using browser automation (claude-in-chrome MCP tools).

## Use Case

When adding a new work colleague to contacts, automatically look up their Teams email instead of guessing the format.

## Teams Email Extraction Workflow

### Step 1: Navigate to Teams

```javascript
tabs_context_mcp({ createIfEmpty: true })
tabs_create_mcp()
navigate({ url: "https://teams.microsoft.com", tabId })
wait({ duration: 5, tabId })  // Teams takes a while to load
```

### Step 2: Search for Contact

```javascript
// Click search bar (usually at top)
find({ query: "search bar", tabId })
computer({ action: "left_click", ref: searchRef, tabId })

// Type the person's name
computer({ action: "type", text: "Rebecca Bhatia", tabId })
wait({ duration: 2, tabId })  // Wait for search results
```

### Step 3: Click on Profile

Look for the person in search results. JHG colleagues typically have "-JHG" suffix:

```javascript
// Find and click the matching profile
find({ query: "Rebecca Bhatia-JHG in search results", tabId })
computer({ action: "left_click", ref: profileRef, tabId })
wait({ duration: 2, tabId })
```

### Step 4: Extract Email

The profile card displays the email. Extract it:

```javascript
javascript_tool({
  action: "javascript_exec",
  text: `
    // Teams profile card shows email in various locations
    // Look for email pattern in the profile panel
    const profileText = document.body.innerText;
    const emailMatch = profileText.match(/[a-zA-Z0-9._%+-]+@jhg\\.com\\.au/);
    emailMatch ? emailMatch[0] : "Email not found";
  `,
  tabId
})
```

Alternatively, use `get_page_text` and search for the email pattern:

```javascript
get_page_text({ tabId })
// Then regex match for @jhg.com.au pattern
```

## Complete Example

```javascript
// 1. Get browser context
tabs_context_mcp({ createIfEmpty: true })

// 2. Create new tab or use existing Teams tab
tabs_create_mcp()

// 3. Navigate to Teams
navigate({ url: "https://teams.microsoft.com", tabId })
wait({ duration: 5, tabId })

// 4. Take screenshot to see current state
computer({ action: "screenshot", tabId })

// 5. Click search and type name
computer({ action: "left_click", coordinate: [searchBarCoords], tabId })
computer({ action: "type", text: "Rebecca Bhatia", tabId })
wait({ duration: 2, tabId })

// 6. Click on matching profile in results
computer({ action: "left_click", coordinate: [profileCoords], tabId })
wait({ duration: 2, tabId })

// 7. Extract email from profile
javascript_tool({
  action: "javascript_exec",
  text: `
    const text = document.body.innerText;
    const email = text.match(/[a-zA-Z0-9._%+-]+@jhg\\.com\\.au/);
    email ? email[0] : null;
  `,
  tabId
})
```

## Important Notes

1. **Authentication**: Teams Web must already be logged in
2. **Email format varies**: Don't guess - always extract from Teams
   - Could be `firstname.lastname@jhg.com.au`
   - Could be `username@jhg.com.au`
   - Could be `flastname@jhg.com.au`
3. **JHG suffix**: Look for "-JHG" in profile names to identify correct match
4. **Wait times**: Teams is slow - use longer waits than WhatsApp

## Troubleshooting

### Issue: Search results don't appear
**Solution**: Wait longer (5+ seconds) or take screenshot to verify page loaded

### Issue: Multiple profiles with same name
**Solution**: Look for "-JHG" suffix or check department/title in results

### Issue: Profile card doesn't show email
**Solution**: Click "View profile" or "See more" to expand full details
