---
name: atlassian-api
description: "Interact with Jira and Confluence via the Atlassian REST API using a lightweight Python CLI. Use this skill whenever the user asks about Jira issues, Confluence pages, Atlassian search, or any Jira/Confluence CRUD operations — especially when the MCP plugin is unavailable or when you need REST API features not exposed by MCP (attachments, sprints, boards, bulk operations, dashboards, filters). Also use this when the user mentions JQL queries, CQL queries, creating tickets, updating issues, reading wiki pages, or managing Atlassian content. Triggers on: Jira, Confluence, Atlassian, JQL, CQL, ticket, issue, wiki page, sprint, board, epic, story, backlog."
---

# Atlassian REST API Skill

A thin Python CLI at `~/.claude/skills/atlassian-api/scripts/atlassian.py` wraps the Atlassian Cloud REST API with automatic authentication, JSON formatting, and pagination support.

## Quick Start

```bash
# Test connection
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/myself
```

The script reads credentials from `~/.atlassian-credentials` (email, token, site) and handles Basic auth automatically.

## CLI Syntax

```
python ~/.claude/skills/atlassian-api/scripts/atlassian.py METHOD PATH [--data JSON] [--params KEY=VAL ...] [--paginate] [--max-pages N]
```

| Flag | Purpose |
|------|---------|
| `--data` / `-d` | JSON request body (for POST/PUT) |
| `--params` / `-p` | Query parameters as `KEY=VAL` pairs |
| `--paginate` | Auto-follow pagination (max 5 pages by default) |
| `--max-pages N` | Override max pages when paginating |
| `--raw` | Print full response without truncation |
| `--timeout N` | Request timeout in seconds (default: 30) |

## Jira REST API v3 — Endpoint Reference

Base path: `/rest/api/3/`

### Search Issues (JQL)

The search endpoint was migrated to `/rest/api/3/search/jql` (the old `/rest/api/3/search` returns 410).

```bash
# POST method (preferred for complex JQL)
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /rest/api/3/search/jql \
  --data '{"jql":"project = EDP ORDER BY created DESC","maxResults":10,"fields":["summary","status","assignee","priority","created"]}'

# GET method (simple queries)
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/search/jql \
  --params jql="project=EDP" maxResults=10 fields=summary,status
```

Key body/params for POST: `jql` (required), `fields` (array), `maxResults` (default 50, max 100), `startAt` (offset), `expand` (renderedFields, names, changelog).

### Get Issue

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/issue/EDP-123
# With specific fields and expansions:
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/issue/EDP-123 \
  --params fields=summary,status,description expand=renderedFields,changelog
```

### Create Issue

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /rest/api/3/issue \
  --data '{
    "fields": {
      "project": {"key": "EDP"},
      "issuetype": {"name": "Task"},
      "summary": "New task title",
      "description": {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Description here"}]}]
      }
    }
  }'
```

Required fields: `project` (key or id), `issuetype` (name or id), `summary`. Description uses ADF (Atlassian Document Format).

### Edit Issue

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py PUT /rest/api/3/issue/EDP-123 \
  --data '{"fields":{"summary":"Updated title","priority":{"name":"High"}}}'
```

### Get Transitions

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/issue/EDP-123/transitions
```

### Transition Issue (change status)

```bash
# First get available transitions, then use the transition ID:
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /rest/api/3/issue/EDP-123/transitions \
  --data '{"transition":{"id":"31"}}'
```

### Add Comment

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /rest/api/3/issue/EDP-123/comment \
  --data '{
    "body": {
      "type": "doc",
      "version": 1,
      "content": [{"type": "paragraph", "content": [{"type": "text", "text": "My comment"}]}]
    }
  }'
```

### List Projects

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/project/search \
  --params maxResults=50
```

### User Search

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/user/search \
  --params query=liam
```

### Issue Link Types

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/issueLinkType
```

### Create Issue Link

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /rest/api/3/issueLink \
  --data '{"type":{"name":"Blocks"},"inwardIssue":{"key":"EDP-10"},"outwardIssue":{"key":"EDP-20"}}'
```

### Add Worklog

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /rest/api/3/issue/EDP-123/worklog \
  --data '{"timeSpent":"2h","comment":{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Worked on implementation"}]}]}}'
```

### Get Issue Types for Project

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/issue/createmeta/EDP/issuetypes
```

### Get Field Metadata for Issue Type

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/issue/createmeta/EDP/issuetypes/10001
```

### Get Current User

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/myself
```

### Remote Issue Links

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/api/3/issue/EDP-123/remotelink
```

## Jira Agile API (bonus — not in MCP)

Base path: `/rest/agile/1.0/`

```bash
# List boards
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/agile/1.0/board --params maxResults=50

# Get sprints for a board
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/agile/1.0/board/42/sprint

# Get issues in a sprint
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/agile/1.0/sprint/100/issue

# Get backlog issues
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /rest/agile/1.0/board/42/backlog
```

## Jira Attachments (bonus — not in MCP)

Upload requires multipart form, so use curl directly:

