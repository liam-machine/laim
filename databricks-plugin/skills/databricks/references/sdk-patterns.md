# Databricks Python SDK Patterns

Common patterns for using the Databricks SDK in Python.

## Installation

```bash
pip install databricks-sdk
```

## Client Initialization

```python
from databricks.sdk import WorkspaceClient

# Using profile from ~/.databrickscfg
w = WorkspaceClient(profile="DEV")

# Explicit configuration
w = WorkspaceClient(
    host="https://workspace.cloud.databricks.com",
    token="dapi..."
)

# From environment variables
# Set DATABRICKS_HOST and DATABRICKS_TOKEN
w = WorkspaceClient()
```

## SQL Queries

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# Simple query
result = w.statement_execution.execute_statement(
    warehouse_id="warehouse-id",
    statement="SELECT * FROM catalog.schema.table LIMIT 10",
    wait_timeout="30s"
)

# Access results
for row in result.result.data_array:
    print(row)

# Get column names
columns = [col.name for col in result.manifest.schema.columns]

# With parameters (prevents SQL injection)
result = w.statement_execution.execute_statement(
    warehouse_id="warehouse-id",
    statement="SELECT * FROM table WHERE date = :date_param",
    parameters=[{"name": "date_param", "value": "2024-01-01"}],
    wait_timeout="30s"
)
```

## Clusters

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List clusters
for cluster in w.clusters.list():
    print(f"{cluster.cluster_name}: {cluster.state.value}")

# Get cluster
cluster = w.clusters.get(cluster_id="abc123")

# Start and wait
w.clusters.start_and_wait(cluster_id="abc123")

# Stop
w.clusters.delete(cluster_id="abc123")

# Restart and wait
w.clusters.restart_and_wait(cluster_id="abc123")
```

## SQL Warehouses

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List warehouses
for wh in w.warehouses.list():
    print(f"{wh.name}: {wh.state.value}")

# Get warehouse
warehouse = w.warehouses.get(id="abc123")

# Start and wait
w.warehouses.start_and_wait(id="abc123")

# Stop
w.warehouses.stop(id="abc123")
```

## Jobs

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List jobs
for job in w.jobs.list():
    print(f"{job.job_id}: {job.settings.name}")

# Get job
job = w.jobs.get(job_id=12345)

# Run job and wait
run = w.jobs.run_now_and_wait(job_id=12345)
print(f"Result: {run.state.result_state.value}")

# Run with parameters
run = w.jobs.run_now_and_wait(
    job_id=12345,
    notebook_params={"date": "2024-01-01"}
)

# List runs
for run in w.jobs.list_runs(job_id=12345, limit=10):
    print(f"Run {run.run_id}: {run.state.result_state.value}")

# Cancel run
w.jobs.cancel_run(run_id=67890)

# Get run output
output = w.jobs.get_run_output(run_id=67890)
print(output.notebook_output.result)
```

## Secrets

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List scopes
for scope in w.secrets.list_scopes():
    print(scope.name)

# List secrets in scope
for secret in w.secrets.list_secrets(scope="my-scope"):
    print(secret.key)

# Put secret
w.secrets.put_secret(
    scope="my-scope",
    key="my-key",
    string_value="secret-value"
)

# Create scope
w.secrets.create_scope(scope="new-scope")

# Get secret (in notebooks only)
# dbutils.secrets.get(scope="my-scope", key="my-key").strip()
```

## Unity Catalog

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List catalogs
for catalog in w.catalogs.list():
    print(catalog.name)

# List schemas
for schema in w.schemas.list(catalog_name="my-catalog"):
    print(schema.name)

# List tables
for table in w.tables.list(catalog_name="my-catalog", schema_name="my-schema"):
    print(f"{table.full_name}: {table.table_type.value}")

# Get table
table = w.tables.get(full_name="catalog.schema.table")
print(table.columns)
```

## Error Handling

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound, PermissionDenied

w = WorkspaceClient(profile="DEV")

try:
    cluster = w.clusters.get(cluster_id="invalid-id")
except NotFound:
    print("Cluster not found")
except PermissionDenied:
    print("Access denied")
except Exception as e:
    print(f"Error: {e}")
```

## Async Operations

```python
from databricks.sdk import WorkspaceClient
import time

w = WorkspaceClient(profile="DEV")

# Start cluster (non-blocking)
w.clusters.start(cluster_id="abc123")

# Poll for completion
while True:
    cluster = w.clusters.get(cluster_id="abc123")
    if cluster.state.value == "RUNNING":
        print("Cluster is ready")
        break
    elif cluster.state.value in ["ERROR", "TERMINATED"]:
        print(f"Cluster failed: {cluster.state_message}")
        break
    time.sleep(10)

# Or use built-in wait methods
w.clusters.start_and_wait(cluster_id="abc123")  # Blocks until ready
```

## Pagination

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# SDK handles pagination automatically
all_jobs = list(w.jobs.list())  # Gets all jobs

# Or iterate lazily
for job in w.jobs.list():
    print(job.job_id)
    if some_condition:
        break  # Stop early without fetching all pages
```

## Current User

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# Get current user
me = w.current_user.me()
print(f"Logged in as: {me.user_name}")
print(f"Display name: {me.display_name}")
```
