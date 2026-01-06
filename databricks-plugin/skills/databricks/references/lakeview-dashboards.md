# Lakeview Dashboard Architecture

Comprehensive guide to Databricks Lakeview (AI/BI) dashboards - structure, patterns, and best practices.

## Dashboard Structure

### URL Patterns

```
Base:     https://{workspace}.cloud.databricks.com/sql/dashboardsv3/{dashboard_id}
Page:     .../dashboardsv3/{dashboard_id}/pages/{page_id}
Dataset:  .../dashboardsv3/{dashboard_id}/datasets/{dataset_name}
```

**Example - Account Usage Dashboard:**
```
Dashboard: 01efad4c105119188449772466d2ba65
Pages:     page1 (Current Usage), 93b02f00 (SQL Warehouse)
```

### Component Hierarchy

```
Dashboard
├── Data (shared datasets)
│   ├── select_* datasets (filter dropdowns)
│   ├── usage_* datasets (chart data)
│   └── warehouse_* datasets (chart data)
├── Pages (tabs)
│   ├── Current Usage (page1)
│   │   ├── Filters (connected to parameters)
│   │   └── Widgets (charts, text)
│   ├── Forecasting
│   └── SQL Warehouse (93b02f00)
│       ├── Filters
│       └── Widgets
└── Parameters (cross-cutting)
```

## Dataset Patterns

### Pattern 1: Static Dropdown Dataset

For fixed filter options (Day/Week/Month, Yes/No, etc.):

```sql
-- Dataset: select_time_key_overview
SELECT explode(array(
    'Day',
    'Week',
    'Month'
)) AS time_key
```

**Result:**
| time_key |
|----------|
| Day      |
| Week     |
| Month    |

### Pattern 2: Dynamic Dropdown Dataset

For options populated from data (workspaces, users, etc.):

```sql
-- Dataset: select_workspace
WITH workspace AS (
    -- Hardcoded workspace ID -> name mapping
    SELECT explode(
        map_entries(from_json(
            '{"4691501256835415":"jhg-databricks-poc","586366940738197":"Exploration"}',
            'MAP<STRING, STRING>'
        ))
    ) AS kvp,
    kvp['key'] AS workspace_id,
    kvp['value'] AS workspace_name
),
-- Join with actual usage to filter to active workspaces
usage_filtered AS (
    SELECT DISTINCT workspace_id
    FROM system.billing.usage
    WHERE usage_date >= :param_start_date
      AND usage_date <= :param_end_date
)
SELECT
    CONCAT(workspace_name, ' (id: ', workspace_id, ')') AS workspace
FROM workspace w
JOIN usage_filtered u ON w.workspace_id = u.workspace_id
ORDER BY workspace_name
```

### Pattern 3: Dynamic Time Aggregation Dataset

For charts with Day/Week/Month filter control:

```sql
-- Dataset: warehouse_query_history
SELECT
    -- Dynamic time aggregation via parameter
    CASE :param_time_key
        WHEN 'Day' THEN DATE(start_time)
        WHEN 'Week' THEN DATE_TRUNC('week', start_time)
        WHEN 'Month' THEN DATE_TRUNC('month', start_time)
        ELSE DATE_TRUNC('week', start_time)
    END AS time_key,

    workspace_id,
    executed_by,
    compute.warehouse_id AS warehouse_id,
    COALESCE(client_application, 'Unknown') AS client_application,

    -- Categorize query source
    CASE
        WHEN query_source.notebook_id IS NOT NULL THEN 'Notebook'
        WHEN query_source.job_info.job_id IS NOT NULL THEN 'Scheduled Job'
        WHEN query_source.dashboard_id IS NOT NULL THEN 'Dashboard'
        WHEN query_source.legacy_dashboard_id IS NOT NULL THEN 'Legacy Dashboard'
        WHEN query_source.sql_query_id IS NOT NULL THEN 'SQL Editor'
        WHEN query_source.alert_id IS NOT NULL THEN 'Alert'
        WHEN query_source.genie_space_id IS NOT NULL THEN 'Genie'
        ELSE 'Direct API/External'
    END AS databricks_source,

    -- Aggregate metrics
    COUNT(*) AS query_count,
    ROUND(SUM(total_duration_ms) / 1000 / 60, 2) AS total_minutes,
    ROUND(AVG(total_duration_ms) / 1000, 2) AS avg_seconds
FROM system.query.history
WHERE
    start_time >= :param_start_date
    AND start_time <= :param_end_date
GROUP BY 1, 2, 3, 4, 5, 6
```

## Parameter System

### Parameter Naming Convention

| Pattern | Example | Purpose |
|---------|---------|---------|
| `param_start_date` | Date picker | Start of date range |
| `param_end_date` | Date picker | End of date range |
| `param_time_key` | Dropdown (Day/Week/Month) | Time aggregation level |
| `param_workspace` | Dropdown | Workspace filter |

### Parameter Default Values

| Type | Syntax | Example |
|------|--------|---------|
| Relative date | `N units ago` | `12 months ago`, `30 days ago` |
| Literal | String/Number | `Today`, `<ALL WORKSPACES>` |
| First option | From dropdown dataset | First row returned |

## Two-Layer Aggregation

### The Problem

Charts can aggregate data at two levels:
1. **SQL Layer** - `DATE_TRUNC` in the dataset query
2. **Chart Layer** - Transform function (MONTHLY, WEEKLY, etc.)

If both layers aggregate, you get incorrect behavior (e.g., daily data shown as monthly).

### The Solution