```bash
CREDS=$(python3 -c "
creds={}
for line in open('$HOME/.atlassian-credentials'):
    if '=' in line:
        k,v = line.strip().split('=',1)
        creds[k.strip()] = v.strip()
print(f\"{creds['email']}:{creds['token']}\")
")
curl -u "$CREDS" -X POST \
  "https://johnholland.atlassian.net/rest/api/3/issue/EDP-123/attachments" \
  -H "X-Atlassian-Token: no-check" \
  -F "file=@/path/to/file.pdf"
```

## Confluence REST API v2 — Endpoint Reference

Base path: `/wiki/api/v2/`

### Search with CQL (uses v1 endpoint)

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/rest/api/search \
  --params cql='type=page AND space=EDP AND text~"pipeline"' limit=25
```

CQL examples:
- `type=page AND space=EDP` — pages in EDP space
- `text ~ "deploy"` — full-text search
- `title = "Meeting Notes"` — exact title
- `label = "architecture"` — by label
- `creator = currentUser()` — your pages
- `lastModified > "2026-01-01"` — recently modified

### Get Page by ID

```bash
# Storage format (raw HTML-like markup)
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/pages/123456789 \
  --params body-format=storage

# Atlas doc format (ADF JSON)
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/pages/123456789 \
  --params body-format=atlas_doc_format
```

### List Spaces

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/spaces --params limit=50
```

### Get Pages in Space

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/spaces/123/pages \
  --params limit=25 sort=-modified-date
```

### Get Child Pages

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/pages/123456789/children
```

### Get Descendants (deeper)

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/pages/123456789/descendants \
  --params limit=50
```

### Create Page

```bash
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /wiki/api/v2/pages \
  --data '{
    "spaceId": "123",
    "status": "current",
    "title": "New Page Title",
    "parentId": "456",
    "body": {
      "representation": "storage",
      "value": "<p>Page content in storage format</p>"
    }
  }'
```

### Update Page

```bash
# First GET the page to get the current version number, then increment it:
python ~/.claude/skills/atlassian-api/scripts/atlassian.py PUT /wiki/api/v2/pages/123456789 \
  --data '{
    "id": "123456789",
    "status": "current",
    "title": "Updated Title",
    "body": {
      "representation": "storage",
      "value": "<p>Updated content</p>"
    },
    "version": {
      "number": 2,
      "message": "Updated via API"
    }
  }'
```

When updating a page, you need the current version number. GET the page first, then increment `version.number` by 1.

### Footer Comments

```bash
# Get footer comments for a page
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/pages/123456789/footer-comments

# Create footer comment
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /wiki/api/v2/footer-comments \
  --data '{"pageId":"123456789","body":{"representation":"storage","value":"<p>Comment text</p>"}}'
```

### Inline Comments

```bash
# Get inline comments for a page
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/pages/123456789/inline-comments

# Create inline comment
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /wiki/api/v2/inline-comments \
  --data '{
    "pageId": "123456789",
    "body": {"representation": "storage", "value": "<p>Inline comment</p>"},
    "inlineCommentProperties": {
      "textSelection": "text to highlight",
      "textSelectionMatchCount": 1,
      "textSelectionMatchIndex": 0
    }
  }'
```

### Comment Children (Replies)

```bash
# Footer comment replies
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/footer-comments/789/children

# Inline comment replies
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/inline-comments/789/children
```

## Confluence Attachments (bonus — not in MCP)

```bash
# List attachments on a page
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/pages/123456789/attachments

# Upload attachment (use curl for multipart)
CREDS=$(python3 -c "
creds={}
for line in open('$HOME/.atlassian-credentials'):
    if '=' in line:
        k,v = line.strip().split('=',1)
        creds[k.strip()] = v.strip()
print(f\"{creds['email']}:{creds['token']}\")
")
curl -u "$CREDS" -X PUT \
  "https://johnholland.atlassian.net/wiki/rest/api/content/123456789/child/attachment" \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@/path/to/document.pdf"
```

## Confluence Labels (bonus — not in MCP)

```bash
# Get labels on a page
python ~/.claude/skills/atlassian-api/scripts/atlassian.py GET /wiki/api/v2/pages/123456789/labels

# Add label
python ~/.claude/skills/atlassian-api/scripts/atlassian.py POST /wiki/rest/api/content/123456789/label \
  --data '[{"prefix":"global","name":"architecture"}]'
```

## Error Handling

The script exits with code 1 on HTTP 4xx/5xx errors and prints the error body. Common errors:
- **401**: Token expired or invalid — regenerate at https://id.atlassian.com/manage-profile/security/api-tokens
- **403**: Insufficient permissions for the operation
- **404**: Issue/page doesn't exist or wrong site
- **400**: Malformed request (check JSON body and ADF format)

## ADF (Atlassian Document Format)

Jira v3 and Confluence v2 use ADF for rich text. Minimal ADF paragraph:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "Plain text here"}
      ]
    }
  ]
}
```

For simple text-only operations, use this template. For richer content (headings, lists, code blocks, mentions), see `references/adf-format.md`.
