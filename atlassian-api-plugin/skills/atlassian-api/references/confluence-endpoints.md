# Confluence Cloud REST API v2 — Detailed Endpoint Reference

**Base URL:** `https://johnholland.atlassian.net`

**Authentication:** Basic Auth using `email:api_token`.

**Note:** CQL search uses v1 API (no v2 equivalent). All other operations use v2.

---

## 1. Search with CQL (v1)

Two options:

**`GET /wiki/rest/api/search`** — General search (recommended, searches content + spaces + users)

| Param | Type | Default | Description |
|---|---|---|---|
| `cql` | string | required | CQL query string |
| `cqlcontext` | string | optional | JSON context, e.g. `{"spaceKey":"DEV"}` |
| `expand` | string | optional | e.g. `content.body.storage` |
| `limit` | integer | 25 | Max results (max 250) |
| `start` | integer | 0 | Offset pagination |
| `cursor` | string | optional | Cursor pagination |
| `includeArchivedSpaces` | boolean | false | Include archived spaces |

**`GET /wiki/rest/api/content/search`** — Content-only search (same params minus `includeArchivedSpaces`)

### CQL Quick Reference

| Field | Examples |
|---|---|
| `type` | `type = page`, `type = blogpost` |
| `space` | `space = EDP` |
| `title` | `title = "Exact"` or `title ~ "fuzzy"` |
| `text` | `text ~ "deploy pipeline"` (full-text: title + body + labels) |
| `label` | `label = "draft"` or `label IN ("draft","review")` |
| `creator` | `creator = "accountId"` or `creator = currentUser()` |
| `ancestor` | `ancestor = 123456` (all descendants) |
| `parent` | `parent = 123456` (direct children) |
| `created` | `created > "2024-01-01"` |
| `lastModified` | `lastModified >= "2024-06-01"` |

**Operators:** `=`, `!=`, `~` (contains), `!~`, `>`, `>=`, `<`, `<=`, `IN`, `NOT IN`
**Keywords:** `AND`, `OR`, `NOT`, `ORDER BY` (asc/desc)

---

## 2. Get Page by ID

**`GET /wiki/api/v2/pages/{id}`**

| Param | Type | Description |
|---|---|---|
| `body-format` | string | `storage`, `atlas_doc_format`, or `view` |
| `version` | integer | Specific version number |
| `include-labels` | boolean | Include labels |
| `include-properties` | boolean | Include content properties |
| `include-versions` | boolean | Include version history |

**Body format options:**
- `storage` — Confluence XHTML-like markup (native read/write format)
- `atlas_doc_format` — ADF JSON structure
- `view` — Rendered HTML (read-only)

---

## 3. List Spaces

**`GET /wiki/api/v2/spaces`**

| Param | Type | Description |
|---|---|---|
| `ids` | array | Filter by space IDs |
| `keys` | array | Filter by space keys |
| `type` | string | `global` or `personal` |
| `status` | string | `current` or `archived` |
| `labels` | array | Filter by space labels |
| `favourite` | boolean | Only favourited spaces |
| `limit` | integer | Max results (1-250, default 25) |
| `cursor` | string | Pagination cursor |

---

## 4. Get Pages in Space

**`GET /wiki/api/v2/spaces/{id}/pages`**

Note: `{id}` is the **space ID** (numeric), not the space key.

| Param | Type | Description |
|---|---|---|
| `status` | string | `current`, `archived`, `trashed` |
| `title` | string | Filter by page title |
| `body-format` | string | `storage`, `atlas_doc_format`, `view` |
| `sort` | string | e.g. `title`, `-modified-date`, `created-date` |
| `limit` | integer | Max results (1-250, default 25) |
| `cursor` | string | Pagination cursor |

---

## 5. Children & Descendants

**Children (direct only):** `GET /wiki/api/v2/pages/{id}/children`

**Descendants (all levels):** `GET /wiki/api/v2/pages/{id}/descendants`

| Param | Type | Description |
|---|---|---|
| `limit` | integer | Max results (1-250) |
| `cursor` | string | Pagination cursor |
| `sort` | string | Sort order |
| `status` | string | `current`, `archived`, `trashed` |

---

## 6. Create Page

**`POST /wiki/api/v2/pages`**

```json
{
  "spaceId": "65541",
  "status": "current",
  "title": "Page Title",
  "parentId": "98765",
  "body": {
    "representation": "storage",
    "value": "<p>Content here</p>"
  }
}
```

