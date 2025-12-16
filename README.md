# laim

A collection of Claude Code plugins for data engineering and cloud workflows.

## Plugins

### databricks-executor

Execute arbitrary Python, SQL, Scala, or R code on Databricks clusters via the Execution Context API.

**Features:**
- Multiple auth methods: CLI args, environment variables, `~/.databrickscfg` profiles
- Support for Python, SQL, Scala, and R languages
- Output formats: text, JSON, CSV
- Interactive REPL mode
- Cluster state checking

**Usage:**
```bash
# Execute Python
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -c "print(spark.version)"

# Execute SQL
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --language sql -c "SHOW DATABASES"

# Interactive REPL
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py --repl
```

**Prerequisites:**
- Databricks workspace URL
- Personal access token (Settings → Developer → Access tokens)
- Running cluster ID

Configure via environment variables:
```bash
export DATABRICKS_HOST="https://adb-xxx.azuredatabricks.net"
export DATABRICKS_TOKEN="dapi-xxx"
export DATABRICKS_CLUSTER_ID="cluster-id"
```

Or create `~/.databrickscfg`:
```ini
[DEFAULT]
host = https://adb-xxx.azuredatabricks.net
token = dapi-xxx
cluster_id = cluster-id
```

---

## Installation

### Option 1: Symlink (Development)

```bash
ln -s /path/to/laim/databricks-executor-plugin ~/.claude/plugins/databricks-executor
```

### Option 2: Copy to plugins directory

```bash
cp -r /path/to/laim/databricks-executor-plugin ~/.claude/plugins/databricks-executor
```

### Option 3: Add to Claude Code settings

Edit `~/.claude/settings.json`:
```json
{
  "plugins": [
    "/path/to/laim/databricks-executor-plugin"
  ]
}
```

After installation, restart Claude Code or start a new session.

## License

MIT
