# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository contains Claude Code plugins - modular extensions that add specialized capabilities to Claude Code. See README.md for the list of available plugins and installation instructions.

## Architecture

### Plugin Structure

Plugins follow the Claude Code plugin convention:

```
<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, description)
└── skills/
    └── <skill-name>/
        ├── SKILL.md         # Skill instructions and triggers
        ├── scripts/         # Executable scripts
        └── references/      # Documentation loaded on-demand
```

### Key Concepts

- **Skills** are auto-triggered based on their `description` field in SKILL.md frontmatter
- **`${CLAUDE_PLUGIN_ROOT}`** must be used for all intra-plugin path references (ensures portability)
- **References** are loaded into context only when needed (progressive disclosure)
- **Scripts** can be executed directly without loading into context

## Testing Plugins

Test the databricks-executor script:
```bash
python3 databricks-executor-plugin/skills/databricks-executor/scripts/databricks_exec.py --help
```

## Plugin Installation

To install a plugin locally for testing:
```bash
ln -s /path/to/laim/<plugin-name> ~/.claude/plugins/<plugin-name>
```

## IMPORTANT: Updating README.md

**When creating a new plugin in this repository, you MUST update README.md** to include the new plugin in the "Plugins" section.

Add a new subsection following this format:

```markdown
### <plugin-name>

<Short description of what the plugin does>

**Features:**
- Feature 1
- Feature 2

**Usage:**
\`\`\`bash
# Example command 1
python3 ${CLAUDE_PLUGIN_ROOT}/skills/<skill-name>/scripts/<script>.py -c "example"

# Example command 2
python3 ${CLAUDE_PLUGIN_ROOT}/skills/<skill-name>/scripts/<script>.py --help
\`\`\`

**Prerequisites:**
- List any required setup (credentials, config files, etc.)

---
```

Also update the Installation section if the new plugin requires any special installation steps.
