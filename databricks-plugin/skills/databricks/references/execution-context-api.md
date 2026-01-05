# Databricks Execution Context API Reference

## API Version

The `/db:execute` command uses the **Execution Context API 1.2** which provides direct code execution on running Spark clusters.

> **Note**: This API is separate from the Statement Execution API used by `/db:query`. Use Execution Context for multi-language code execution on clusters; use Statement Execution for SQL queries on warehouses.

## Endpoints

### Create Context

**POST** `/api/1.2/contexts/create`

Creates an execution context on a cluster.

```json
{
  "language": "python",
  "clusterId": "1234-567890-abc123"
}
```

Response:
```json
{
  "id": "context-id-here"
}
```

### Execute Command

**POST** `/api/1.2/commands/execute`

Submits a command for execution.

```json
{
  "language": "python",
  "contextId": "context-id",
  "clusterId": "cluster-id",
  "command": "print(spark.version)"
}
```

Response:
```json
{
  "id": "command-id-here"
}
```

### Check Command Status

**GET** `/api/1.2/commands/status`

Query parameters:
- `clusterId` - Cluster ID
- `contextId` - Context ID
- `commandId` - Command ID

Response:
```json
{
  "id": "command-id",
  "status": "Finished",
  "results": {
    "resultType": "text",
    "data": "3.3.0"
  }
}
```

### Destroy Context

**POST** `/api/1.2/contexts/destroy`

```json
{
  "contextId": "context-id",
  "clusterId": "cluster-id"
}
```

### Cancel Command

**POST** `/api/1.2/commands/cancel`

```json
{
  "clusterId": "cluster-id",
  "contextId": "context-id",
  "commandId": "command-id"
}
```

## Command Statuses

| Status | Description |
|--------|-------------|
| `Queued` | Command is waiting to execute |
| `Running` | Command is currently executing |
| `Finished` | Command completed successfully |
| `Error` | Command failed with an error |
| `Cancelled` | Command was cancelled |

## Result Types

### Text Result

```json
{
  "resultType": "text",
  "data": "Hello, World!"
}
```

### Table Result

```json
{
  "resultType": "table",
  "schema": [
    {"name": "id", "type": "\"integer\""},
    {"name": "name", "type": "\"string\""}
  ],
  "data": [
    [1, "Alice"],
    [2, "Bob"]
  ],
  "truncated": false
}
```

### Error Result

```json
{
  "resultType": "error",
  "summary": "NameError: name 'undefined_var' is not defined",
  "cause": "<full stack trace>"
}
```

### Image Result

```json
{
  "resultType": "images",
  "data": ["<base64-encoded-png>"]
}
```

## Supported Languages

| Language | Value | Notes |
|----------|-------|-------|
| Python | `python` | Full PySpark support, `spark` variable available |
| SQL | `sql` | Spark SQL queries |
| Scala | `scala` | Full Spark Scala support |
| R | `r` | SparkR support |

## Rate Limits & Best Practices

### Context Limits

- Each cluster has a maximum number of execution contexts
- Always destroy contexts when done
- Use context managers (`with` statement) for automatic cleanup

### Polling Best Practices

- Default poll interval: 0.5 seconds
- For long-running commands, consider longer intervals (1-2 seconds)
- Implement timeout handling for safety

### Large Results

- Table results may be truncated if too large
- Use `.limit()` in SQL/Spark queries for large datasets
- Stream large results to files instead of returning them

## Error Handling

### HTTP Errors

| Code | Meaning |
|------|---------|
| 400 | Bad request - check parameters |
| 401 | Unauthorized - invalid/expired token |
| 403 | Forbidden - no access to cluster |
| 404 | Not found - cluster/context doesn't exist |
| 429 | Rate limited - slow down requests |
| 500 | Server error - retry with backoff |

### Execution Errors

Errors from code execution are returned with `resultType: "error"`:

```json
{
  "status": "Finished",
  "results": {
    "resultType": "error",
    "summary": "Error message",
    "cause": "Full traceback"
  }
}
```

## Security Considerations

- Tokens grant full cluster access - protect them
- Use least-privilege service principals for automation
- Rotate tokens regularly
- Never commit tokens to version control
- Use environment variables or secret managers
