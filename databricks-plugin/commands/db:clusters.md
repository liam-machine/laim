---
description: Manage Databricks Spark clusters
argument-hint: "[list|start|stop|get] [CLUSTER_ID] [-p PROFILE]"
---

# Databricks Clusters

Start, stop, and monitor Spark clusters.

## Quick Reference

| Action | Command |
|--------|---------|
| List all | `db_clusters.py list -p PROFILE` |
| List running | `db_clusters.py list --state RUNNING -p PROFILE` |
| Get details | `db_clusters.py get CLUSTER_ID -p PROFILE` |
| Start | `db_clusters.py start CLUSTER_ID -p PROFILE` |
| Stop | `db_clusters.py stop CLUSTER_ID -p PROFILE` |
| Restart | `db_clusters.py restart CLUSTER_ID -p PROFILE` |

## Script Usage

```bash
# List all clusters
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py list -p DEV

# List only running clusters
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py list -p DEV --state RUNNING

# Get cluster details
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py get abc123-def456 -p DEV

# Start a cluster and wait
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py start abc123-def456 -p DEV --wait

# Stop a cluster
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py stop abc123-def456 -p DEV

# JSON output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py list -p DEV -o json
```

## CLI Fallback

```bash
# List clusters
databricks clusters list -p DEV

# Get cluster (POSITIONAL, not --cluster-id)
databricks clusters get CLUSTER_ID -p DEV

# Start cluster
databricks clusters start CLUSTER_ID -p DEV

# Stop cluster (called "delete" in CLI)
databricks clusters delete CLUSTER_ID -p DEV
```

## Python SDK

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List running clusters
for c in w.clusters.list():
    if c.state.value == "RUNNING":
        print(f"{c.cluster_name}: {c.cluster_id}")

# Start cluster and wait
w.clusters.start_and_wait(cluster_id="abc123-def456")

# Get cluster details
cluster = w.clusters.get(cluster_id="abc123-def456")
print(f"State: {cluster.state.value}")
```

## Cluster States

| State | Meaning |
|-------|---------|
| `PENDING` | Starting up |
| `RUNNING` | Ready to use |
| `RESTARTING` | Restarting |
| `RESIZING` | Changing size |
| `TERMINATING` | Shutting down |
| `TERMINATED` | Stopped |
| `ERROR` | Failed to start |

## Arguments

| Arg | Description |
|-----|-------------|
| `list` | List all clusters |
| `get` | Get cluster details |
| `start` | Start a cluster |
| `stop` | Stop a cluster |
| `restart` | Restart a cluster |
| `-p, --profile` | Databricks profile |
| `--state` | Filter by state |
| `--wait` | Wait for operation to complete |
| `-o, --output` | Format: table, json, csv |
