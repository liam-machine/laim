---
description: Execute code on Databricks Spark clusters (Python, SQL, Scala, R)
argument-hint: "<code> [-l LANGUAGE] [-p PROFILE] [--cluster CLUSTER_ID]"
---

# Databricks Execute

Execute arbitrary code on Databricks Spark clusters using the Execution Context API.

## Quick Reference

| Action | Command |
|--------|---------|
| Run Python | `db_execute.py -c "print(spark.version)" -p PROFILE` |
| Run SQL | `db_execute.py -l sql -c "SHOW DATABASES" -p PROFILE` |
| Run Scala | `db_execute.py -l scala -c "println(spark.version)" -p PROFILE` |
| Run R | `db_execute.py -l r -c "print(sparkR.version())" -p PROFILE` |
| Run file | `db_execute.py -f script.py -p PROFILE` |
| REPL mode | `db_execute.py --repl -p PROFILE` |
| Check cluster | `db_execute.py --check-cluster -p PROFILE` |

## Script Usage

```bash
# Python (default language)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -c "print(spark.version)" -p DEV

# SQL query
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -l sql -c "SHOW DATABASES" -p DEV

# Scala code
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -l scala -c "println(spark.version)" -p DEV

# Execute a file
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -f etl_script.py -p DEV

# Interactive REPL session
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py --repl -p DEV

# JSON output for tabular results
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -l sql -c "SELECT * FROM table" -p DEV -o json

# CSV output for exports
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -l sql -c "SELECT * FROM table" -p DEV -o csv > output.csv
```

## REPL Mode

The REPL (Read-Eval-Print Loop) provides an interactive session with persistent state:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py --repl -p DEV

# Session output:
Databricks Execution Context REPL
Language: python | Cluster: abc123-xyz
Type 'exit' or 'quit' to end session. Multi-line: end with blank line.

[python]>>> df = spark.table("catalog.schema.table")
Executing... Done.
(No output)

[python]>>> df.count()
Executing... Done.
1234567

[python]>>> exit
Exiting...
```

**REPL Features:**
- State preserved across commands (variables persist)
- Multi-line support (end with blank line to execute)
- Exit with `exit` or `quit`
- Interrupt with Ctrl+C

## vs /db:query

| Feature | /db:execute | /db:query |
|---------|-------------|-----------|
| Target | Spark clusters | SQL warehouses |
| Languages | Python, SQL, Scala, R | SQL only |
| State | Persistent context | Stateless |
| REPL | Yes | No |
| Use case | Code execution, exploration | Ad-hoc queries |

Use `/db:execute` for:
- Running PySpark/Scala/R code
- Interactive data exploration
- Testing scripts on clusters
- Complex multi-step operations

Use `/db:query` for:
- Simple SQL queries
- Production analytics
- Queries requiring SQL warehouse features

## Configuration

The script uses `~/.databrickscfg` profiles. Ensure your profile has `cluster_id`:

```ini
[DEV]
host = https://dbc-xxx.cloud.databricks.com
token = dapi...
cluster_id = 0123-456789-abc123
```

Override with CLI arguments:
```bash
db_execute.py -c "print(1)" --host "https://..." --token "dapi..." --cluster-id "abc123"
```

## Arguments

| Arg | Description |
|-----|-------------|
| `-c, --command` | Code to execute |
| `-f, --file` | File to execute |
| `--repl` | Start interactive REPL |
| `-l, --language` | python, sql, scala, r (default: python) |
| `-p, --profile` | Databricks profile |
| `--cluster-id` | Override cluster ID |
| `-o, --output` | Format: text, json, csv |
| `-v, --verbose` | Show debug output |
| `--check-cluster` | Check cluster state |
| `--poll-interval` | Polling interval in seconds |
