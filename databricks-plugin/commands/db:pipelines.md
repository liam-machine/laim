---
description: Manage Delta Live Tables / Lakeflow pipelines
argument-hint: "[list|get|start|stop|updates|events] [PIPELINE_ID]"
---

# Databricks Pipelines

Manage Delta Live Tables (DLT) and Lakeflow declarative pipelines.

## Quick Reference

| Action | Command |
|--------|---------|
| List pipelines | `db_pipelines.py list -p PROFILE` |
| Get details | `db_pipelines.py get PIPELINE_ID -p PROFILE` |
| Start update | `db_pipelines.py start PIPELINE_ID -p PROFILE` |
| Start and wait | `db_pipelines.py start PIPELINE_ID -p PROFILE --wait` |
| Full refresh | `db_pipelines.py start PIPELINE_ID -p PROFILE --full-refresh` |
| Stop pipeline | `db_pipelines.py stop PIPELINE_ID -p PROFILE` |
| View updates | `db_pipelines.py updates PIPELINE_ID -p PROFILE` |
| View events | `db_pipelines.py events PIPELINE_ID -p PROFILE` |

## Script Usage

```bash
# List all pipelines
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_pipelines.py list -p DEV

# Get pipeline details
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_pipelines.py get abc123-def456 -p DEV

# Start a pipeline update
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_pipelines.py start abc123-def456 -p DEV

# Start and wait for completion
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_pipelines.py start abc123-def456 -p DEV --wait

# Full refresh (recompute all tables)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_pipelines.py start abc123-def456 -p DEV --full-refresh --wait

# Stop a running pipeline
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_pipelines.py stop abc123-def456 -p DEV

# View recent updates
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_pipelines.py updates abc123-def456 -p DEV --limit 5

# View pipeline events (for debugging)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_pipelines.py events abc123-def456 -p DEV --limit 20
```

## Pipeline States

| State | Description |
|-------|-------------|
| `IDLE` | Not running |
| `RUNNING` | Update in progress |
| `STOPPING` | Shutting down |
| `FAILED` | Last update failed |
| `DELETED` | Pipeline deleted |

## Update States

| State | Description |
|-------|-------------|
| `QUEUED` | Waiting to start |
| `CREATED` | Initializing |
| `RUNNING` | Processing |
| `COMPLETED` | Finished successfully |
| `FAILED` | Failed with errors |
| `CANCELED` | Manually stopped |

## CLI Fallback

```bash
# List pipelines
databricks pipelines list-pipelines -p DEV

# Get pipeline
databricks pipelines get abc123-def456 -p DEV

# Start update
databricks pipelines start-update abc123-def456 -p DEV

# Stop
databricks pipelines stop abc123-def456 -p DEV
```

## Python SDK

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List pipelines
for p in w.pipelines.list_pipelines():
    print(f"{p.name}: {p.state.value}")

# Start update
response = w.pipelines.start_update(
    pipeline_id="abc123",
    full_refresh=True
)
print(f"Started: {response.update_id}")

# Wait for update
w.pipelines.wait_get_pipeline_running(pipeline_id="abc123")
```

## Arguments

| Arg | Description |
|-----|-------------|
| `list` | List all pipelines |
| `get` | Get pipeline details |
| `start` | Start a pipeline update |
| `stop` | Stop a running pipeline |
| `updates` | List recent updates |
| `events` | List pipeline events |
| `--wait` | Wait for completion |
| `--full-refresh` | Recompute all tables |
| `--limit` | Max results to return |
| `-p, --profile` | Databricks profile |
| `-o, --output` | Format: table, json, csv |
