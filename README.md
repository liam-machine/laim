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
<summary><strong>messaging</strong> - Multi-platform messaging (Teams, WhatsApp, iMessage, Messenger)</summary>

### messaging

Send messages across multiple platforms from Claude Code. Supports contact lookup by name with intelligent platform selection based on message content.

| Feature | Description |
|---------|-------------|
| Platforms | Teams, WhatsApp, iMessage, Messenger |
| Mode | Draft by default (manual send) |
| Contacts | Name-based lookup with platform routing |
| Inference | Work keywords trigger work platform (Teams) |
| Platform | macOS only |

**Quick Start:**

1. Ensure platform apps are installed (Teams, WhatsApp, Messages, Messenger)
2. Grant Accessibility permissions to Terminal (System Settings > Privacy & Security > Accessibility)
3. Add contacts to `${CLAUDE_PLUGIN_ROOT}/skills/messaging/references/contacts.yaml`
4. Ask Claude to send a message:

```
"Message James about the Databricks pipeline"     # → Teams (work keyword detected)
"Message James about drinks on Friday"            # → Asks which platform
"WhatsApp James: Running 10 minutes late"         # → WhatsApp (explicit)
```

Or run directly:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/message.sh \
  --platform teams \
  --recipient "jdowzard@jhg.com.au" \
  --message "Your message"
```

See [setup guide](messaging-plugin/skills/messaging/references/setup.md) for platform-specific configuration.

</details>

<details>
<summary><strong>teams-message</strong> - Draft Microsoft Teams messages on macOS (deprecated)</summary>

### teams-message

> **Note:** This plugin has been superseded by the `messaging` plugin which supports multiple platforms.

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

## License

MIT
