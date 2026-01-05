---
description: Databricks Asset Bundles (DAB) deployment
argument-hint: "[validate|deploy|destroy|run|summary] [-t TARGET]"
---

# Databricks Deploy

Manage Databricks Asset Bundles (DAB) for infrastructure as code deployments.

## Quick Reference

| Action | Command |
|--------|---------|
| Validate bundle | `db_deploy.py validate -t TARGET -p PROFILE` |
| Deploy bundle | `db_deploy.py deploy -t TARGET -p PROFILE` |
| Destroy resources | `db_deploy.py destroy -t TARGET -p PROFILE` |
| Run bundle job | `db_deploy.py run JOB_KEY -t TARGET -p PROFILE` |
| View summary | `db_deploy.py summary -t TARGET -p PROFILE` |

## Script Usage

```bash
# Validate bundle configuration
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_deploy.py validate -t dev -p DEV

# Deploy to dev target
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_deploy.py deploy -t dev -p DEV

# Deploy to production
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_deploy.py deploy -t prod -p PROD

# Run a job defined in the bundle
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_deploy.py run my_etl_job -t dev -p DEV

# View deployment summary
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_deploy.py summary -t dev -p DEV

# Destroy all deployed resources
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_deploy.py destroy -t dev -p DEV
```

## Bundle Structure

Databricks Asset Bundles use a `databricks.yml` file:

```yaml
bundle:
  name: my-data-pipeline

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://dbc-xxx.cloud.databricks.com

  prod:
    mode: production
    workspace:
      host: https://dbc-yyy.cloud.databricks.com

resources:
  jobs:
    my_etl_job:
      name: "My ETL Job"
      tasks:
        - task_key: extract
          notebook_task:
            notebook_path: ./notebooks/extract.py
```

## Targets

Targets define deployment environments:

| Target | Use Case |
|--------|----------|
| `dev` | Development/testing |
| `staging` | Pre-production |
| `prod` | Production |

## CLI Fallback

```bash
# Validate
databricks bundle validate -t dev -p DEV

# Deploy
databricks bundle deploy -t dev -p DEV

# Run job
databricks bundle run my_etl_job -t dev -p DEV

# Destroy
databricks bundle destroy -t dev -p DEV --auto-approve

# Summary
databricks bundle summary -t dev -p DEV
```

## Prerequisites

1. **Databricks CLI v0.200+**: Required for bundle commands
   ```bash
   pip install databricks-cli
   databricks --version
   ```

2. **databricks.yml**: Bundle configuration in project root

3. **Profile configuration**: `~/.databrickscfg` with workspace credentials

## Common Workflows

### Initial Deployment
```bash
# Validate first
db_deploy.py validate -t dev -p DEV

# Deploy if valid
db_deploy.py deploy -t dev -p DEV

# Run to test
db_deploy.py run my_job -t dev -p DEV
```

### Promote to Production
```bash
# Deploy to prod
db_deploy.py deploy -t prod -p PROD

# Verify
db_deploy.py summary -t prod -p PROD
```

### Teardown
```bash
# Destroy all resources
db_deploy.py destroy -t dev -p DEV
```

## Arguments

| Arg | Description |
|-----|-------------|
| `validate` | Validate bundle configuration |
| `deploy` | Deploy bundle to target |
| `destroy` | Destroy deployed resources |
| `run` | Run a job from the bundle |
| `summary` | Show deployment summary |
| `-t, --target` | Deployment target (dev, prod, etc.) |
| `-p, --profile` | Databricks profile |
