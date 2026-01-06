---
name: databricks
description: Comprehensive Databricks administration - SQL queries, code execution, clusters, warehouses, jobs, secrets, Unity Catalog, pipelines, dashboards, permissions, and bundle deployments. Triggers on "run query on Databricks", "execute on cluster", "Spark query", "PySpark", "databricks REPL", "check job status", "start cluster", "list warehouses", "deploy bundle", "manage secrets", "Unity Catalog", "DLT pipeline", "Lakeview dashboard", or any Databricks administration task.
---

# Databricks

Comprehensive Databricks administration across multiple workspaces.

## Command Routing

Route to the appropriate command based on the task:

| Task | Command | When to Use |
|------|---------|-------------|
| **Execute SQL** | `/db:query` | SQL queries via SQL warehouses |
| **Execute code** | `/db:execute` | Python/SQL/Scala/R on Spark clusters |
| **Manage clusters** | `/db:clusters` | Start, stop, list Spark clusters |
| **Manage warehouses** | `/db:warehouses` | Start, stop, list SQL warehouses |
| **Manage jobs** | `/db:jobs` | List, trigger, cancel jobs |
| **Manage secrets** | `/db:secrets` | Secret scopes and values |
| **Unity Catalog** | `/db:catalog` | Catalogs, schemas, tables, volumes, grants |
| **Pipelines** | `/db:pipelines` | Delta Live Tables / Lakeflow |
| **Dashboards** | `/db:lakeview` | Lakeview dashboard management |
| **Permissions** | `/db:permissions` | Object-level ACLs and grants |
| **Deploy bundles** | `/db:deploy` | DAB validate, deploy, destroy |
| **Profiles** | `/db:profiles` | List and test workspace profiles |
| **Setup** | `/db:setup` | Initial configuration |

## Quick Start

### Check Available Profiles

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py list
```

### Execute SQL on Warehouses

```bash
# Using default profile
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_query.py -c "SHOW DATABASES"

# Using specific profile
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_query.py -c "SELECT * FROM catalog.schema.table LIMIT 10" -p DEV
```

### Execute Code on Clusters

```bash
# Python on Spark cluster
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -c "print(spark.version)" -p DEV

# SQL on Spark cluster
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -l sql -c "SHOW DATABASES" -p DEV

# Interactive REPL
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py --repl -p DEV
```

### Manage Clusters

```bash
# List all clusters
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py list -p DEV

# Start a cluster
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py start CLUSTER_ID -p DEV --wait
```

### Manage Warehouses

```bash
# List warehouses
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py list -p DEV

# Start a warehouse
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py start WAREHOUSE_ID -p DEV --wait
```

### Manage Jobs

```bash
# List jobs
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py list -p DEV

# Run a job
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py run JOB_ID -p DEV --wait

# Check recent runs
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py runs JOB_ID -p DEV --limit 5
```

## Profile System

The plugin reads workspace profiles from `~/.databrickscfg`:

```ini
[DEV]
host  = https://dbc-xxx.cloud.databricks.com
token = dapi...

[PROD]
host  = https://dbc-yyy.cloud.databricks.com
token = dapi...
```

### Profile Selection Priority

1. Explicit `-p PROFILE` argument
2. `DATABRICKS_PROFILE` environment variable
3. Plugin config `default_profile` (if configured)
4. `DEFAULT` profile (if exists)
5. First available profile

### Test a Profile

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py test DEV
```

## CLI Fallback

For operations not covered by scripts, use the Databricks CLI directly:

```bash
# Always specify profile with -p
databricks clusters list -p DEV
databricks jobs list -p PROD
databricks bundle deploy -t prod -p DEV
```

## SDK Usage

For complex operations, use the Python SDK:

```python
from databricks.sdk import WorkspaceClient

# Uses profile from ~/.databrickscfg
w = WorkspaceClient(profile="DEV")

# List running clusters
for c in w.clusters.list():
    if c.state.value == "RUNNING":
        print(f"{c.cluster_name}: {c.cluster_id}")

# Execute SQL
result = w.statement_execution.execute_statement(
    warehouse_id="warehouse-id",
    statement="SELECT * FROM table LIMIT 10",
    wait_timeout="30s"
)
```

## Prerequisites

### Required
- **~/.databrickscfg** - Profile configuration with host and token
- **databricks-sdk** - `pip install databricks-sdk`

### Optional
- **databricks-cli** - For bundle deployments and advanced operations
- **~/.databricks-plugin/config.yaml** - Plugin-specific settings

## Resources

- **scripts/** - Executable Python scripts for each operation
- **references/configuration.md** - Setup and authentication guide
- **references/cli-reference.md** - CLI command patterns
- **references/lakeview-dashboards.md** - Lakeview dashboard architecture and patterns
