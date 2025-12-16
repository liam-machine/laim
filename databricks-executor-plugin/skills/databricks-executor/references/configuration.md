# Databricks Executor Configuration Guide

## Authentication Methods

### 1. Environment Variables (Recommended for CI/CD)

Set these environment variables:

```bash
export DATABRICKS_HOST="https://adb-1234567890.1.azuredatabricks.net"
export DATABRICKS_TOKEN="dapi1234567890abcdef"
export DATABRICKS_CLUSTER_ID="1234-567890-abc123"
```

### 2. Databricks CLI Configuration File

Create or edit `~/.databrickscfg`:

```ini
[DEFAULT]
host = https://adb-1234567890.1.azuredatabricks.net
token = dapi1234567890abcdef
cluster_id = 1234-567890-abc123

[PROD]
host = https://adb-prod.azuredatabricks.net
token = dapi-prod-token
cluster_id = prod-cluster-id

[DEV]
host = https://adb-dev.azuredatabricks.net
token = dapi-dev-token
cluster_id = dev-cluster-id
```

Use profiles with `--profile`:
```bash
python databricks_exec.py --profile PROD -c "print(spark.version)"
```

### 3. CLI Arguments (Highest Priority)

```bash
python databricks_exec.py \
  --host "https://adb-xxx.azuredatabricks.net" \
  --token "dapi-xxx" \
  --cluster-id "cluster-id" \
  -c "print(1)"
```

## Configuration Priority

Values are resolved in this order (highest to lowest):
1. CLI arguments (`--host`, `--token`, `--cluster-id`)
2. Environment variables (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_CLUSTER_ID`)
3. Profile in `~/.databrickscfg` (specified by `--profile` or `DATABRICKS_PROFILE`)
4. DEFAULT profile in `~/.databrickscfg`

## Getting Your Token

### Personal Access Token (PAT)

1. Go to your Databricks workspace
2. Click your profile icon → **Settings**
3. Go to **Developer** → **Access tokens**
4. Click **Generate new token**
5. Give it a name and optionally set expiration
6. Copy the token (you won't see it again)

### OAuth Token (Service Principal)

For automated pipelines, use a service principal:

1. Create a service principal in Azure AD / Databricks account
2. Grant it workspace access
3. Use OAuth to get access tokens:

```python
import requests

response = requests.post(
    "https://accounts.azuredatabricks.net/oidc/accounts/{account_id}/v1/token",
    data={
        "grant_type": "client_credentials",
        "client_id": "<sp-client-id>",
        "client_secret": "<sp-client-secret>",
        "scope": "all-apis"
    }
)
token = response.json()["access_token"]
```

## Finding Your Cluster ID

### From Databricks UI

1. Go to **Compute** in the sidebar
2. Click on your cluster
3. The cluster ID is in the URL: `https://xxx.azuredatabricks.net/#/compute/clusters/{cluster-id}`

### From CLI

```bash
# List all clusters
databricks clusters list

# Get specific cluster
databricks clusters get --cluster-id "1234-567890-abc123"
```

### From API

```bash
curl -X GET "https://your-workspace.azuredatabricks.net/api/2.0/clusters/list" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN"
```

## Cluster Requirements

The cluster must:
- Be in **RUNNING** state
- Have the user's token authorized to access it
- Support the language you want to execute (Python, SQL, Scala, R)

Check cluster state:
```bash
python databricks_exec.py --check-cluster
```

## Troubleshooting

### "Missing required configuration"

Ensure you have set:
- `DATABRICKS_HOST` or `--host`
- `DATABRICKS_TOKEN` or `--token`
- `DATABRICKS_CLUSTER_ID` or `--cluster-id`

### "API Error (401)"

Your token is invalid or expired. Generate a new token.

### "API Error (403)"

Your token doesn't have permission to access the cluster or workspace.

### "API Error (404)"

The cluster ID doesn't exist or was deleted.

### "Cluster is not running"

Start the cluster from the Databricks UI or wait for it to auto-start.

### "Context creation failed"

- The cluster might be starting up - wait and retry
- You've hit the maximum execution contexts limit - destroy old contexts
- The cluster doesn't support the requested language