- `spaceId` (required): Numeric space ID
- `title` (required): Page title
- `body` (required): With `representation` (`storage` or `atlas_doc_format`) and `value`
- `parentId` (optional): Parent page ID (omit for root-level)
- `status`: `current` (published) or `draft`

Response: 201 with full page object.

---

## 7. Update Page

**`PUT /wiki/api/v2/pages/{id}`**

```json
{
  "id": "123456789",
  "status": "current",
  "title": "Updated Title",
  "body": {
    "representation": "storage",
    "value": "<p>Updated content</p>"
  },
  "version": {
    "number": 6,
    "message": "Updated via API"
  }
}
```

**Important:** `version.number` must be current version + 1. GET the page first to find current version.

---

## 8. Footer Comments

**Get:** `GET /wiki/api/v2/pages/{id}/footer-comments`

| Param | Type | Description |
|---|---|---|
| `body-format` | string | `storage` or `atlas_doc_format` |
| `sort` | string | `created-date`, `-created-date` |
| `limit` | integer | Max results (1-250, default 25) |
| `status` | string | `current`, `archived`, `trashed`, `deleted`, `historical`, `draft` |

**Create:** `POST /wiki/api/v2/footer-comments`

```json
{
  "pageId": "123456789",
  "body": {"representation": "storage", "value": "<p>Comment text</p>"},
  "parentCommentId": "optional-for-replies"
}
```

---

## 9. Inline Comments

**Get:** `GET /wiki/api/v2/pages/{id}/inline-comments`

Extra param: `resolution-status` — `open`, `resolved`, `dangling`, `reopened`

**Create:** `POST /wiki/api/v2/inline-comments`

```json
{
  "pageId": "123456789",
  "body": {"representation": "storage", "value": "<p>Comment</p>"},
  "inlineCommentProperties": {
    "textSelection": "text to highlight",
    "textSelectionMatchCount": 1,
    "textSelectionMatchIndex": 0
  }
}
```

---

## 10. Comment Children (Replies)

**Footer:** `GET /wiki/api/v2/footer-comments/{id}/children`
**Inline:** `GET /wiki/api/v2/inline-comments/{id}/children`

Both support `body-format`, `sort`, `cursor`, `limit` params.

---

## Attachments (bonus)

**List:** `GET /wiki/api/v2/pages/{id}/attachments`

**Upload** (v1, multipart):
```bash
curl -u email:token -X PUT \
  "https://johnholland.atlassian.net/wiki/rest/api/content/{pageId}/child/attachment" \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@/path/to/file.pdf"
```

---

## Labels (bonus)

**Get:** `GET /wiki/api/v2/pages/{id}/labels`

**Add (v1):** `POST /wiki/rest/api/content/{id}/label`
```json
[{"prefix": "global", "name": "architecture"}]
```

---

## Pagination

All v2 list endpoints use cursor-based pagination:
- Response includes `_links.next` with cursor URL
- Default limit: 25 (max 250)
- Follow `_links.next` until it's absent

v1 search uses offset-based: `start` + `limit` + `size` (stop when `size < limit`).

---

## Quick Reference

| # | Operation | Method | Path |
|---|---|---|---|
| 1 | CQL Search | GET | `/wiki/rest/api/search` (v1) |
| 2 | Get Page | GET | `/wiki/api/v2/pages/{id}` |
| 3 | List Spaces | GET | `/wiki/api/v2/spaces` |
| 4 | Pages in Space | GET | `/wiki/api/v2/spaces/{id}/pages` |
| 5a | Children | GET | `/wiki/api/v2/pages/{id}/children` |
| 5b | Descendants | GET | `/wiki/api/v2/pages/{id}/descendants` |
| 6 | Create Page | POST | `/wiki/api/v2/pages` |
| 7 | Update Page | PUT | `/wiki/api/v2/pages/{id}` |
| 8 | Footer Comments | GET | `/wiki/api/v2/pages/{id}/footer-comments` |
| 9 | Inline Comments | GET | `/wiki/api/v2/pages/{id}/inline-comments` |
| 10 | Comment Replies | GET | `/wiki/api/v2/{footer\|inline}-comments/{id}/children` |
| 11 | Create Footer | POST | `/wiki/api/v2/footer-comments` |
| 12 | Create Inline | POST | `/wiki/api/v2/inline-comments` |
| 13 | Attachments | GET | `/wiki/api/v2/pages/{id}/attachments` |
| 14 | Labels | GET | `/wiki/api/v2/pages/{id}/labels` |
