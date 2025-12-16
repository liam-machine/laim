# laim

A collection of Claude Code plugins for data engineering and cloud workflows.

## Installation

### Option 1: Symlink (Recommended for Development)

```bash
ln -s /path/to/laim/<plugin-name> ~/.claude/plugins/<plugin-name>
```

### Option 2: Copy to plugins directory

```bash
cp -r /path/to/laim/<plugin-name> ~/.claude/plugins/<plugin-name>
```

### Option 3: Add to Claude Code settings

Edit `~/.claude/settings.json`:
```json
{
  "plugins": [
    "/path/to/laim/<plugin-name>"
  ]
}
```

After installation, restart Claude Code or start a new session.

## Plugins

### databricks-executor

Execute Python, SQL, Scala, or R code on Databricks clusters via the Execution Context API.

| Feature | Description |
|---------|-------------|
| Languages | Python, SQL, Scala, R |
| Auth | CLI args, env vars, `~/.databrickscfg` |
| Output | text, JSON, CSV |
| Modes | Single command, file execution, REPL |

**Quick Start:**
```bash
# Set credentials
export DATABRICKS_HOST="https://adb-xxx.azuredatabricks.net"
export DATABRICKS_TOKEN="dapi-xxx"
export DATABRICKS_CLUSTER_ID="cluster-id"

# Execute code
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks-executor/scripts/databricks_exec.py -c "print(spark.version)"
```

See [configuration guide](databricks-executor-plugin/skills/databricks-executor/references/configuration.md) for detailed setup.

---

## License

MIT
