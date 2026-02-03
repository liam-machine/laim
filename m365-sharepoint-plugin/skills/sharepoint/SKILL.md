---
name: sharepoint
description: Edit and manage SharePoint modern pages. Use this skill when the user wants to "edit SharePoint page", "update SharePoint content", "modify SharePoint text", "change page content", "add section to SharePoint", "list SharePoint pages", "get page sections", "SharePoint page editing", "PnP PowerShell", or any request involving reading or modifying SharePoint site pages. Provides both REST API operations for reading and PnP PowerShell command generation for editing.
---

# SharePoint Page Editing

This skill helps you read and edit SharePoint modern pages. Since SharePoint page editing requires PnP PowerShell for most operations, this skill:

1. **Reads pages** via SharePoint REST API (Python)
2. **Generates PnP PowerShell commands** for editing operations
3. **Identifies editable content** (text web parts, sections)

## Quick Reference

| Operation | Method |
|-----------|--------|
| List pages | REST API (Python) |
| Read page content | REST API (Python) |
| Get sections/web parts | REST API (Python) |
| Edit text content | PnP PowerShell (generated) |
| Add sections | PnP PowerShell (generated) |
| Add web parts | PnP PowerShell (generated) |

## Authentication

Uses MSAL device code flow with the **PnP Management Shell** client ID, which has `Sites.FullControl.All` pre-consented. First run will prompt for browser authentication.

Tokens are cached at: `~/.credentials/sp_<tenant>_token.json`

## Reading Pages

### List all pages in a site

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py list "https://johnholland.sharepoint.com/sites/MySite"
```

### Get page content

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py get "https://johnholland.sharepoint.com/sites/MySite" "Home.aspx"
```

### Get page sections and web parts

This is the most useful command for understanding page structure before editing:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py sections "https://johnholland.sharepoint.com/sites/MySite" "Home.aspx"
```

Output shows:
- Section index and layout
- Web parts with **instance IDs** (needed for editing)
- Text content (HTML and plain text)
- Web part types

## Editing Pages (PnP PowerShell)

SharePoint modern page editing requires PnP PowerShell. The scripts generate ready-to-run commands.

### Prerequisites

Install PnP PowerShell (one-time):

```powershell
Install-Module PnP.PowerShell -Scope CurrentUser
```

### Generate PnP connect command

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py pnp-connect "https://johnholland.sharepoint.com/sites/MySite"
```

### Edit text web part

First, get the instance ID from the sections command, then:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py edit-text \
  "https://johnholland.sharepoint.com/sites/MySite" \
  "Home.aspx" \
  "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  "<p>New content here</p>"
```

This outputs a PnP PowerShell script you can run.

### Add a section

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py add-section \
  "https://johnholland.sharepoint.com/sites/MySite" \
  "Home.aspx" \
  --layout TwoColumn \
  --order 2
```

Layouts: `OneColumn`, `TwoColumn`, `TwoColumnLeft`, `TwoColumnRight`, `ThreeColumn`

### Add text web part

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py add-text \
  "https://johnholland.sharepoint.com/sites/MySite" \
  "Home.aspx" \
  "<h2>New Section</h2><p>Content goes here.</p>" \
  --section 1 \
  --column 1
```

## Workflow for Editing a Page

1. **List pages** to find the one you want to edit
2. **Get sections** to see the page structure and find instance IDs
3. **Generate PnP commands** for the changes you want
4. **Run the PowerShell commands** in a terminal with PnP.PowerShell installed

Example workflow:

```bash
# 1. Find the page
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py list "https://johnholland.sharepoint.com/sites/JHG-VermillionTirana"

# 2. Get page structure
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py sections "https://johnholland.sharepoint.com/sites/JHG-VermillionTirana" "Home.aspx"

# 3. Generate edit command
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py edit-text \
  "https://johnholland.sharepoint.com/sites/JHG-VermillionTirana" \
  "Home.aspx" \
  "abc12345-..." \
  "<p>Updated content</p>"

# 4. Run the generated PowerShell commands
```

## Common JHG Sites

| Site | URL |
|------|-----|
| VT (Vermillion Tirana) | `https://johnholland.sharepoint.com/sites/JHG-VermillionTirana` |
| TEK Geotechnical | `https://johnholland.sharepoint.com/sites/JHG-TEKGeotechnical` |
| Sydney Metro West | `https://johnholland.sharepoint.com/sites/P16212SydneyMetroWestLinewide` |
| More Trains More Services | `https://johnholland.sharepoint.com/sites/MoreTrainsMoreServices` |

## Limitations

1. **Page editing requires PnP PowerShell** - REST API is read-only for modern pages
2. **Some web parts can't be edited** - Only text web parts support direct content editing
3. **Complex layouts need manual work** - Hero web parts, news, etc. have complex schemas
4. **JHG tenant restrictions may apply** - Some sites may require additional permissions

See @references/pnp-commands.md for a complete PnP PowerShell reference.
See @references/troubleshooting.md for common issues and solutions.
