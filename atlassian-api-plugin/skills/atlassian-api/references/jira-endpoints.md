# Jira Cloud REST API v3 — Detailed Endpoint Reference

**Base URL:** `https://johnholland.atlassian.net`

**Authentication:** Basic Auth using `email:api_token`, base64-encoded.

**Note:** All rich text fields (description, comment body, etc.) use **ADF (Atlassian Document Format)**, not plain strings.

---

## 1. Search Issues with JQL

**`POST /rest/api/3/search/jql`** (new endpoint — old `/rest/api/3/search` returns 410)

| Field | Type | Required | Description |
|---|---|---|---|
| `jql` | string | Yes | JQL query string |
| `startAt` | integer | No | Page offset (default 0) |
| `maxResults` | integer | No | Max issues per page (default 50, max 100) |
| `fields` | string[] | No | Fields to return (e.g. `["summary","status","assignee"]`) |
| `expand` | string[] | No | `renderedFields`, `names`, `schema`, `transitions`, `operations`, `editmeta`, `changelog` |
| `validateQuery` | string | No | `strict`, `warn`, or `none` |

---

## 2. Get Issue

**`GET /rest/api/3/issue/{issueIdOrKey}`**

| Param | Type | Description |
|---|---|---|
| `fields` | string | Comma-separated. `*all`, `*navigable`, or field names. Prefix `-` to exclude. |
| `expand` | string | `renderedFields`, `names`, `schema`, `transitions`, `editmeta`, `changelog` |
| `properties` | string | Issue property keys. `*all` or specific keys. |

---

## 3. Create Issue

**`POST /rest/api/3/issue`**

Required fields inside `fields`:
- `project` — `{"key": "PROJ"}` or `{"id": "10000"}`
- `issuetype` — `{"name": "Task"}` or `{"id": "10001"}`
- `summary` — string

Optional: `description` (ADF), `assignee` (`{"accountId": "..."}"`), `priority` (`{"name": "High"}`), `labels`, `components`, `parent` (for subtasks).

Response (201): `{"id": "10000", "key": "PROJ-1", "self": "..."}`

---

## 4. Edit Issue

**`PUT /rest/api/3/issue/{issueIdOrKey}`**

| Param | Type | Description |
|---|---|---|
| `notifyUsers` | boolean | Send email notifications (default true) |
| `returnIssue` | boolean | Return updated issue in response |

Body uses `fields` for simple sets, `update` for add/remove/set operations. A field cannot appear in both.

Response: 204 (no content) by default.

---

## 5. Get Transitions

**`GET /rest/api/3/issue/{issueIdOrKey}/transitions`**

| Param | Type | Description |
|---|---|---|
| `expand` | string | `transitions.fields` for screen field metadata |
| `includeUnavailableTransitions` | boolean | Include transitions that fail conditions |

Response includes `transitions[]` array with `id`, `name`, `to` (status object).

---

## 6. Transition Issue

**`POST /rest/api/3/issue/{issueIdOrKey}/transitions`**

| Field | Type | Required | Description |
|---|---|---|---|
| `transition` | object | Yes | `{"id": "31"}` — the transition ID |
| `fields` | object | No | Screen fields to set during transition |
| `update` | object | No | Field update operations |

Response: 204 (no content).

---

## 7. Add Comment

**`POST /rest/api/3/issue/{issueIdOrKey}/comment`**

| Field | Type | Required | Description |
|---|---|---|---|
| `body` | ADF object | Yes | Comment body |
| `visibility` | object | No | `{"type": "role"/"group", "value": "..."}` |

Response (201): Comment object with `id`, `author`, `body`, `created`, `updated`.

---

## 8. Get Projects

**`GET /rest/api/3/project/search`**

| Param | Type | Description |
|---|---|---|
| `maxResults` | integer | Max results (default 50, max 50) |
| `startAt` | integer | Page offset |
| `query` | string | Filter by project name (prefix match) |
| `typeKey` | string | `software`, `service_desk`, `business` |
| `action` | string | `view`, `browse`, `edit`, `create` — permission filter |
| `expand` | string | `description`, `projectKeys`, `lead`, `issueTypes`, `url`, `insight` |

