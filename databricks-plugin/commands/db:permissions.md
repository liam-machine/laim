---
description: Manage object-level permissions and ACLs
argument-hint: "[get|update|levels] OBJECT_TYPE [OBJECT_ID]"
---

# Databricks Permissions

Manage object-level permissions and access control lists (ACLs).

## Quick Reference

| Action | Command |
|--------|---------|
| Get permissions | `db_permissions.py get OBJECT_TYPE OBJECT_ID -p PROFILE` |
| Update permissions | `db_permissions.py update OBJECT_TYPE OBJECT_ID --principal USER --level LEVEL -p PROFILE` |
| List levels | `db_permissions.py levels OBJECT_TYPE -p PROFILE` |

## Object Types

| Type | Description |
|------|-------------|
| `clusters` | Spark clusters |
| `cluster-policies` | Cluster policies |
| `directories` | Workspace directories |
| `experiments` | MLflow experiments |
| `jobs` | Jobs |
| `models` | MLflow models |
| `notebooks` | Notebooks |
| `pipelines` | DLT pipelines |
| `registered-models` | Model registry |
| `repos` | Git repos |
| `serving-endpoints` | Model serving |
| `sql/warehouses` | SQL warehouses |

## Script Usage

```bash
# Get permissions on a cluster
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_permissions.py get clusters abc123 -p DEV

# Get permissions on a job
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_permissions.py get jobs 12345 -p DEV

# Grant user CAN_MANAGE on a job
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_permissions.py update jobs 12345 \
  --principal user@example.com --level CAN_MANAGE -p DEV

# Grant group CAN_VIEW on a cluster
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_permissions.py update clusters abc123 \
  --principal data-team --level CAN_ATTACH_TO -p DEV

# List valid permission levels for jobs
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_permissions.py levels jobs -p DEV
```

## Permission Levels

| Level | Description |
|-------|-------------|
| `CAN_VIEW` | View only |
| `CAN_READ` | Read access |
| `CAN_RUN` | Can execute/run |
| `CAN_EDIT` | Edit access |
| `CAN_MANAGE` | Full management |
| `CAN_MANAGE_RUN` | Manage runs |
| `CAN_ATTACH_TO` | Can attach to cluster |
| `CAN_RESTART` | Can restart cluster |
| `IS_OWNER` | Owner |

Note: Available levels vary by object type. Use `levels` subcommand to see valid options.

## CLI Fallback

```bash
# Get permissions
databricks permissions get clusters abc123 -p DEV

# Update permissions
databricks permissions update jobs 12345 \
  --json '{"access_control_list": [{"user_name": "user@example.com", "permission_level": "CAN_MANAGE"}]}' \
  -p DEV
```

## Python SDK

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.iam import AccessControlRequest, PermissionLevel

w = WorkspaceClient(profile="DEV")

# Get job permissions
perms = w.permissions.get_job_permissions(job_id="12345")
for acl in perms.access_control_list:
    print(f"{acl.user_name or acl.group_name}: {acl.all_permissions}")

# Update permissions
w.permissions.update_job_permissions(
    job_id="12345",
    access_control_list=[
        AccessControlRequest(
            user_name="user@example.com",
            permission_level=PermissionLevel.CAN_MANAGE
        )
    ]
)
```

## Arguments

| Arg | Description |
|-----|-------------|
| `get` | Get permissions for an object |
| `update` | Update permissions |
| `levels` | List valid permission levels |
| `--principal` | User email or group name |
| `--level` | Permission level to grant |
| `-p, --profile` | Databricks profile |
| `-o, --output` | Format: table, json, csv |
