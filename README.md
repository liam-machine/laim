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

## Plugin Structure

```
laim/
├── databricks-plugin/
│   ├── skills/databricks/             # Comprehensive Databricks admin
│   └── commands/                      # /db:* slash commands
│
├── databricks-executor-plugin/
│   └── skills/
│       └── databricks-executor        # Execute code on Databricks clusters
│
├── people-plugin/
│   └── skills/
│       ├── messaging                  # Multi-platform messaging
│       └── github-collaborator        # Add repo collaborators by name
│
├── manim-web-plugin/
│   └── skills/
│       └── manim-web                  # Animated splash screens & web animations
│
├── repo-creator-plugin/
│   └── skills/
│       └── repo                       # Create repos, publish to GitHub
│
├── ssh-pi/
│   └── skills/
│       └── ssh-pi                     # Execute commands on Raspberry Pi via SSH
│
├── next-feature-plugin/
│   └── commands/
│       └── next-feature.md            # /next-feature slash command
│
└── statusline-plugin/
    └── hooks/                         # Rich status line (no skills, hooks only)
```

| Plugin | Skills | Category |
|--------|--------|----------|
| **databricks** | `databricks` + 6 commands | Data Engineering |
| **databricks-executor** | `databricks-executor` | Data Engineering |
| **people** | `messaging`, `github-collaborator` | Productivity |
| **manim-web** | `manim-web` | Creative |
| **repo-creator** | `repo` | Productivity |
| **ssh-pi** | `ssh-pi` | Productivity |
| **next-feature** | `/next-feature` *(command)* | Productivity |
| **statusline** | *(hooks only)* | Productivity |

## Skills

Skills are auto-triggered based on context — Claude automatically uses them when relevant.

<details>
<summary><strong>databricks</strong> - Comprehensive Databricks administration</summary>

### databricks

Full Databricks administration across multiple workspaces: SQL queries, clusters, warehouses, jobs, and more.

| Feature | Description |
|---------|-------------|
| Multi-Workspace | Support for multiple profiles (DEV, PROD, UAT, etc.) |
| SQL Queries | Execute queries via SQL warehouses |
| Clusters | Start, stop, list Spark clusters |
| Warehouses | Manage SQL warehouses |
| Jobs | List, trigger, monitor job runs |
| Profiles | Auto-detect from `~/.databrickscfg` |

**Commands:**
- `/db:query` — Execute SQL queries
- `/db:clusters` — Cluster management
- `/db:warehouses` — Warehouse management
- `/db:jobs` — Job and run management
- `/db:profiles` — List and test profiles
- `/db:setup` — Initial configuration

**Quick Start:**
```bash
# List your profiles
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py list

# Run a query
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_query.py -c "SHOW DATABASES" -p DEV

# List clusters
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py list -p DEV
```

See [configuration guide](databricks-plugin/skills/databricks/references/configuration.md) for setup.

</details>

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
<summary><strong>people</strong> - Person-directed actions (messaging + GitHub collaboration)</summary>

### people

Person-directed actions: send messages across platforms and manage GitHub collaborators. Resolves contact names to platform-specific identifiers.

| Feature | Description |
|---------|-------------|
| Platforms | Teams, WhatsApp, iMessage, Messenger |
| GitHub | Add/remove collaborators by contact name |
| Mode | Draft by default (manual send) |
| Contacts | Name-based lookup with platform routing |
| Inference | Work keywords trigger work platform (Teams) |
| Platform | macOS only |

**Skills included:**
- `messaging` — Multi-platform messaging
- `github-collaborator` — Add repo collaborators by name

**Quick Start:**

1. Ensure platform apps are installed (Teams, WhatsApp, Messages, Messenger)
2. Grant Accessibility permissions to Terminal (System Settings > Privacy & Security > Accessibility)
3. Add contacts to `${CLAUDE_PLUGIN_ROOT}/skills/messaging/references/contacts.yaml`
4. Ask Claude:

```
"Message James about the Databricks pipeline"     # → Teams (work keyword detected)
"Message James about drinks on Friday"            # → Asks which platform
"WhatsApp James: Running 10 minutes late"         # → WhatsApp (explicit)
"Add James as a collaborator to my active repo"   # → GitHub (uses github handle)
```

See [setup guide](people-plugin/skills/messaging/references/setup.md) for platform-specific configuration.

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

<details>
<summary><strong>manim-web</strong> - Animated splash screens and web animations with Manim</summary>

### manim-web

Create professional splash screens, loading animations, and web-ready motion graphics using Manim Community — the animation engine behind 3Blue1Brown's videos.