For **dynamic filter-controlled aggregation**:

1. Use `CASE :param_time_key` in SQL to set data granularity
2. Set chart X-axis **Transform: None** (not MONTHLY, not WEEKLY)
3. Let Lakeview auto-detect granularity from the data

**Example - Chart Configuration:**
```
X-axis: time_key
Transform: None  <-- CRITICAL
Y-axis: SUM(query_count)
Group by: executed_by
```

### When to Use Each

| Use Case | SQL Aggregation | Chart Transform |
|----------|-----------------|-----------------|
| Fixed weekly chart | `DATE_TRUNC('week', ...)` | None |
| Fixed monthly chart | Direct date column | MONTHLY |
| Dynamic Day/Week/Month | `CASE :param_time_key` | **None** |

## Filter Configuration

### Filter Widget Structure

Each page filter has:

1. **Display Label** - "View date by", "Workspace", etc.
2. **Field Dataset** - Provides dropdown options
3. **Target Parameter** - Which parameter receives the selected value
4. **Default Value** - Initial selection

### Filter-Parameter-Dataset Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Filter Widget  │───>│   Parameter     │───>│  Data Dataset   │
│  "View date by" │    │  param_time_key │    │  WHERE clause   │
│  Options: D/W/M │    │  Value: "Week"  │    │  or CASE stmt   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │                                              │
         v                                              v
┌─────────────────┐                          ┌─────────────────┐
│ Dropdown Dataset│                          │  Chart Widgets  │
│ select_time_key │                          │  use result set │
└─────────────────┘                          └─────────────────┘
```

## System Tables Reference

### system.billing.usage

DBU consumption data (billing).

| Column | Type | Description |
|--------|------|-------------|
| `usage_date` | DATE | Date of usage |
| `workspace_id` | STRING | Workspace ID |
| `sku_name` | STRING | SKU (ALL_PURPOSE, JOBS, SQL, etc.) |
| `usage_quantity` | DECIMAL | DBUs consumed |
| `usage_unit` | STRING | Unit (DBU) |
| `billing_origin_product` | STRING | Product category |

### system.query.history

Query execution history (365-day retention).

| Column | Type | Description |
|--------|------|-------------|
| `start_time` | TIMESTAMP | Query start |
| `executed_by` | STRING | User email |
| `compute.warehouse_id` | STRING | Warehouse ID |
| `total_duration_ms` | LONG | Total duration |
| `execution_status` | STRING | FINISHED/FAILED/CANCELED |
| `client_application` | STRING | PowerBI, JDBC, etc. |
| `query_source.notebook_id` | STRING | Source notebook (if any) |
| `query_source.job_info.job_id` | STRING | Source job (if any) |
| `query_source.dashboard_id` | STRING | Source dashboard (if any) |
| `query_source.sql_query_id` | STRING | Source SQL query (if any) |
| `statement_text` | STRING | SQL text |

## Common Operations

### Adding a New Filter

1. Create dropdown dataset (Pattern 1 or 2)
2. Add filter widget to page
3. Connect widget to dropdown dataset
4. Create/update data dataset to use the parameter
5. Connect filter to parameter

### Adding a New Chart

1. Ensure data dataset has required columns
2. Add visualization widget
3. Select dataset
4. Configure X/Y axes and grouping
5. Set Transform: None if using dynamic time aggregation
6. Connect to page filters/parameters

### Modifying Time Aggregation

1. Update dataset SQL with `CASE :param_time_key` pattern
2. Ensure `select_time_key_*` dropdown dataset exists
3. Verify chart X-axis Transform is "None"
4. Test all filter values (Day, Week, Month)

## Account Usage Dashboard Reference

### Dashboard ID
`01efad4c105119188449772466d2ba65`

### Pages

| Page ID | Name | Purpose |
|---------|------|---------|
| `page1` | Current Usage | DBU billing overview |
| `93b02f00` | SQL Warehouse | Query history analytics |

### Key Datasets

| Dataset | Type | Purpose |
|---------|------|---------|
| `select_time_key_overview` | Static dropdown | Day/Week/Month options |
| `select_workspace` | Dynamic dropdown | Workspace filter options |
| `usage_overview` | Chart data | DBU usage over time |
| `warehouse_query_history` | Chart data | Query metrics by time |

### SQL Warehouse Tab Datasets

```sql
-- warehouse_query_history parameters:
-- :param_time_key (from select_time_key_overview)
-- :param_start_date (date picker)
-- :param_end_date (date picker)
```

### Charts on SQL Warehouse Tab

| Chart | Type | X-axis | Y-axis | Group by |
|-------|------|--------|--------|----------|
| WHO \| Query Count by User | Stacked Bar | time_key | query_count | executed_by |
| WHAT \| Query Count by Source | Stacked Bar | time_key | query_count | databricks_source |
| WHEN \| Compute Minutes Over Time | Line | time_key | total_minutes | - |

## Best Practices

### Dataset Naming

- `select_*` - Dropdown datasets
- `usage_*` - Usage/billing data
- `warehouse_*` - Warehouse/query data
- Descriptive names for chart-specific datasets

### Parameter Naming

- Always use `param_` prefix
- Use consistent names across datasets
- Document expected values in SQL comments

### Performance

- Pre-aggregate in SQL when possible
- Limit date ranges with parameters
- Use `LIMIT` for dropdown datasets if large
- Consider materialized views for complex aggregations

### Maintainability

- Comment SQL with parameter expectations
- Use CTEs for complex queries
- Keep dropdown datasets simple
- Test all filter combinations after changes