---

## 9. User Search

**`GET /rest/api/3/user/search`** — Simple search

| Param | Type | Description |
|---|---|---|
| `query` | string | Matches displayName, emailAddress |
| `maxResults` | integer | Default 50 |

**`GET /rest/api/3/user/picker`** — Autocomplete-style

| Param | Type | Description |
|---|---|---|
| `query` | string | Required. Prefix match. |
| `maxResults` | integer | Default 50 |
| `showAvatar` | boolean | Include avatar URI |

---

## 10. Issue Link Types

**`GET /rest/api/3/issueLinkType`** — No parameters.

Returns `issueLinkTypes[]` with `id`, `name`, `inward`, `outward`.

---

## 11. Create Issue Link

**`POST /rest/api/3/issueLink`**

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | object | Yes | `{"name": "Blocks"}` or `{"id": "10000"}` |
| `inwardIssue` | object | Yes | `{"key": "HSP-1"}` |
| `outwardIssue` | object | Yes | `{"key": "MKY-1"}` |
| `comment` | object | No | Comment with ADF body |

Response: 201 (no body).

---

## 12. Add Worklog

**`POST /rest/api/3/issue/{issueIdOrKey}/worklog`**

| Field | Type | Required | Description |
|---|---|---|---|
| `timeSpent` | string | Yes* | Duration, e.g. `"2h 30m"`, `"1d"` |
| `timeSpentSeconds` | integer | Yes* | Alternative in seconds |
| `started` | string | No | ISO 8601 datetime. Defaults to now. |
| `comment` | ADF object | No | Worklog comment |
| `visibility` | object | No | Restriction |

*One of `timeSpent` or `timeSpentSeconds` required.

Query param `adjustEstimate`: `auto` (default), `new`, `leave`, `manual`.

---

## 13. Issue Type Metadata

**`GET /rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes`**

Returns `issueTypes[]` with `id`, `name`, `description`, `subtask`, `hierarchyLevel`.

For field metadata: **`GET /rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes/{issueTypeId}`**

---

## 14. Get Current User

**`GET /rest/api/3/myself`**

Query param `expand`: `groups`, `applicationRoles`.

Returns user object with `accountId`, `emailAddress`, `displayName`, `active`, `timeZone`, `locale`.

---

## 15. Remote Issue Links

**`GET /rest/api/3/issue/{issueIdOrKey}/remotelink`**

Query param `globalId`: Filter by specific remote link.

Returns array of remote link objects with `id`, `globalId`, `application`, `relationship`, `object` (url, title, summary, status).

---

## Agile API (bonus)

Base: `/rest/agile/1.0/`

| Operation | Method | Path |
|---|---|---|
| List boards | GET | `/rest/agile/1.0/board` |
| Get board sprints | GET | `/rest/agile/1.0/board/{boardId}/sprint` |
| Get sprint issues | GET | `/rest/agile/1.0/sprint/{sprintId}/issue` |
| Get backlog | GET | `/rest/agile/1.0/board/{boardId}/backlog` |
| Get board config | GET | `/rest/agile/1.0/board/{boardId}/configuration` |
| Move issues to sprint | POST | `/rest/agile/1.0/sprint/{sprintId}/issue` |

---

## ADF Quick Reference

Minimal text paragraph:
```json
{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Your text"}]}]}
```

Heading:
```json
{"type":"heading","attrs":{"level":2},"content":[{"type":"text","text":"Heading text"}]}
```

Bullet list:
```json
{"type":"bulletList","content":[{"type":"listItem","content":[{"type":"paragraph","content":[{"type":"text","text":"Item 1"}]}]}]}
```

Code block:
```json
{"type":"codeBlock","attrs":{"language":"python"},"content":[{"type":"text","text":"print('hello')"}]}
```

Mention:
```json
{"type":"mention","attrs":{"id":"accountId","text":"@Display Name","accessLevel":""}}
```
