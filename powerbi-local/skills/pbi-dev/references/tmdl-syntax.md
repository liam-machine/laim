# TMDL (Tabular Model Definition Language) Syntax Reference

This document provides comprehensive syntax documentation for TMDL (Tabular Model Definition Language), the text-based format used to define Power BI semantic models and Analysis Services tabular models.

## Table of Contents

1. [TMDL Overview](#1-tmdl-overview)
2. [File Structure in PBIP Projects](#2-file-structure-in-pbip-projects)
3. [Core Syntax Elements](#3-core-syntax-elements)
4. [Object Types Reference](#4-object-types-reference)
5. [Data Types](#5-data-types)
6. [LineageTag Rules](#6-lineagetag-rules)
7. [Best Practices](#7-best-practices)

---

## 1. TMDL Overview

### What is TMDL?

TMDL (Tabular Model Definition Language) is a human-readable, text-based metadata format for defining tabular data models. It was introduced as an alternative to the JSON-based model.bim (TMSL) format and is designed to be:

- **Human-readable**: Uses a clean, YAML-like syntax that is easy to read and write
- **Source control friendly**: Files are designed for clean diffs and easier merge conflict resolution
- **Modular**: Splits model definitions across multiple files by object type
- **Compatible**: Works with Power BI semantic models and Analysis Services tabular models at compatibility level 1200 or higher

### Relationship to TOM (Tabular Object Model)

TMDL is the serialization format for the Tabular Object Model (TOM). TOM is the .NET object model that represents tabular models programmatically:

| Concept | TOM | TMDL |
|---------|-----|------|
| Model root | `Model` class | `model.tmdl` file |
| Tables | `Table` collection | Individual files in `tables/` folder |
| Relationships | `Relationship` collection | `relationships.tmdl` file |
| Roles | `Role` collection | Individual files in `roles/` folder |
| Cultures | `Culture` collection | Individual files in `cultures/` folder |

The TOM API (`TmdlSerializer` class) can serialize and deserialize TMDL:

```csharp
// Serialize model to TMDL folder
TmdlSerializer.SerializeDatabaseToFolder(database, path);

// Deserialize TMDL folder to model
Database database = TmdlSerializer.DeserializeDatabaseFromFolder(path);
```

---

## 2. File Structure in PBIP Projects

### TMDL Folder Organization

When using TMDL format in a Power BI Project (PBIP), the semantic model definition is stored in a `definition/` folder:

```
ProjectName.SemanticModel/
├── .pbi/
│   ├── localSettings.json        # User-specific settings (git-ignored)
│   ├── editorSettings.json       # Shared editor settings
│   └── cache.abf                 # Model cache (git-ignored)
├── definition/                    # TMDL definition folder
│   ├── database.tmdl             # Database properties
│   ├── model.tmdl                # Model properties and references
│   ├── relationships.tmdl        # All relationship definitions
│   ├── expressions.tmdl          # Shared/named M expressions
│   ├── dataSources.tmdl          # Data source connections (if any)
│   ├── tables/
│   │   ├── Sales.tmdl            # Table with columns, measures, partitions
│   │   ├── Products.tmdl
│   │   ├── Calendar.tmdl
│   │   └── ...
│   ├── roles/
│   │   ├── Reader.tmdl           # RLS role definitions
│   │   └── Manager.tmdl
│   ├── cultures/
│   │   ├── en-US.tmdl            # Localization/translations
│   │   └── de-DE.tmdl
│   └── perspectives/
│       └── Sales Analysis.tmdl   # Perspective definitions
├── definition.pbism              # Semantic model entry point
├── diagramLayout.json            # Diagram view layout
└── .platform                     # Fabric platform properties
```

### File Descriptions

| File | Quantity | Description |
|------|----------|-------------|
| `database.tmdl` | One | Database name and compatibility level |
| `model.tmdl` | One | Model properties, culture, and object references |
| `relationships.tmdl` | One | All relationship definitions |
| `expressions.tmdl` | One | Named M expressions (parameters, shared queries) |
| `dataSources.tmdl` | One | Legacy data source definitions |
| `tables/*.tmdl` | One per table | Table definition with columns, measures, partitions |
| `roles/*.tmdl` | One per role | Security role definitions with table permissions |
| `cultures/*.tmdl` | One per culture | Translation/localization data |
| `perspectives/*.tmdl` | One per perspective | Perspective definitions |

### Enabling TMDL in Power BI Desktop

To use TMDL format for semantic models:

1. Go to **File > Options and settings > Options**
2. Select **Preview features**
3. Enable **Store semantic model using TMDL format**
4. Save and reopen the project

**Note**: Converting from model.bim to TMDL is irreversible within the same project.

---

## 3. Core Syntax Elements

### Indentation Rules

TMDL uses **strict whitespace indentation** with tabs (not spaces) as the default:

```tmdl
table Sales                           // Level 0 (root object)
    lineageTag: abc123-def456         // Level 1 (object properties)

    measure 'Total Sales' = SUM(...)  // Level 1 (child object)
        formatString: $#,##0.00       // Level 2 (child properties)
        displayFolder: Revenue

    column Amount                     // Level 1 (child object)
        dataType: decimal             // Level 2 (child properties)
        sourceColumn: Amount
```

**Indentation Levels:**

| Level | Purpose | Example |
|-------|---------|---------|
| 0 | Root objects | `table`, `relationship`, `role`, `model` |
| 1 | Object properties and direct children | `lineageTag:`, `measure`, `column` |
| 2 | Child object properties | `formatString:`, `dataType:` |
| 3+ | Multi-line expression content | DAX/M expression lines |

### Object Declarations

Objects are declared with their type keyword followed by the name:

```tmdl
// Basic object declaration
table Sales

// Object with name containing special characters (must use single quotes)
table 'Fact Sales'

// Object with default property (uses = delimiter)
measure 'Total Sales' = SUM(Sales[Amount])

// Object with GUID identifier
relationship 9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d
```

**Naming Rules:**

- Names containing these characters must be wrapped in single quotes: `. = : ' ` and whitespace
- Single quotes within names are escaped by doubling: `'It''s a Name'`
- GUID identifiers (for relationships) do not require quotes

### Property Syntax

Properties use two delimiters depending on their type:

#### Colon Delimiter (`:`) - Standard Properties

```tmdl
table Sales
    lineageTag: e9374b9a-faee-4f9e-b2e7-d9aafb9d6a91
    dataCategory: Time
    isHidden: true
```

#### Equals Delimiter (`=`) - Expressions and Default Properties

```tmdl
// Expression properties
measure 'Total Sales' = SUM(Sales[Amount])

// Partition source expression
partition Sales-Partition = m
    source =
        let
            Source = Sql.Database("server", "database")
        in
            Source
```

### Boolean Properties

Boolean properties can use explicit values or shorthand:

```tmdl
column ProductKey
    isHidden: true           // Explicit true
    isKey: false             // Explicit false
    isNullable              // Shorthand for true (property present = true)
```

### Text Property Values

```tmdl
measure 'Sales Amount' = SUM(...)
    formatString: $#,##0.00
    description: "This is a simple description"
    displayFolder: "My ""Quoted"" Folder"    // Escape quotes with ""
```

**Rules:**

- Leading/trailing double quotes are optional and auto-stripped
- Use double quotes if value contains leading/trailing whitespace
- Escape internal double quotes with `""`

### Multi-Line Expressions

Multi-line expressions must be indented one level deeper than the parent property:

```tmdl
measure 'Sales YoY %' =
        var currentYear = [Total Sales]
        var priorYear = CALCULATE(
            [Total Sales],
            SAMEPERIODLASTYEAR('Calendar'[Date])
        )
        return
        DIVIDE(currentYear - priorYear, priorYear)
    formatString: 0.00%;-0.00%;0.00%
```

#### Backtick Enclosure for Exact Formatting

Use triple backticks to preserve exact whitespace and blank lines:

```tmdl
measure 'Complex Measure' = ```
var step1 = CALCULATE(...)

var step2 = SUMX(...)

return step1 + step2
```
```

### Comments and Descriptions

TMDL uses triple-slash (`///`) for object descriptions:

```tmdl
/// This table contains all sales transactions
/// Data refreshed daily from the warehouse
table Sales
    lineageTag: abc123

    /// Total sales revenue in USD
    measure 'Total Sales' = SUM(Sales[Amount])
        formatString: $#,##0.00

    /// Primary key for the sales table
    column SalesID
        dataType: int64
        isKey
```

**Rules:**

- No whitespace allowed between description block and object declaration
- Multiple lines are supported
- Descriptions are stored in the object's `description` property

### Object References with `ref`

The `ref` keyword declares and preserves collection ordering:

```tmdl
model Model
    culture: en-US

    ref table Calendar
    ref table Sales
    ref table Products
    ref table Customers

    ref role Reader
    ref role Manager
```

---

## 4. Object Types Reference

### Database Object

The `database.tmdl` file defines the database container:

```tmdl
database ContosoSales
    compatibilityLevel: 1567
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `compatibilityLevel` | int | Yes | Model compatibility level (1200-1600+) |

### Model Object

The `model.tmdl` file defines the semantic model:

```tmdl
model Model
    culture: en-US
    defaultPowerBIDataSourceVersion: powerBI_V3
    discourageImplicitMeasures

    ref table Calendar
    ref table Sales
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `culture` | string | No | Default culture/locale (e.g., `en-US`) |
| `defaultPowerBIDataSourceVersion` | enum | No | `powerBI_V3` for modern datasets |
| `discourageImplicitMeasures` | bool | No | Disable implicit measures in reports |
| `dataAccessOptions` | object | No | Data access configuration |

### Table Object

Tables are defined in individual files under `tables/`:

```tmdl
table Sales
    lineageTag: e9374b9a-faee-4f9e-b2e7-d9aafb9d6a91
    dataCategory: Regular

    column SalesID
        dataType: int64
        isKey
        sourceColumn: SalesID
        lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890

    column Amount
        dataType: decimal
        formatString: $#,##0.00
        sourceColumn: Amount
        summarizeBy: sum
        lineageTag: b2c3d4e5-f6a7-8901-bcde-f12345678901

    measure 'Total Sales' = SUM(Sales[Amount])
        formatString: $#,##0.00
        lineageTag: c3d4e5f6-a7b8-9012-cdef-123456789012

    partition Sales-Partition = m
        mode: import
        source =
            let
                Source = Sql.Database("server", "database"),
                Sales = Source{[Schema="dbo",Item="Sales"]}[Data]
            in
                Sales
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `lineageTag` | GUID | Yes | Unique identifier for model lineage |
| `dataCategory` | enum | No | `Regular`, `Time`, `Geography`, etc. |
| `isHidden` | bool | No | Hide table from report view |
| `description` | string | No | Table description |
| `columns` | collection | No | Column definitions (inline) |
| `measures` | collection | No | Measure definitions (inline) |
| `partitions` | collection | Yes | Data partition definitions (inline) |
| `hierarchies` | collection | No | Hierarchy definitions (inline) |

### Column Object

Columns are defined within their parent table:

```tmdl
column 'Product Name'
    dataType: string
    sourceColumn: ProductName
    lineageTag: d4e5f6a7-b8c9-0123-def0-234567890123
    isHidden: false
    summarizeBy: none

column 'Unit Price'
    dataType: decimal
    formatString: $#,##0.00
    sourceColumn: UnitPrice
    lineageTag: e5f6a7b8-c9d0-1234-ef01-345678901234
    summarizeBy: none

column 'Order Date'
    dataType: dateTime
    formatString: Short Date
    sourceColumn: OrderDate
    lineageTag: f6a7b8c9-d0e1-2345-f012-456789012345
    isKey: false
    sortByColumn: 'Order Date Key'
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `dataType` | enum | Yes | Data type (see Data Types section) |
| `sourceColumn` | string | Yes* | Source column name from partition |
| `lineageTag` | GUID | Yes | Unique identifier |
| `isHidden` | bool | No | Hide from report field list |
| `isKey` | bool | No | Mark as table key column |
| `isNullable` | bool | No | Allow null values |
| `formatString` | string | No | Display format |
| `summarizeBy` | enum | No | Default aggregation: `none`, `sum`, `count`, `min`, `max`, `average` |
| `sortByColumn` | ref | No | Reference to sort-by column |
| `displayFolder` | string | No | Folder for organization |
| `description` | string | No | Column description |

*`sourceColumn` is required for data columns; not used for calculated columns.

### Calculated Column

```tmdl
column 'Full Name' = [First Name] & " " & [Last Name]
    dataType: string
    lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890
    isDataTypeInferred
```

| Additional Property | Type | Description |
|--------------------|------|-------------|
| `expression` | DAX | Calculated column DAX expression (via `=`) |
| `isDataTypeInferred` | bool | Data type inferred from expression |

### Measure Object

Measures are defined within their parent table:

```tmdl
measure 'Total Revenue' = SUMX(Sales, Sales[Quantity] * Sales[Unit Price])
    formatString: $#,##0.00
    displayFolder: Revenue
    lineageTag: b2c3d4e5-f6a7-8901-bcde-f12345678901
    description: "Total revenue from all sales transactions"

measure 'YTD Revenue' =
        TOTALYTD([Total Revenue], 'Calendar'[Date])
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: c3d4e5f6-a7b8-9012-cdef-123456789012
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `expression` | DAX | Yes | Measure DAX expression (via `=`) |
| `formatString` | string | No | Display format string |
| `displayFolder` | string | No | Folder path (use `\` for nesting) |
| `lineageTag` | GUID | Yes | Unique identifier |
| `description` | string | No | Measure description |
| `isHidden` | bool | No | Hide from report field list |
| `kpi` | object | No | KPI configuration |
| `detailRowsDefinition` | object | No | Detail rows expression |

### Partition Object

Partitions define data sources within tables:

```tmdl
partition Sales-Partition = m
    mode: import
    source =
        let
            Source = Sql.Database("server", "database"),
            dbo_Sales = Source{[Schema="dbo",Item="Sales"]}[Data]
        in
            dbo_Sales
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `mode` | enum | Yes | `import`, `directQuery`, `dual` |
| `source` | M expression | Yes | Power Query M expression |

#### Calculated Table Partition

```tmdl
table 'Date Table'
    lineageTag: ...

    partition 'Date Table' = calculated
        mode: import
        source = CALENDAR(DATE(2020,1,1), DATE(2025,12,31))
```

### Relationship Object

Relationships are defined in `relationships.tmdl`:

```tmdl
relationship 9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d
    fromColumn: Sales.'Product Key'
    toColumn: Products.'Product Key'

relationship 1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d
    fromColumn: Sales.'Customer Key'
    toColumn: Customers.'Customer Key'
    crossFilteringBehavior: bothDirections
    isActive: false
    securityFilteringBehavior: oneDirection
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `fromColumn` | ref | Yes | Foreign key column (`Table.Column`) |
| `toColumn` | ref | Yes | Primary key column (`Table.Column`) |
| `crossFilteringBehavior` | enum | No | `oneDirection`, `bothDirections` |
| `isActive` | bool | No | Active relationship (default: true) |
| `securityFilteringBehavior` | enum | No | RLS filter direction |
| `joinOnDateBehavior` | enum | No | Date join behavior |
| `relyOnReferentialIntegrity` | bool | No | Assume referential integrity |

**Cardinality:**

- **One-to-Many** (default): `toColumn` must be unique
- **Many-to-Many**: Both columns can have duplicates (compatibility level 1500+)
- **One-to-One**: Both columns must be unique

### Role Object

Security roles are defined in `roles/`:

```tmdl
role Reader
    modelPermission: read

    tablePermission Sales = 'Sales'[Region] = "North America"
    tablePermission Customers = 'Customers'[Country] = "USA"
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `modelPermission` | enum | Yes | `read`, `readRefresh`, `none` |
| `tablePermission` | collection | No | Table-level RLS filters |
| `description` | string | No | Role description |
| `members` | collection | No | Role members (for AS only) |

### Calculation Group Object

Calculation groups are specialized tables:

```tmdl
table 'Time Intelligence'
    lineageTag: ...

    calculationGroup
        precedence: 20

        calculationItem Current = SELECTEDMEASURE()

        calculationItem MTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESMTD('Calendar'[Date])
                )

        calculationItem YTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESYTD('Calendar'[Date])
                )

        calculationItem 'PY' =
                CALCULATE(
                    SELECTEDMEASURE(),
                    SAMEPERIODLASTYEAR('Calendar'[Date])
                )

    column 'Time Calculation'
        dataType: string
        sourceColumn: Name
        sortByColumn: Ordinal

    column Ordinal
        dataType: int64
        sourceColumn: Ordinal
        isHidden
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `precedence` | int | No | Evaluation order (higher = applied later) |
| `calculationItem` | collection | Yes | Calculation item definitions |

### Named Expression (Shared Query/Parameter)

Named expressions are defined in `expressions.tmdl`:

```tmdl
expression ServerName = "sql-server.database.windows.net" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

expression DatabaseName = "ContosoRetail" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

expression SharedDate =
        let
            Source = Date.From(DateTime.LocalNow())
        in
            Source
    meta [IsParameterQuery=true, Type="Date"]
```

---

## 5. Data Types

TMDL supports the following data types for columns:

| TMDL Data Type | DAX Data Type | .NET Type | Description |
|----------------|---------------|-----------|-------------|
| `string` | Text | String | Unicode text (max 32,767 bytes) |
| `int64` | Whole Number | Int64 | 64-bit integer |
| `double` | Decimal Number | Double | 64-bit floating point |
| `decimal` | Currency | Decimal | Fixed precision (4 decimal places) |
| `dateTime` | Date/Time | DateTime | Date and time values |
| `boolean` | True/False | Boolean | True or false |
| `binary` | Binary | Byte[] | Binary data (max 67,108,864 bytes) |

### Data Type Ranges

| Data Type | Range/Limits |
|-----------|--------------|
| `int64` | -9,223,372,036,854,775,807 to 9,223,372,036,854,775,806 |
| `double` | -1.79E+308 to 1.79E+308 (15 significant digits) |
| `decimal` | -922,337,203,685,477.5807 to 922,337,203,685,477.5806 |
| `dateTime` | Valid dates after March 1, 1900 |
| `string` | Max 32,767 bytes (approx 10,922 Unicode characters) |

### Common Format Strings

| Format | Example Output | Description |
|--------|----------------|-------------|
| `$#,##0.00` | $1,234.56 | US currency |
| `#,##0` | 1,235 | Whole number with thousands separator |
| `0.00%` | 12.34% | Percentage with 2 decimals |
| `0.00` | 1234.56 | Decimal with 2 places |
| `Short Date` | 1/15/2024 | Locale short date |
| `Long Date` | Monday, January 15, 2024 | Locale long date |
| `General Date` | 1/15/2024 3:30:00 PM | Date and time |
| `#,##0.00;(#,##0.00);0.00` | (1,234.56) | Negative in parentheses |

---

## 6. LineageTag Rules

### What Are LineageTags?

LineageTags are GUIDs that uniquely identify objects within a model. They serve several purposes:

- **Object Identity**: Maintain object identity across renames
- **Report Binding**: Reports reference objects by lineageTag, not by name
- **Deployment**: Track objects across deployments and merges
- **Refresh**: Identify objects for incremental refresh

### When LineageTags Are Required

| Object Type | LineageTag Required |
|-------------|---------------------|
| Table | Yes |
| Column | Yes |
| Measure | Yes |
| Hierarchy | Yes |
| Level | Yes |
| Partition | No |
| Relationship | Uses GUID as name |
| Role | No |
| Calculation Group | Yes (via table) |
| Calculation Item | Yes |

### Generating New LineageTags

LineageTags follow the standard GUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

**PowerShell:**
```powershell
[guid]::NewGuid().ToString()
# Output: e9374b9a-faee-4f9e-b2e7-d9aafb9d6a91
```

**Python:**
```python
import uuid
str(uuid.uuid4())
# Output: 'e9374b9a-faee-4f9e-b2e7-d9aafb9d6a91'
```

**C#:**
```csharp
Guid.NewGuid().ToString()
// Output: "e9374b9a-faee-4f9e-b2e7-d9aafb9d6a91"
```

### LineageTag Best Practices

1. **Never reuse lineageTags** between different objects
2. **Preserve lineageTags** when renaming objects
3. **Generate new lineageTags** only when creating new objects
4. **Document lineageTag changes** in source control commits

---

## 7. Best Practices

### File Organization

1. **One table per file**: Each table should have its own `.tmdl` file
2. **Meaningful names**: Use descriptive file names matching object names
3. **Consistent casing**: Use PascalCase for table file names

### Source Control

1. **Use `.gitignore`** for user-specific files:
   ```
   .pbi/localSettings.json
   .pbi/cache.abf
   ```

2. **Commit atomic changes**: Group related object changes in single commits
3. **Review diffs**: TMDL produces clean diffs for easy code review

### Measure Organization

1. **Use displayFolders** to group related measures:
   ```tmdl
   measure 'Total Sales' = ...
       displayFolder: Revenue

   measure 'YTD Sales' = ...
       displayFolder: Revenue\Time Intelligence
   ```

2. **Include descriptions** for complex measures
3. **Use consistent naming conventions** (`Total X`, `X %`, `X YTD`)

### Expression Formatting

1. **Use multi-line format** for complex DAX:
   ```tmdl
   measure 'Complex Calculation' =
           var step1 = CALCULATE(...)
           var step2 = FILTER(...)
           return
           SUMX(step2, step1)
   ```

2. **Indent consistently** within expressions
3. **Use variables** for readability

### Validation

1. **Use Tabular Editor** or **VS Code TMDL extension** for syntax highlighting
2. **Test in Power BI Desktop** after manual edits
3. **Run schema validation** before deployment

---

## References

- [Microsoft TMDL Documentation](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview)
- [Power BI PBIP Projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset)
- [Tabular Object Model (TOM)](https://learn.microsoft.com/en-us/analysis-services/tom/tom-pbi-datasets)
- [TMDL VS Code Extension](https://marketplace.visualstudio.com/items?itemName=analysis-services.TMDL)
- [Tabular Editor TMDL Support](https://docs.tabulareditor.com/)
