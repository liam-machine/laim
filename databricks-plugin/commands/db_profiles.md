---
description: List and test Databricks workspace profiles
argument-hint: "[list|validate|test] [PROFILE]"
---

# Databricks Profiles

Manage and test workspace profiles from `~/.databrickscfg`.

## Quick Reference

| Action | Command |
|--------|---------|
| List profiles | `db_profiles.py list` |
| Validate | `db_profiles.py validate PROFILE` |
| Test connection | `db_profiles.py test PROFILE` |

## Script Usage

```bash
# List all available profiles
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py list

# JSON output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py list -o json

# Validate a profile configuration
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py validate DEV

# Test profile connection
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_profiles.py test DEV
```

## Profile Configuration

Profiles are defined in `~/.databrickscfg`:

```ini
[DEFAULT]
host  = https://dbc-xxx.cloud.databricks.com
token = dapi...

[DEV]
host  = https://dbc-yyy.cloud.databricks.com
token = dapi...

[PROD]
host  = https://dbc-zzz.cloud.databricks.com
token = dapi...
```

## Profile Selection Priority

When no `-p PROFILE` is specified:

1. `DATABRICKS_PROFILE` environment variable
2. Plugin config `default_profile` (in `~/.databricks-plugin/config.yaml`)
3. `DEFAULT` profile (if exists)
4. First available profile

## Setting Default Profile

### Via Environment Variable

```bash
export DATABRICKS_PROFILE=DEV
```

### Via Plugin Config

Create `~/.databricks-plugin/config.yaml`:

```yaml
default_profile: DEV
```

## Creating a Token

1. Go to your Databricks workspace
2. Click your username → Settings → Developer
3. Click "Manage" under "Access tokens"
4. Generate new token
5. Add to `~/.databrickscfg`

## Arguments

| Arg | Description |
|-----|-------------|
| `list` | List all profiles |
| `validate` | Check profile configuration |
| `test` | Test connection to workspace |
| `-o, --output` | Format: table, json |
