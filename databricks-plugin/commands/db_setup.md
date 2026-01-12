---
description: Configure Databricks workspaces for first-time setup
argument-hint: ""
---

# Databricks Setup

Interactive setup guide for configuring Databricks workspaces.

## Prerequisites

1. **Databricks CLI** - Install with:
   ```bash
   pip install databricks-cli
   # or
   brew install databricks
   ```

2. **Databricks SDK** - Install with:
   ```bash
   pip install databricks-sdk
   ```

3. **Workspace Access** - You need access to at least one Databricks workspace

## Setup Steps

### 1. Create Personal Access Token (PAT)

For each workspace:

1. Log into your Databricks workspace
2. Click your username (top right) → **Settings**
3. Go to **Developer** → **Access tokens**
4. Click **Generate new token**
5. Give it a name (e.g., "Claude Code") and optional expiry
6. **Copy the token immediately** - you won't see it again

### 2. Configure Profile

Add to `~/.databrickscfg`:

```ini
[PROFILE_NAME]
host  = https://your-workspace.cloud.databricks.com
token = dapi-your-token-here
```

Example with multiple workspaces:

```ini
[DEFAULT]
host  = https://dbc-xxx.cloud.databricks.com
token = dapiXXX

[DEV]
host  = https://dbc-yyy.cloud.databricks.com
token = dapiYYY

[PROD]
host  = https://dbc-zzz.cloud.databricks.com
token = dapiZZZ
```

### 3. Test Configuration

```bash
# List profiles
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py list

# Test a specific profile
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py test DEV
```

### 4. Set Default Profile (Optional)

Create `~/.databricks-plugin/config.yaml`:

```yaml
default_profile: DEV
```

Or set environment variable:

```bash
export DATABRICKS_PROFILE=DEV
```

## Verification

After setup, verify everything works:

```bash
# List clusters
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_clusters.py list -p DEV

# List warehouses
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_warehouses.py list -p DEV

# Run a simple query
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_query.py -c "SELECT 1" -p DEV
```

## Troubleshooting

### "No profiles found"

Check that `~/.databrickscfg` exists and has the correct format:
- Section names in `[brackets]`
- `host` and `token` on separate lines
- No quotes around values

### "Connection failed"

1. Verify the host URL is correct
2. Check the token hasn't expired
3. Ensure you have network access to the workspace

### "Invalid token"

1. Generate a new token in the workspace
2. Update `~/.databrickscfg`
3. Test again with `db_profiles.py test PROFILE`

## Security Notes

- **Never commit tokens** - Keep `~/.databrickscfg` secure
- **Use minimal permissions** - Create tokens with only needed access
- **Rotate regularly** - Consider refreshing tokens periodically
- **File permissions** - Ensure `~/.databrickscfg` is readable only by you:
  ```bash
  chmod 600 ~/.databrickscfg
  ```
