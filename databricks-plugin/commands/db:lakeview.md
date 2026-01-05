---
description: Manage Lakeview dashboards
argument-hint: "[list|get|publish|unpublish|trash] [DASHBOARD_ID]"
---

# Lakeview Dashboards

Manage Lakeview dashboards (modern replacement for legacy SQL dashboards).

## Quick Reference

| Action | Command |
|--------|---------|
| List dashboards | `db_lakeview.py list -p PROFILE` |
| Get details | `db_lakeview.py get DASHBOARD_ID -p PROFILE` |
| Publish | `db_lakeview.py publish DASHBOARD_ID -p PROFILE` |
| Unpublish | `db_lakeview.py unpublish DASHBOARD_ID -p PROFILE` |
| Trash | `db_lakeview.py trash DASHBOARD_ID -p PROFILE` |

## Script Usage

```bash
# List all Lakeview dashboards
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_lakeview.py list -p DEV

# Get dashboard details
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_lakeview.py get abc123 -p DEV

# Get details as JSON
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_lakeview.py get abc123 -p DEV -o json

# Publish a dashboard
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_lakeview.py publish abc123 -p DEV

# Unpublish a dashboard
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_lakeview.py unpublish abc123 -p DEV

# Move to trash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_lakeview.py trash abc123 -p DEV
```

## Dashboard States

| State | Description |
|-------|-------------|
| `ACTIVE` | Dashboard is available |
| `TRASHED` | In trash (can be restored) |

## CLI Fallback

```bash
# List dashboards
databricks lakeview list -p DEV

# Get dashboard
databricks lakeview get abc123 -p DEV

# Publish
databricks lakeview publish abc123 -p DEV

# Trash
databricks lakeview trash abc123 -p DEV
```

## Python SDK

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List dashboards
for d in w.lakeview.list():
    print(f"{d.display_name}: {d.lifecycle_state.value}")

# Get dashboard
dashboard = w.lakeview.get(dashboard_id="abc123")
print(f"Path: {dashboard.path}")

# Publish
w.lakeview.publish(dashboard_id="abc123")
```

## Arguments

| Arg | Description |
|-----|-------------|
| `list` | List all dashboards |
| `get` | Get dashboard details |
| `publish` | Publish a dashboard |
| `unpublish` | Unpublish a dashboard |
| `trash` | Move dashboard to trash |
| `-p, --profile` | Databricks profile |
| `-o, --output` | Format: table, json, csv |
