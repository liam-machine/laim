---
description: Unity Catalog operations (catalogs, schemas, tables, volumes, grants)
argument-hint: "[catalogs|schemas|tables|describe|volumes|grants] [PATH]"
---

# Unity Catalog

Browse and manage Unity Catalog objects: catalogs, schemas, tables, volumes, and grants.

## Quick Reference

| Action | Command |
|--------|---------|
| List catalogs | `db_catalog.py catalogs -p PROFILE` |
| List schemas | `db_catalog.py schemas CATALOG -p PROFILE` |
| List tables | `db_catalog.py tables CATALOG.SCHEMA -p PROFILE` |
| Describe table | `db_catalog.py describe CATALOG.SCHEMA.TABLE -p PROFILE` |
| List volumes | `db_catalog.py volumes CATALOG.SCHEMA -p PROFILE` |
| Show grants | `db_catalog.py grants TYPE FULL_NAME -p PROFILE` |

## Script Usage

```bash
# List all catalogs
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py catalogs -p DEV

# List schemas in a catalog
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py schemas main -p DEV

# List tables in a schema
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py tables main.default -p DEV

# Describe a table (columns, metadata)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py describe main.default.customers -p DEV

# Describe table with JSON output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py describe main.default.customers -p DEV -o json

# List volumes
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py volumes main.default -p DEV

# Show grants on a catalog
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py grants CATALOG main -p DEV

# Show grants on a table
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_catalog.py grants TABLE main.default.customers -p DEV
```

## Path Conventions

| Object | Format | Example |
|--------|--------|---------|
| Catalog | `NAME` | `main` |
| Schema | `CATALOG.SCHEMA` | `main.default` |
| Table | `CATALOG.SCHEMA.TABLE` | `main.default.customers` |
| Volume | `CATALOG.SCHEMA.VOLUME` | `main.default.my_volume` |

## Securable Types for Grants

| Type | Description |
|------|-------------|
| `CATALOG` | Catalog-level grants |
| `SCHEMA` | Schema-level grants |
| `TABLE` | Table/view grants |
| `VOLUME` | Volume grants |
| `FUNCTION` | Function grants |
| `EXTERNAL_LOCATION` | External location grants |
| `STORAGE_CREDENTIAL` | Storage credential grants |

## CLI Fallback

```bash
# List catalogs
databricks catalogs list -p DEV

# List schemas
databricks schemas list main -p DEV

# List tables
databricks tables list main.default -p DEV

# Get table info
databricks tables get main.default.customers -p DEV

# List volumes
databricks volumes list main.default -p DEV

# Show grants
databricks grants get catalog main -p DEV
```

## Python SDK

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List catalogs
for cat in w.catalogs.list():
    print(cat.name)

# List tables
for table in w.tables.list(catalog_name="main", schema_name="default"):
    print(f"{table.full_name}: {table.table_type.value}")

# Get table details
table = w.tables.get(full_name="main.default.customers")
for col in table.columns:
    print(f"  {col.name}: {col.type_text}")
```

## Arguments

| Arg | Description |
|-----|-------------|
| `catalogs` | List all catalogs |
| `schemas` | List schemas in a catalog |
| `tables` | List tables in a schema |
| `describe` | Show table details and columns |
| `volumes` | List volumes in a schema |
| `grants` | Show grants on a securable |
| `-p, --profile` | Databricks profile |
| `-o, --output` | Format: table, json, csv |