| Feature | Description |
|---------|-------------|
| Formats | GIF, WebM (transparent), MP4, MOV |
| Quality | 480p to 4K presets |
| Templates | Logo reveals, loaders, UI components |
| Easing | 20+ rate functions (bounce, elastic, back, etc.) |

**Quick Start:**
```bash
# Install Manim
pip install manim

# Create a simple splash screen
cat > splash.py << 'EOF'
from manim import *

class LogoReveal(Scene):
    def construct(self):
        logo = Text("MyApp", font_size=96, gradient=(BLUE, PURPLE))
        self.play(FadeIn(logo, scale=0.8), rate_func=ease_out_back, run_time=1)
        self.wait(0.5)
EOF

# Render with transparency for web
manim -t --format webm -qh splash.py LogoReveal
```

**Using the render helper:**
```bash
# Use presets for common use cases
python3 ${CLAUDE_PLUGIN_ROOT}/skills/manim-web/scripts/render_web.py splash.py LogoReveal --preset splash

# List available presets
python3 ${CLAUDE_PLUGIN_ROOT}/skills/manim-web/scripts/render_web.py --list-presets
```

**Templates included:**
- `splash_screens.py` — Logo reveals, particle entries, morphing shapes
- `web_components.py` — Buttons, cards, loaders, notifications

See [animation reference](manim-web-plugin/skills/manim-web/references/animations.md) and [easing reference](manim-web-plugin/skills/manim-web/references/easing.md) for full documentation.

</details>

<details>
<summary><strong>repo-creator</strong> - Create repositories and publish to GitHub</summary>

### repo-creator

Create repositories with a guided workflow: initialize git, publish to GitHub (personal or organization), and set up virtual environments.

| Feature | Description |
|---------|-------------|
| Targets | Personal repos, organization repos |
| Publishing | GitHub CLI (`gh`) integration |
| Environments | venv, conda, npm |
| Config | Persistent path preferences |

**Quick Start:**

```bash
# Personal repository
/repo my-new-project

# Organization repository
/repo my-org-project org
```

**Workflow:**
1. Checks/creates config for default paths
2. Verifies GitHub CLI is installed and authenticated
3. Creates local repo with `git init`
4. Publishes to GitHub (private/public choice)
5. Optionally sets up venv, conda, or npm
6. Activates environment and confirms setup

**Configuration:**

The skill stores preferences in `~/.claude/repo-creator-config.json`:
- `personalReposPath` - Default directory for personal repos
- `configuredPaths` - Saved paths for quick selection

See [configuration guide](repo-creator-plugin/skills/repo-creator/references/configuration.md) for details.

</details>

<details>
<summary><strong>ssh-pi</strong> - Execute commands on Raspberry Pi via SSH</summary>

### ssh-pi

Execute commands, run scripts, and manage files on a Raspberry Pi via SSH for local Mac + remote Pi development workflows.

| Feature | Description |
|---------|-------------|
| Commands | Execute shell commands via `ssh pi "command"` |
| Scripts | Run local bash/python scripts on Pi |
| Sync | rsync directories with common excludes |
| Helper | Bundled `pi-exec.sh` for info, logs, temp |

**Quick Start:**

1. Configure SSH alias in `~/.ssh/config`:
```
Host pi
    HostName raspberrypi.local
    User pi
```

2. Ask Claude:
```
"Run htop on the pi"
"Sync this project to /home/pi/project"
"Check the pi's temperature"
"Deploy this script to the raspberry pi and run it"
```

**Common Operations:**
```bash
# Execute command
ssh pi "python3 --version"

# Sync project
rsync -avz ./project/ pi:/home/pi/project/

# System info
${CLAUDE_PLUGIN_ROOT}/skills/ssh-pi/scripts/pi-exec.sh info
```

See [configuration guide](ssh-pi/skills/ssh-pi/references/configuration.md) for SSH setup.

</details>

<details>
<summary><strong>next-feature</strong> - Implement the next feature from features.json</summary>

### next-feature

Slash command that reads features.json and implements the next feature using the feature-dev agent, with Chrome browser automation and automatic commits.

| Feature | Description |
|---------|-------------|
| Input | Reads `features.json` from project root |
| Agent | Uses feature-dev agent for implementation |
| Browser | Chrome automation when needed |
| Commit | Auto-commits after validation |

**Quick Start:**
```bash
/next-feature
```

**Requirements:**
- A `features.json` file in your project with feature definitions
- The feature-dev plugin installed for guided implementation

</details>

## License

MIT
