---
name: databricks-executor
description: Execute arbitrary Python, SQL, Scala, or R code on Databricks clusters via the Execution Context API. Use when the user asks to run code on Databricks, execute Spark queries, test scripts on a cluster, interact with a Databricks workspace programmatically, or needs a REPL session with Databricks. Triggers include "run on Databricks", "execute on cluster", "Spark query", "test this on Databricks", "databricks REPL", "run PySpark", or any request to execute code remotely on a Databricks environment.
---

# Databricks Executor

Execute arbitrary code on Databricks clusters using the Execution Context API (1.2).

## Quick Start

### Prerequisites

User must have configured Databricks credentials. Check for configuration:

```bash
# Check for config file
cat ~/.databrickscfg 2>/dev/null || echo "No config file"

# Check for environment variables
echo "HOST: ${DATABRICKS_HOST:-not set}"
echo "TOKEN: ${DATABRICKS_TOKEN:-not set}"
echo "CLUSTER: ${DATABRICKS_CLUSTER_ID:-not set}"
```

If not configured, see [references/configuration.md](references/configuration.md) for setup instructions.

### Execute Code

The execution script is located at: `${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py`

```bash
# Python (default)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -c "print(spark.version)"

# SQL query
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language sql -c "SHOW DATABASES"

# Scala
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language scala -c "println(spark.version)"

# Execute a file
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -f /path/to/script.py

# Interactive REPL
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --repl
```

## Workflow Decision Tree

```
User wants to execute code on Databricks
├── Single command? → Use -c flag
│   └── python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -c "<code>"
├── Script file? → Use -f flag
│   └── python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -f script.py
├── Interactive session? → Use --repl
│   └── python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --repl
└── Check cluster first? → Use --check-cluster
    └── python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --check-cluster
```

## Common Patterns

### Run Spark SQL Queries

```bash
# List databases
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language sql -c "SHOW DATABASES"

# Query data
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language sql -c "SELECT * FROM catalog.schema.table LIMIT 10"

# Get CSV output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language sql --output-format csv -c "SELECT * FROM table"
```

### Run PySpark Code

```bash
# DataFrame operations
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -c "spark.sql('SELECT 1 as col').show()"

# Read data
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -c "df = spark.table('catalog.schema.table'); print(df.count())"

# Complex script
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -f etl_script.py
```

### Use Different Profiles/Clusters

```bash
# Use named profile
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --profile PROD -c "print(1)"

# Override cluster
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --cluster-id "new-cluster-id" -c "print(1)"

# Full override
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py \
  --host "https://workspace.azuredatabricks.net" \
  --token "dapi-xxx" \
  --cluster-id "cluster-id" \
  -c "print(1)"
```

### Output Formats

```bash
# Default text output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language sql -c "SELECT * FROM table"

# JSON output (for programmatic use)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language sql --output-format json -c "SELECT * FROM table"

# CSV output (for exports)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language sql --output-format csv -c "SELECT * FROM table" > output.csv
```

## Error Handling

The script returns exit codes:
- `0` - Success
- `1` - Error (configuration, connection, or execution error)

Errors include:
- Configuration errors (missing host/token/cluster)
- Connection errors (network issues)
- Execution errors (code errors, displayed with traceback)

## Resources

- **scripts/databricks_exec.py** - Main execution script (run directly)
- **references/configuration.md** - Authentication and configuration guide
- **references/api-reference.md** - Databricks API details

## User Setup Requirements

Before using this skill, ensure the user has:

1. **Databricks workspace access** - URL like `https://adb-xxx.azuredatabricks.net`
2. **Personal access token** - Generated from workspace Settings → Developer → Access tokens
3. **Running cluster** - With appropriate permissions
4. **Configuration** - Via `~/.databrickscfg`, environment variables, or CLI args

Prompt user to configure if missing:

```
To use Databricks execution, you need:
1. Your Databricks workspace URL (e.g., https://adb-xxx.azuredatabricks.net)
2. A personal access token (generate in Settings → Developer → Access tokens)
3. A cluster ID (find in Compute → your cluster → URL)

Would you like me to help you set up ~/.databrickscfg?
```
