---
description: Execute SQL query on Databricks
argument-hint: "<sql-query> [-p PROFILE]"
---

# Databricks SQL Query

Execute SQL queries on Databricks.

## Quick Reference

| Action | Command |
|--------|---------|
| Run query | `db_query.py -c "SELECT ..." -p PROFILE` |
| Run from file | `db_query.py -f query.sql -p PROFILE` |
| Output as CSV | `db_query.py -c "SELECT ..." -o csv` |
| Output as JSON | `db_query.py -c "SELECT ..." -o json` |

## Script Usage

```bash
# Simple query
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_query.py \
  -c "SELECT * FROM catalog.schema.table LIMIT 10" \
  -p DEV

# Query with CSV output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_query.py \
  -c "SELECT * FROM table" \
  -p DEV \
  -o csv > output.csv

# Run query from file
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_query.py \
  -f complex_query.sql \
  -p PROD \
  -o json
```

## CLI Fallback

```bash
# Via API endpoint
databricks api post /api/2.0/sql/statements --json '{
  "warehouse_id": "WAREHOUSE_ID",
  "statement": "SELECT * FROM table LIMIT 10"
}' -p DEV
```

## Python SDK

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

result = w.statement_execution.execute_statement(
    warehouse_id="WAREHOUSE_ID",
    statement="SELECT * FROM catalog.schema.table LIMIT 10",
    wait_timeout="30s"
)

# Access results
for row in result.result.data_array:
    print(row)

# With parameters (prevents SQL injection)
result = w.statement_execution.execute_statement(
    warehouse_id="WAREHOUSE_ID",
    statement="SELECT * FROM table WHERE date = :date_param",
    parameters=[{"name": "date_param", "value": "2024-01-01"}],
    wait_timeout="30s"
)
```

## Common Queries

```sql
-- Show databases
SHOW DATABASES

-- Describe table
DESCRIBE TABLE catalog.schema.table
DESCRIBE TABLE EXTENDED catalog.schema.table

-- Table history (Delta)
DESCRIBE HISTORY catalog.schema.table

-- Row count
SELECT COUNT(*) FROM catalog.schema.table
```

## Arguments

| Arg | Description |
|-----|-------------|
| `-c, --command` | SQL query string |
| `-f, --file` | SQL file path |
| `-p, --profile` | Databricks profile name |
| `-w, --warehouse` | Warehouse ID (default: first running) |
| `-o, --output` | Format: table, json, csv |
| `-t, --timeout` | Query timeout (default: 30s) |
