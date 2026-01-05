---
description: Manage Databricks SQL warehouses
argument-hint: "[list|start|stop|get] [WAREHOUSE_ID] [-p PROFILE]"
---

# Databricks SQL Warehouses

Start, stop, and monitor SQL warehouses.

## Quick Reference

| Action | Command |
|--------|---------|
| List all | `db_warehouses.py list -p PROFILE` |
| List running | `db_warehouses.py list --state RUNNING -p PROFILE` |
| Get details | `db_warehouses.py get WAREHOUSE_ID -p PROFILE` |
| Start | `db_warehouses.py start WAREHOUSE_ID -p PROFILE` |
| Stop | `db_warehouses.py stop WAREHOUSE_ID -p PROFILE` |

## Script Usage

```bash
# List all warehouses
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py list -p DEV

# List only running warehouses
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py list -p DEV --state RUNNING

# Get warehouse details
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py get abc123 -p DEV

# Start a warehouse and wait
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py start abc123 -p DEV --wait

# Stop a warehouse
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py stop abc123 -p DEV

# JSON output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py list -p DEV -o json
```

## CLI Fallback

```bash
# List warehouses
databricks warehouses list -p DEV

# Get warehouse
databricks warehouses get WAREHOUSE_ID -p DEV

# Start warehouse
databricks warehouses start WAREHOUSE_ID -p DEV

# Stop warehouse
databricks warehouses stop WAREHOUSE_ID -p DEV
```

## Python SDK

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List running warehouses
for wh in w.warehouses.list():
    if wh.state.value == "RUNNING":
        print(f"{wh.name}: {wh.id}")

# Start warehouse and wait
w.warehouses.start_and_wait(id="abc123")

# Get warehouse details
warehouse = w.warehouses.get(id="abc123")
print(f"State: {warehouse.state.value}")
print(f"Size: {warehouse.cluster_size}")
```

## Warehouse States

| State | Meaning |
|-------|---------|
| `STARTING` | Starting up |
| `RUNNING` | Ready for queries |
| `STOPPING` | Shutting down |
| `STOPPED` | Not running |
| `DELETED` | Permanently removed |

## Warehouse Types

| Type | Description |
|------|-------------|
| **Serverless** | Auto-scaling, pay-per-query |
| **Classic** | Traditional provisioned clusters |
| **Pro** | Enhanced features (photon, etc.) |

## Arguments

| Arg | Description |
|-----|-------------|
| `list` | List all warehouses |
| `get` | Get warehouse details |
| `start` | Start a warehouse |
| `stop` | Stop a warehouse |
| `-p, --profile` | Databricks profile |
| `--state` | Filter by state |
| `--wait` | Wait for operation to complete |
| `-o, --output` | Format: table, json, csv |
