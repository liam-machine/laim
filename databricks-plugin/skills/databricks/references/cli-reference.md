# Databricks CLI Reference

Quick reference for Databricks CLI commands. Always use `-p PROFILE` for workspace selection.

## Installation

```bash
# Via pip
pip install databricks-cli

# Via Homebrew (macOS)
brew install databricks
```

## Clusters

```bash
# List clusters
databricks clusters list -p PROFILE

# Get cluster details (POSITIONAL, not --cluster-id)
databricks clusters get CLUSTER_ID -p PROFILE

# Start cluster
databricks clusters start CLUSTER_ID -p PROFILE

# Stop cluster (called "delete")
databricks clusters delete CLUSTER_ID -p PROFILE

# Restart cluster
databricks clusters restart CLUSTER_ID -p PROFILE

# Create cluster
databricks clusters create --json '{...}' -p PROFILE
```

## SQL Warehouses

```bash
# List warehouses
databricks warehouses list -p PROFILE

# Get warehouse
databricks warehouses get WAREHOUSE_ID -p PROFILE

# Start warehouse
databricks warehouses start WAREHOUSE_ID -p PROFILE

# Stop warehouse
databricks warehouses stop WAREHOUSE_ID -p PROFILE
```

## Jobs

```bash
# List jobs
databricks jobs list -p PROFILE

# Filter by name
databricks jobs list --name "ETL Job" -p PROFILE

# Get job (POSITIONAL)
databricks jobs get JOB_ID -p PROFILE

# Run job
databricks jobs run-now JOB_ID -p PROFILE

# Run with parameters
databricks jobs run-now JOB_ID --json '{"notebook_params": {"key": "value"}}' -p PROFILE

# List runs
databricks jobs list-runs --job-id JOB_ID --limit 10 -p PROFILE

# Get run
databricks jobs get-run RUN_ID -p PROFILE

# Get run output
databricks jobs get-run-output RUN_ID -p PROFILE

# Cancel run
databricks jobs cancel-run RUN_ID -p PROFILE
```

## SQL Queries

```bash
# Execute via API
databricks api post /api/2.0/sql/statements --json '{
  "warehouse_id": "WAREHOUSE_ID",
  "statement": "SELECT * FROM table LIMIT 10"
}' -p PROFILE
```

## Secrets

```bash
# List scopes
databricks secrets list-scopes -p PROFILE

# List secrets in scope
databricks secrets list-secrets SCOPE -p PROFILE

# Put secret
databricks secrets put-secret SCOPE KEY --string-value "value" -p PROFILE

# Create scope
databricks secrets create-scope SCOPE -p PROFILE

# Delete secret
databricks secrets delete-secret SCOPE KEY -p PROFILE
```

## Unity Catalog

```bash
# List catalogs
databricks catalogs list -p PROFILE

# List schemas
databricks schemas list CATALOG -p PROFILE

# List tables
databricks tables list CATALOG.SCHEMA -p PROFILE

# Describe table
databricks tables get CATALOG.SCHEMA.TABLE -p PROFILE
```

## Workspace Files

```bash
# List
databricks workspace list /path -p PROFILE

# Import
databricks workspace import-dir ./local/path /Workspace/remote/path -p PROFILE

# Export
databricks workspace export-dir /Workspace/path ./local/path -p PROFILE
```

## Databricks Asset Bundles (DAB)

```bash
# Validate bundle
databricks bundle validate -t TARGET -p PROFILE

# Deploy bundle
databricks bundle deploy -t TARGET -p PROFILE

# Run bundle job
databricks bundle run JOB_NAME -t TARGET -p PROFILE

# Destroy bundle resources
databricks bundle destroy -t TARGET -p PROFILE
```

## Apps

```bash
# List apps
databricks apps list -p PROFILE

# Get app
databricks apps get APP_NAME -p PROFILE

# Deploy app
databricks apps deploy APP_NAME -p PROFILE

# View logs
databricks apps logs APP_NAME -p PROFILE
databricks apps logs APP_NAME --follow -p PROFILE

# Start/stop
databricks apps start APP_NAME -p PROFILE
databricks apps stop APP_NAME -p PROFILE
```

## Permissions

```bash
# Get permissions
databricks permissions get JOB JOB_ID -p PROFILE

# Update permissions (PATCH - additive)
databricks permissions update JOB JOB_ID --json '{
  "access_control_list": [
    {"user_name": "user@example.com", "permission_level": "CAN_VIEW"}
  ]
}' -p PROFILE
```

**Permission Levels:**
- `IS_OWNER`, `CAN_MANAGE`, `CAN_MANAGE_RUN`, `CAN_VIEW`

## Common Gotchas

| Issue | Solution |
|-------|----------|
| `jobs get --job-id 123` | Use positional: `jobs get 123` |
| `get-run-output` on multi-task | Get individual task run IDs first |
| `permissions set` removes all | Use `update` (PATCH) not `set` (PUT) |
| Secrets with newlines | Use file input: `--binary-file` |

## Output Formats

```bash
# Default (text)
databricks jobs list -p PROFILE

# JSON
databricks jobs list -o json -p PROFILE

# JQ for parsing
databricks jobs list -o json -p PROFILE | jq '.[].job_id'
```
