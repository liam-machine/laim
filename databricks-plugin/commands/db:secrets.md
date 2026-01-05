---
description: Manage Databricks secret scopes and secrets
argument-hint: "[list-scopes|create-scope|list|put|delete|acls] [SCOPE] [KEY]"
---

# Databricks Secrets

Manage secret scopes and secrets for secure credential storage.

## Quick Reference

| Action | Command |
|--------|---------|
| List scopes | `db_secrets.py list-scopes -p PROFILE` |
| Create scope | `db_secrets.py create-scope NAME -p PROFILE` |
| Delete scope | `db_secrets.py delete-scope NAME -p PROFILE` |
| List secrets | `db_secrets.py list SCOPE -p PROFILE` |
| Put secret | `db_secrets.py put SCOPE KEY --value VALUE -p PROFILE` |
| Delete secret | `db_secrets.py delete SCOPE KEY -p PROFILE` |
| View ACLs | `db_secrets.py acls SCOPE -p PROFILE` |

## Script Usage

```bash
# List all secret scopes
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_secrets.py list-scopes -p DEV

# Create a new scope
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_secrets.py create-scope my-app-secrets -p DEV

# Add a secret (value from argument)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_secrets.py put my-app-secrets api-key --value "sk-xxx" -p DEV

# Add a secret (value from interactive prompt)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_secrets.py put my-app-secrets db-password -p DEV

# List secrets in a scope (shows keys only, not values)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_secrets.py list my-app-secrets -p DEV

# Delete a secret
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_secrets.py delete my-app-secrets api-key -p DEV

# Delete entire scope
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_secrets.py delete-scope my-app-secrets -p DEV

# View scope permissions
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_secrets.py acls my-app-secrets -p DEV
```

## Using Secrets in Notebooks

```python
# Access secrets in notebooks/jobs
api_key = dbutils.secrets.get(scope="my-app-secrets", key="api-key")
db_password = dbutils.secrets.get(scope="my-app-secrets", key="db-password")
```

## CLI Fallback

```bash
# List scopes
databricks secrets list-scopes -p DEV

# Create scope
databricks secrets create-scope my-scope -p DEV

# Put secret
databricks secrets put-secret my-scope my-key --string-value "secret" -p DEV

# List secrets
databricks secrets list-secrets my-scope -p DEV

# Delete secret
databricks secrets delete-secret my-scope my-key -p DEV
```

## Security Notes

- Secret values are **never retrievable** via API (write-only)
- Values are encrypted at rest
- Access controlled via scope ACLs
- Use service principals for production workloads
- Never hardcode secrets in notebooks

## Arguments

| Arg | Description |
|-----|-------------|
| `list-scopes` | List all secret scopes |
| `create-scope` | Create a new scope |
| `delete-scope` | Delete a scope (and all secrets) |
| `list` | List secrets in a scope (keys only) |
| `put` | Add/update a secret |
| `delete` | Delete a secret |
| `acls` | List scope ACLs |
| `-p, --profile` | Databricks profile |
| `-o, --output` | Format: table, json, csv |
