# Configuration

The repo-creator skill stores its configuration in `~/.claude/repo-creator-config.json`.

## Configuration File

```json
{
  "personalReposPath": "/Users/username/GIT",
  "configuredPaths": [
    "/Users/username/GIT",
    "/Users/username/work/projects",
    "/Users/username/sandbox"
  ]
}
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `personalReposPath` | string | Default directory for personal repositories |
| `configuredPaths` | string[] | List of known project directories (used for org repo path selection) |

## How It Works

### Personal Repositories

When creating a personal repository (no `org` flag):
1. The repository is created at `<personalReposPath>/<repo-name>`
2. No path selection is prompted

### Organization Repositories

When creating an organization repository (`/repo myrepo org`):
1. You are prompted to select from `configuredPaths`
2. You can also provide a custom path via "Other"
3. New paths are automatically added to `configuredPaths` for future use

## Initial Setup

On first run, the skill will ask for your personal projects directory. This creates the initial config file:

```json
{
  "personalReposPath": "/path/you/provided",
  "configuredPaths": ["/path/you/provided"]
}
```

## Manual Configuration

You can manually edit `~/.claude/repo-creator-config.json` to:

- Add frequently-used project directories to `configuredPaths`
- Change your default `personalReposPath`
- Pre-configure paths for different project types

### Example: Multiple Project Types

```json
{
  "personalReposPath": "/Users/liam/GIT/personal",
  "configuredPaths": [
    "/Users/liam/GIT/personal",
    "/Users/liam/GIT/work",
    "/Users/liam/GIT/experiments",
    "/Users/liam/GIT/clients"
  ]
}
```

## Troubleshooting

### Config file not found

The config is created automatically on first `/repo` invocation. If issues persist:

```bash
mkdir -p ~/.claude
echo '{"personalReposPath": "/your/path", "configuredPaths": ["/your/path"]}' > ~/.claude/repo-creator-config.json
```

### Path permissions

Ensure you have write permissions to:
- `~/.claude/` (for config storage)
- Paths in `configuredPaths` (for repository creation)
