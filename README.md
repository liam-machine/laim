# laim

*Liam's **AI** plugins* — Claude Code extensions for data engineering, cloud workflows, and developer productivity.

## Installation

### Step 1: Add the Marketplace

```shell
/plugin marketplace add liam-machine/laim
```

### Step 2: Install a Plugin

**Option A - Browse and install interactively:**
```shell
/plugin
```
Then select "Browse Plugins" and choose the plugin to install.

**Option B - Install directly:**
```shell
/plugin install databricks-executor@liam-machine/laim
```

### Step 3: Choose Installation Scope

When prompted, select a scope:

| Scope | Location | Use Case |
|-------|----------|----------|
| `user` | `~/.claude/settings.json` | Available in all projects |
| `project` | `.claude/settings.json` | Shared with team via git |
| `local` | `.claude/settings.local.json` | Personal, gitignored |

### Step 4: Restart Claude Code

Restart or start a new session to activate the plugin.

## Skills

Skills are auto-triggered based on context - Claude automatically uses them when relevant.

<details>
<summary><strong>databricks-executor</strong> - Execute code on Databricks clusters</summary>

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

</details>

<details>
<summary><strong>teams-message</strong> - Draft Microsoft Teams messages on macOS</summary>

### teams-message

Draft Microsoft Teams messages via AppleScript automation. Messages are drafted for you to review and send manually.

| Feature | Description |
|---------|-------------|
| Platform | macOS only |
| App | Microsoft Teams desktop |
| Mode | Draft only (manual send) |
| Auth | Uses your existing Teams session |

**Quick Start:**

1. Ensure Microsoft Teams is installed and you're signed in
2. Grant Accessibility permissions to Terminal (System Settings > Privacy & Security > Accessibility)
3. Ask Claude to send a message:

```
"Send a Teams message to colleague@company.com saying Hello!"
```

Or run directly:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/teams-message/scripts/teams-message.sh "recipient@email.com" "Your message"
```

See [setup guide](teams-message-plugin/skills/teams-message/references/setup.md) for detailed configuration.

</details>

<details>
<summary><strong>statusline</strong> - Rich status line with usage tracking and git info</summary>

### statusline

Rich Claude Code status line displaying context usage, API rate limits, git info, and visual progress bars.

| Feature | Description |
|---------|-------------|
| Context | Token count with progress bar (e.g., `10%-20K/200K`) |
| Session | 5-hour API rate limit with time remaining |
| Weekly | 7-day rate limit with time remaining |
| Git | Repo, branch, status (`*` unstaged, `+` staged, `↑↓` ahead/behind) |
| Cost | Session cost and duration |

**Example Output:**
```
Opus 4.5 | 💭 █░░░░░░░ 10%-20K/200K | ⏱ █░░░░░░░ 6%-4h42m | 📅 █░░░░░░░ 2%-2d12h | $1.25 | 5m | laim:main[✓] | v2.0.31
```

**Quick Start:**

After installing the plugin, ask Claude to set up the statusline:
```
"Set up the rich statusline for me"
```

Or manually:
```bash
# Copy the script
mkdir -p ~/.claude/scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/statusline.py ~/.claude/scripts/

# Add to ~/.claude/settings.json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/scripts/statusline.py"
  }
}
```

</details>

## Slash Commands

Slash commands are invoked explicitly with `/<command-name>`.

<details>
<summary><strong>repo</strong> - Create and publish repos with <code>/repo</code></summary>

### repo

Quickly create and publish repositories with the `/repo` command. Supports personal and org repositories, GitHub publishing, and virtual environment setup.

| Feature | Description |
|---------|-------------|
| Usage | `/repo <repo-name> [org]` |
| GitHub | Automatic publishing via `gh` CLI |
| Environments | venv, conda, npm |
| Config | `~/.claude/repo-creator-config.json` |

**Quick Start:**
```bash
# Create a personal repo
/repo my-new-project

# Create an org repo
/repo my-project org
```

On first run, you'll be prompted to configure your personal projects directory.

</details>

## License

MIT
