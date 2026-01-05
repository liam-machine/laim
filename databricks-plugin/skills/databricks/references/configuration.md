# Databricks Plugin Configuration

Complete guide to configuring the Databricks plugin for Claude Code.

## Overview

The plugin uses a layered configuration system:

1. **~/.databrickscfg** - Workspace profiles (host, token)
2. **~/.databricks-plugin/config.yaml** - Plugin preferences (optional)
3. **Environment variables** - Runtime overrides
4. **Command arguments** - Per-command overrides

## Profile Configuration

### ~/.databrickscfg

The primary configuration file. Standard INI format:

```ini
[DEFAULT]
host  = https://dbc-xxx.cloud.databricks.com
token = dapi...

[DEV]
host  = https://dbc-yyy.cloud.databricks.com
token = dapi...
cluster_id = 1234-567890-abc123  # Optional default cluster

[PROD]
host  = https://dbc-zzz.cloud.databricks.com
token = dapi...

[UAT]
host  = https://dbc-aaa.cloud.databricks.com
token = dapi...
```

### Profile Options

| Option | Required | Description |
|--------|----------|-------------|
| `host` | Yes | Workspace URL |
| `token` | Yes | Personal Access Token |
| `cluster_id` | No | Default cluster for execution |
| `warehouse_id` | No | Default SQL warehouse |

## Plugin Configuration (Optional)

### ~/.databricks-plugin/config.yaml

```yaml
# Default profile when none specified
default_profile: DEV

# Default output format
output_format: table  # table, json, csv

# Preferences
preferences:
  timezone: Australia/Brisbane
  confirm_destructive: true
  auto_start_warehouse: false
```

## Environment Variables

Override configuration at runtime:

| Variable | Description |
|----------|-------------|
| `DATABRICKS_PROFILE` | Profile to use |
| `DATABRICKS_HOST` | Workspace URL (overrides profile) |
| `DATABRICKS_TOKEN` | Token (overrides profile) |
| `DATABRICKS_CLUSTER_ID` | Default cluster |
| `DATABRICKS_WAREHOUSE_ID` | Default warehouse |

## Profile Selection Priority

When determining which profile to use:

1. **Explicit argument** - `-p PROFILE` or `--profile PROFILE`
2. **Environment variable** - `DATABRICKS_PROFILE`
3. **Plugin config** - `default_profile` in config.yaml
4. **DEFAULT section** - If exists in ~/.databrickscfg
5. **First profile** - First available profile

## Authentication Methods

### Personal Access Token (PAT) - Recommended

1. Go to Databricks workspace
2. Click username → Settings → Developer
3. Access tokens → Generate new token
4. Add to ~/.databrickscfg

**Pros:**
- Simple setup
- Works everywhere
- No browser interaction

**Cons:**
- Token can expire
- Manual rotation

### OAuth (Browser-based)

```bash
databricks auth login --host https://workspace.cloud.databricks.com
```

**Pros:**
- No token management
- MFA support

**Cons:**
- Requires browser
- May expire frequently with strict IdP settings

### Service Principal (M2M)

For automation and CI/CD:

```ini
[SERVICE]
host = https://workspace.cloud.databricks.com
client_id = your-client-id
client_secret = your-client-secret
```

## Multiple Workspaces

### Recommended Naming Convention

Use environment-based names:

```ini
[DEV]
host = https://dev-workspace.cloud.databricks.com
token = dapi...

[UAT]
host = https://uat-workspace.cloud.databricks.com
token = dapi...

[PROD]
host = https://prod-workspace.cloud.databricks.com
token = dapi...
```

### Cross-Workspace Operations

Specify profile for each operation:

```bash
# Query DEV
db_query.py -c "SELECT * FROM table" -p DEV

# Query PROD
db_query.py -c "SELECT * FROM table" -p PROD
```

## Security Best Practices

### File Permissions

```bash
chmod 600 ~/.databrickscfg
chmod 700 ~/.databricks-plugin
```

### Token Management

1. **Use minimal permissions** - Create tokens with only required access
2. **Set expiry** - Don't use non-expiring tokens in production
3. **Rotate regularly** - Refresh tokens periodically
4. **Never commit** - Add to .gitignore

### Separate Tokens per Environment

Use different tokens for DEV and PROD to limit blast radius.

## Troubleshooting

### "Profile not found"

```bash
# List available profiles
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py list
```

### "Invalid token"

1. Check token hasn't expired
2. Verify token has required permissions
3. Generate new token if needed

### "Connection refused"

1. Verify host URL is correct
2. Check network connectivity
3. Verify workspace is accessible

### "Permission denied"

1. Token may lack required permissions
2. Check workspace ACLs
3. Verify user has access to the resource
