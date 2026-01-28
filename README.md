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
│   ├── skills/databricks/             # Comprehensive Databricks admin (13 commands)
│   └── commands/                      # /db:* slash commands
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
├── plan-converter-plugin/
│   └── skills/
│       ├── plan-converter                    # Convert plan.md → features.json
│       └── create-next-feature-skill-local   # Scaffold /next-feature locally
│
├── powerbi-local/
│   └── skills/
│       ├── pbi-dev/                   # Power BI development (TMDL, PBIR, DAX)
│       └── pbi-test/                  # Feature testing and verification
│
└── statusline-plugin/
    └── hooks/                         # Rich status line (no skills, hooks only)
```

| Plugin | Skills | Category |
|--------|--------|----------|
| **databricks** | `databricks` + 13 commands | Data Engineering |
| **powerbi-local** | `pbi-dev`, `pbi-test` | Data Engineering |
| **people** | `messaging`, `github-collaborator` | Productivity |
| **manim-web** | `manim-web` | Creative |
| **repo-creator** | `repo` | Productivity |
| **ssh-pi** | `ssh-pi` | Productivity |
| **next-feature** | `/next-feature` *(command)* | Productivity |
| **plan-converter** | `plan-converter`, `create-next-feature-skill-local` | Productivity |
| **statusline** | *(hooks only)* | Productivity |

## Skills

Skills are auto-triggered based on context — Claude automatically uses them when relevant.

<details>
<summary><strong>databricks</strong> - Comprehensive Databricks administration</summary>

### databricks

Full Databricks administration across multiple workspaces: SQL queries, code execution, clusters, warehouses, jobs, secrets, Unity Catalog, pipelines, dashboards, permissions, and deployments.

| Feature | Description |
|---------|-------------|
| Multi-Workspace | Support for multiple profiles (DEV, PROD, UAT, etc.) |
| SQL Queries | Execute queries via SQL warehouses |
| Code Execution | Python, SQL, Scala, R on Spark clusters (REPL supported) |
| Clusters | Start, stop, list Spark clusters |
| Warehouses | Manage SQL warehouses |
| Jobs | List, trigger, monitor job runs |
| Secrets | Secret scopes and values |
| Unity Catalog | Catalogs, schemas, tables, volumes, grants |
| Pipelines | Delta Live Tables / Lakeflow management |
| Dashboards | Lakeview dashboard management |
| Permissions | Object-level ACLs and grants |
| Deployment | DAB bundle validate, deploy, destroy |

**Commands:**
- `/db:query` — Execute SQL queries on warehouses
- `/db:execute` — Execute code on Spark clusters (Python, SQL, Scala, R)
- `/db:clusters` — Cluster management
- `/db:warehouses` — Warehouse management
- `/db:jobs` — Job and run management
- `/db:secrets` — Secret scope management
- `/db:catalog` — Unity Catalog operations
- `/db:pipelines` — DLT/Lakeflow pipeline management
- `/db:lakeview` — Lakeview dashboard management
- `/db:permissions` — Object-level permissions
- `/db:deploy` — DAB bundle deployments
- `/db:profiles` — List and test profiles
- `/db:setup` — Initial configuration

**Quick Start:**
```bash
# List your profiles
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py list

# Run SQL on warehouse
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_query.py -c "SHOW DATABASES" -p DEV

# Run Python on Spark cluster
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py -c "print(spark.version)" -p DEV

# Interactive REPL
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_execute.py --repl -p DEV

# List Unity Catalog tables
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py tables main.default -p DEV
```

See [configuration guide](databricks-plugin/skills/databricks/references/configuration.md) for setup.

</details>

<details>
<summary><strong>powerbi-local</strong> - Power BI development with Microsoft MCP and Claude computer use</summary>

### powerbi-local

Local Power BI development using Microsoft's official MCP server and Claude's computer use capabilities. Edit semantic models (TMDL), create reports (PBIR), execute DAX queries, and verify features visually.

| Feature | Description |
|---------|-------------|
| Semantic Model | Edit tables, measures, columns, relationships via TMDL |
| Reports | Create/edit visuals, pages via PBIR JSON with templates |
| DAX Queries | Execute queries via MCP, test measures |
| Computer Use | Screenshot reports, click slicers, verify visuals |
| Testing | Automated verification of measures, relationships, visuals |

**Skills included:**
- `pbi-dev` — Power BI development (TMDL, PBIR, DAX patterns)
- `pbi-test` — Feature testing and verification

**Commands:**
- `/pbi` — Power BI development assistance
- `/pbi-test` — Test and verify Power BI features

**Quick Start:**

1. Install the Power BI MCP server:
```bash
npm install -g @microsoft/powerbi-modeling-mcp
```

2. Configure MCP in `.mcp.json`:
```json
{
  "mcpServers": {
    "powerbi": {
      "command": "npx",
      "args": ["-y", "@microsoft/powerbi-modeling-mcp@latest"]
    }
  }
}
```

3. Enable PBIP format in Power BI Desktop:
   - File → Options → Preview Features
   - Enable "Power BI Project (.pbip) save option"
   - Enable "Store semantic model in TMDL format"

4. Ask Claude:
```
"Add a YoY Growth measure to the Sales table"
"Create a bar chart showing sales by region"
"Test if my new measure works correctly"
"Add a relationship between Products and Sales"
```

**Requirements:**
- Windows 10/11 (Power BI Desktop is Windows-only)
- Power BI Desktop (non-Store version recommended)
- Node.js 18+
- Claude Code with computer use enabled

See [architecture documentation](docs/powerbi-plugin-v2.md) for details.

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
<summary><strong>plan-converter</strong> - Convert plan.md to features.json and scaffold /next-feature locally</summary>

### plan-converter

End-to-end feature development pipeline: convert plan.md into features.json, then scaffold a `/next-feature` command in the project repo.

| Feature | Description |
|---------|-------------|
| Plan Conversion | Parse plan.md into features.json with phases, IDs, validation criteria |
| Platform Detection | Auto-detects iOS/Android/Web from tech stack for validation |
| Phase-Based IDs | 100-based spacing (Phase 1: F100–F199) for easy insertion |
| Local Scaffolding | Creates `/next-feature` command in project's `.claude/commands/` |
| Progress Tracking | Completion percentage overall and by phase after each feature |

**Skills:**
- `plan-converter` — Convert plan.md to features.json
- `create-next-feature-skill-local` — Scaffold `/next-feature` command in the project repo

**Quick Start:**
```
# 1. Convert your plan
"Convert plan.md to features.json"

# 2. Scaffold the /next-feature command locally
"Create the next-feature command for this project"

# 3. Implement features one by one
/next-feature

# 4. Jump to a specific feature
/next-feature F102
```

See [schema reference](plan-converter-plugin/skills/plan-converter/references/schema.md) for the complete features.json structure.

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

## Documentation

- **[Power BI Local Development](docs/powerbi-plugin-v2.md)** - Architecture for local Power BI development with Claude Code using Microsoft MCP and computer use

## License

MIT
