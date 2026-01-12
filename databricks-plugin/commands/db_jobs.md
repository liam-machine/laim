---
description: Manage Databricks jobs and runs
argument-hint: "[list|get|run|runs|cancel] [JOB_ID] [-p PROFILE]"
---

# Databricks Jobs

List, trigger, and monitor jobs and runs.

## Quick Reference

| Action | Command |
|--------|---------|
| List jobs | `db_jobs.py list -p PROFILE` |
| Get job | `db_jobs.py get JOB_ID -p PROFILE` |
| Run job | `db_jobs.py run JOB_ID -p PROFILE` |
| List runs | `db_jobs.py runs JOB_ID -p PROFILE` |
| Cancel run | `db_jobs.py cancel RUN_ID -p PROFILE` |
| Get output | `db_jobs.py run-output RUN_ID -p PROFILE` |

## Script Usage

```bash
# List all jobs
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py list -p DEV

# Filter by name
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py list -p DEV --name "ETL"

# Get job details
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py get 12345 -p DEV

# Run a job and wait
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py run 12345 -p DEV --wait

# Run with parameters
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py run 12345 -p DEV \
  --params '{"notebook_params": {"date": "2024-01-01"}}'

# List recent runs
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py runs 12345 -p DEV --limit 5

# Cancel a run
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py cancel 67890 -p DEV

# Get run output
python3 ${CLAUDE_PLUGIN_ROOT}/skills/databricks/scripts/db_jobs.py run-output 67890 -p DEV
```

## CLI Fallback

```bash
# List jobs
databricks jobs list -p DEV

# Get job (POSITIONAL arg)
databricks jobs get 12345 -p DEV

# Run job
databricks jobs run-now 12345 -p DEV

# With parameters
databricks jobs run-now 12345 --json '{"notebook_params": {"key": "value"}}' -p DEV

# List runs
databricks jobs list-runs --job-id 12345 --limit 5 -p DEV

# Cancel run
databricks jobs cancel-run 67890 -p DEV

# Get run output
databricks jobs get-run-output 67890 -p DEV
```

## Python SDK

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEV")

# List jobs
for job in w.jobs.list():
    print(f"{job.job_id}: {job.settings.name}")

# Run job and wait
run = w.jobs.run_now_and_wait(job_id=12345)
print(f"Result: {run.state.result_state.value}")

# With parameters
run = w.jobs.run_now_and_wait(
    job_id=12345,
    notebook_params={"date": "2024-01-01"}
)

# List runs
for run in w.jobs.list_runs(job_id=12345, limit=10):
    print(f"Run {run.run_id}: {run.state.result_state}")
```

## Run States

| Lifecycle State | Meaning |
|-----------------|---------|
| `PENDING` | Waiting to start |
| `RUNNING` | Currently executing |
| `TERMINATING` | Shutting down |
| `TERMINATED` | Finished |
| `SKIPPED` | Skipped (concurrent run limit) |
| `INTERNAL_ERROR` | Platform error |

## Result States

| Result State | Meaning |
|--------------|---------|
| `SUCCESS` | Completed successfully |
| `FAILED` | Task failed |
| `TIMEDOUT` | Exceeded timeout |
| `CANCELED` | Manually cancelled |
| `UPSTREAM_FAILED` | Dependency failed |

## Arguments

| Arg | Description |
|-----|-------------|
| `list` | List all jobs |
| `get` | Get job details |
| `run` | Trigger a job run |
| `runs` | List job runs |
| `cancel` | Cancel a run |
| `run-output` | Get run output |
| `-p, --profile` | Databricks profile |
| `--name` | Filter by job name |
| `--limit` | Max runs to show |
| `--wait` | Wait for completion |
| `--params` | Job parameters (JSON) |
| `-o, --output` | Format: table, json, csv |

## Common Gotchas

| Issue | Solution |
|-------|----------|
| `jobs get --job-id 123` | Use positional: `jobs get 123` |
| `get-run-output` on multi-task | Get individual task run IDs first |
| Parameters not working | Use `notebook_params` for notebooks |
