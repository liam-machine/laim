# Power Query M Language Reference

This document provides comprehensive reference documentation for the Power Query M language as used in Power BI PBIP projects. M is the formula language used to define data transformations and queries in Power BI semantic models.

## Table of Contents

1. [M Language in PBIP Projects](#1-m-language-in-pbip-projects)
2. [M Language Fundamentals](#2-m-language-fundamentals)
3. [Common Data Source Functions](#3-common-data-source-functions)
4. [Essential Transformation Functions](#4-essential-transformation-functions)
5. [Type Conversions](#5-type-conversions)
6. [Parameters](#6-parameters)
7. [Error Handling](#7-error-handling)
8. [Performance Best Practices](#8-performance-best-practices)
9. [TMDL Partition Examples](#9-tmdl-partition-examples)
10. [Common Patterns](#10-common-patterns)

---

## 1. M Language in PBIP Projects

### Where M Code Lives

In PBIP (Power BI Project) format, M expressions are stored in two primary locations:

#### Partition Sources in TMDL Files

Each table in the semantic model has a partition that contains the M expression defining its data source. These are stored in `.tmdl` files under `definition/tables/`:

```
ProjectName.SemanticModel/
└── definition/
    └── tables/
        ├── Sales.tmdl          # Contains partition with M expression
        ├── Products.tmdl
        └── Calendar.tmdl
```

#### Expression Files

For shared expressions, parameters, and custom functions, M code may also appear in:

```
ProjectName.SemanticModel/
└── definition/
    ├── expressions.tmdl        # Shared M expressions
    └── tables/
        └── [TableName].tmdl    # Table-specific partitions
```

### Relationship Between Power Query and Semantic Model Partitions

In Power BI's tabular model architecture:

1. **Tables** are containers for columns, measures, and relationships
2. **Partitions** define how data is loaded into tables
3. **M Expressions** in partitions specify the data source and transformations
4. **Query folding** pushes transformations to the data source when possible

When Power BI refreshes a table:
1. It evaluates the M expression in the partition
2. Query folding translates eligible operations to native queries
3. Data is retrieved and loaded into the in-memory model
4. Calculated columns and measures are computed

### How Claude Should Edit M Expressions

When editing M expressions in TMDL files:

1. **Preserve the partition structure**: The M expression is embedded within the partition definition
2. **Maintain indentation**: TMDL uses significant whitespace; M code must be properly indented
3. **Escape special characters**: Strings containing quotes need proper escaping
4. **Test with validate_tmdl**: Use MCP to validate syntax before loading in Power BI Desktop

**Example Edit Pattern:**

```tmdl
// Before: Simple table reference
partition 'Sales-partition' = m
    mode: import
    source =
        let
            Source = Sql.Database("server", "database"),
            Sales = Source{[Schema="dbo", Item="Sales"]}[Data]
        in
            Sales

// After: Adding a filter step
partition 'Sales-partition' = m
    mode: import
    source =
        let
            Source = Sql.Database("server", "database"),
            Sales = Source{[Schema="dbo", Item="Sales"]}[Data],
            FilteredRows = Table.SelectRows(Sales, each [OrderDate] >= #date(2023, 1, 1))
        in
            FilteredRows
```

---

## 2. M Language Fundamentals

### let...in Structure

Every M query follows the `let...in` pattern. The `let` block defines named steps, and `in` specifies the final output:

```powerquery-m
let
    // Step 1: Define the data source
    Source = Sql.Database("myserver.database.windows.net", "AdventureWorks"),

    // Step 2: Navigate to table
    Sales = Source{[Schema="Sales", Item="SalesOrderHeader"]}[Data],

    // Step 3: Filter rows
    FilteredRows = Table.SelectRows(Sales, each [OrderDate] >= #date(2023, 1, 1)),

    // Step 4: Select columns
    SelectedColumns = Table.SelectColumns(FilteredRows, {"SalesOrderID", "OrderDate", "TotalDue"})
in
    // Return the final step
    SelectedColumns
```

**Key Rules:**
- Each step is separated by a comma
- Step names can contain spaces if wrapped in `#"Step Name"`
- The final step before `in` has no trailing comma
- Steps are lazily evaluated - only referenced steps execute

### Record Syntax

Records are key-value collections enclosed in square brackets:

```powerquery-m
// Simple record
let
    Person = [Name = "Alice", Age = 30, City = "Seattle"]
in
    Person

// Accessing record fields
let
    Person = [Name = "Alice", Age = 30],
    PersonName = Person[Name]    // Returns "Alice"
in
    PersonName

// Nested records
let
    Employee = [
        Name = "Bob",
        Address = [
            Street = "123 Main St",
            City = "Portland",
            State = "OR"
        ]
    ],
    City = Employee[Address][City]    // Returns "Portland"
in
    City
```

### List Syntax

Lists are ordered collections enclosed in curly braces:

```powerquery-m
// Simple list
let
    Numbers = {1, 2, 3, 4, 5},
    Cities = {"New York", "Los Angeles", "Chicago"}
in
    Numbers

// List operations
let
    Numbers = {1, 2, 3, 4, 5},
    FirstItem = Numbers{0},           // Returns 1 (0-indexed)
    LastItem = List.Last(Numbers),    // Returns 5
    Count = List.Count(Numbers)       // Returns 5
in
    FirstItem

// List ranges
let
    Range = {1..10},                   // {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    EvenNumbers = {2, 4..10}          // {2, 4, 6, 8, 10}
in
    Range
```

### Table Syntax

Tables can be created using `#table` or `Table.FromRecords`:

```powerquery-m
// Using #table constructor
let
    MyTable = #table(
        type table [Name = text, Age = number, City = text],
        {
            {"Alice", 30, "Seattle"},
            {"Bob", 25, "Portland"},
            {"Carol", 35, "San Francisco"}
        }
    )
in
    MyTable

// Using Table.FromRecords
let
    MyTable = Table.FromRecords({
        [Name = "Alice", Age = 30, City = "Seattle"],
        [Name = "Bob", Age = 25, City = "Portland"],
        [Name = "Carol", Age = 35, City = "San Francisco"]
    })
in
    MyTable

// Accessing table data
let
    Source = #table({"A", "B"}, {{1, 2}, {3, 4}}),
    FirstRow = Source{0},             // Returns record [A = 1, B = 2]
    CellValue = Source{0}[A]          // Returns 1
in
    CellValue
```

### Comments

M supports both single-line and multi-line comments:

```powerquery-m
let
    // This is a single-line comment
    Source = Sql.Database("server", "database"),

    /*
       This is a multi-line comment.
       It can span multiple lines.
       Useful for documentation.
    */
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Comments can appear anywhere
    FilteredRows = Table.SelectRows(
        Sales,
        each [Status] = "Completed"  // Filter to completed orders only
    )
in
    FilteredRows
```

### The `each` Keyword

The `each` keyword is syntactic sugar for creating single-parameter functions:

```powerquery-m
// These are equivalent:
each [ColumnName]
(_) => _[ColumnName]

// Used in filtering
Table.SelectRows(Source, each [Amount] > 100)
// Is equivalent to:
Table.SelectRows(Source, (_) => _[Amount] > 100)

// Used in column generation
Table.AddColumn(Source, "NewColumn", each [Price] * [Quantity])
// Is equivalent to:
Table.AddColumn(Source, "NewColumn", (_) => _[Price] * _[Quantity])
```

---

## 3. Common Data Source Functions

### Sql.Database / Sql.Databases

Connect to SQL Server and Azure SQL databases:

```powerquery-m
// Basic connection
let
    Source = Sql.Database("myserver.database.windows.net", "AdventureWorks"),
    Sales = Source{[Schema="Sales", Item="SalesOrderHeader"]}[Data]
in
    Sales

// With optional parameters
let
    Source = Sql.Database(
        "myserver.database.windows.net",
        "AdventureWorks",
        [
            Query = "SELECT * FROM Sales.SalesOrderHeader WHERE OrderDate >= '2023-01-01'",
            CommandTimeout = #duration(0, 0, 10, 0),  // 10 minutes
            ConnectionTimeout = #duration(0, 0, 0, 30)  // 30 seconds
        ]
    )
in
    Source

// List all databases on a server
let
    Databases = Sql.Databases("myserver.database.windows.net")
in
    Databases
```

**Key Parameters for Sql.Database:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `Query` | text | Native SQL query to execute |
| `CommandTimeout` | duration | Query execution timeout |
| `ConnectionTimeout` | duration | Connection establishment timeout |
| `HierarchicalNavigation` | logical | Group tables by schema |
| `MaxDegreeOfParallelism` | number | Sets MAXDOP hint |
| `EnableCrossDatabaseFolding` | logical | Allow cross-database query folding |

### Web.Contents / Web.Page

Fetch data from web URLs and APIs:

```powerquery-m
// Simple GET request
let
    Source = Web.Contents("https://api.example.com/data"),
    JsonResponse = Json.Document(Source)
in
    JsonResponse

// With headers and query parameters
let
    Source = Web.Contents(
        "https://api.example.com/data",
        [
            Headers = [
                #"Authorization" = "Bearer " & AccessToken,
                #"Content-Type" = "application/json"
            ],
            Query = [
                page = "1",
                pageSize = "100"
            ],
            RelativePath = "orders",
            ManualStatusHandling = {400, 404, 500}
        ]
    ),
    JsonResponse = Json.Document(Source)
in
    JsonResponse

// POST request with body
let
    Source = Web.Contents(
        "https://api.example.com/data",
        [
            Headers = [#"Content-Type" = "application/json"],
            Content = Json.FromValue([query = "SELECT * FROM users"])
        ]
    ),
    JsonResponse = Json.Document(Source)
in
    JsonResponse

// Parse HTML page
let
    Source = Web.Page(Web.Contents("https://example.com/table-page")),
    DataTable = Source{0}[Data]  // First table on the page
in
    DataTable
```

### Excel.Workbook

Read Excel files:

```powerquery-m
// From local file path
let
    Source = Excel.Workbook(File.Contents("C:\Data\Sales.xlsx"), null, true),
    SalesSheet = Source{[Item="Sales", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(SalesSheet, [PromoteAllScalars=true])
in
    PromotedHeaders

// From SharePoint
let
    Source = Excel.Workbook(
        Web.Contents("https://company.sharepoint.com/sites/data/Shared Documents/Sales.xlsx"),
        null,
        true
    ),
    SalesSheet = Source{[Item="Sales", Kind="Sheet"]}[Data]
in
    SalesSheet

// Accessing named ranges
let
    Source = Excel.Workbook(File.Contents("C:\Data\Report.xlsx"), null, true),
    NamedRange = Source{[Item="SalesData", Kind="DefinedName"]}[Data]
in
    NamedRange
```

### Csv.Document

Parse CSV content:

```powerquery-m
// From file
let
    Source = Csv.Document(
        File.Contents("C:\Data\sales.csv"),
        [
            Delimiter = ",",
            Encoding = 65001,  // UTF-8
            QuoteStyle = QuoteStyle.None
        ]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    PromotedHeaders

// With custom options
let
    Source = Csv.Document(
        File.Contents("C:\Data\european_data.csv"),
        [
            Delimiter = ";",           // European CSV often uses semicolon
            Encoding = 1252,           // Windows-1252
            QuoteStyle = QuoteStyle.Csv,
            Columns = 5,               // Expected column count
            CultureInfo = "de-DE"      // German locale
        ]
    )
in
    Source
```

### SharePoint.Files / SharePoint.Contents

Access SharePoint document libraries:

```powerquery-m
// List all files in a SharePoint site
let
    Source = SharePoint.Files(
        "https://company.sharepoint.com/sites/DataTeam",
        [ApiVersion = 15]
    ),
    FilteredFiles = Table.SelectRows(Source, each Text.EndsWith([Name], ".xlsx"))
in
    FilteredFiles

// Get specific folder contents
let
    Source = SharePoint.Contents(
        "https://company.sharepoint.com/sites/DataTeam",
        [ApiVersion = 15]
    ),
    Reports = Source{[Name="Reports"]}[Content],
    MonthlyReports = Reports{[Name="Monthly"]}[Content]
in
    MonthlyReports

// Combine all Excel files from SharePoint folder
let
    Source = SharePoint.Files("https://company.sharepoint.com/sites/Sales", [ApiVersion = 15]),
    FilteredFiles = Table.SelectRows(Source, each
        Text.Contains([Folder Path], "/Reports/") and
        Text.EndsWith([Name], ".xlsx")
    ),
    AddedContent = Table.AddColumn(FilteredFiles, "Tables", each
        Excel.Workbook([Content], true, true){[Item="Data", Kind="Sheet"]}[Data]
    ),
    ExpandedTables = Table.ExpandTableColumn(AddedContent, "Tables",
        Table.ColumnNames(AddedContent{0}[Tables]))
in
    ExpandedTables
```

### Folder.Files / Folder.Contents

Access local file system folders:

```powerquery-m
// List all files in a folder
let
    Source = Folder.Files("C:\Data\Reports"),
    CsvFiles = Table.SelectRows(Source, each [Extension] = ".csv")
in
    CsvFiles

// Combine multiple CSV files
let
    Source = Folder.Files("C:\Data\Monthly"),
    FilteredFiles = Table.SelectRows(Source, each [Extension] = ".csv"),
    AddedContent = Table.AddColumn(FilteredFiles, "Data", each
        Csv.Document([Content], [Delimiter=",", Encoding=65001])
    ),
    PromotedHeaders = Table.TransformColumns(AddedContent,
        {"Data", each Table.PromoteHeaders(_, [PromoteAllScalars=true])}
    ),
    ExpandedData = Table.ExpandTableColumn(PromotedHeaders, "Data",
        Table.ColumnNames(PromotedHeaders{0}[Data]))
in
    ExpandedData
```

### OData.Feed

Connect to OData services:

```powerquery-m
// Basic OData connection
let
    Source = OData.Feed("https://services.odata.org/V4/Northwind/Northwind.svc/"),
    Orders = Source{[Name="Orders", Signature="table"]}[Data]
in
    Orders

// With authentication and options
let
    Source = OData.Feed(
        "https://api.example.com/odata/v4/",
        null,
        [
            Headers = [Authorization = "Bearer " & Token],
            Query = [
                #"$filter" = "CreatedDate ge 2023-01-01",
                #"$select" = "Id,Name,Amount",
                #"$top" = "1000"
            ],
            ODataVersion = 4,
            MoreColumns = true
        ]
    )
in
    Source
```

### AzureStorage.Blobs

Access Azure Blob Storage:

```powerquery-m
// List blobs in a container
let
    Source = AzureStorage.Blobs("https://mystorageaccount.blob.core.windows.net/mycontainer"),
    CsvBlobs = Table.SelectRows(Source, each Text.EndsWith([Name], ".csv"))
in
    CsvBlobs

// Read specific blob content
let
    Source = AzureStorage.Blobs("https://mystorageaccount.blob.core.windows.net/data"),
    SalesBlob = Source{[Name="sales/2023/monthly.csv"]}[Content],
    CsvData = Csv.Document(SalesBlob, [Delimiter=",", Encoding=65001]),
    PromotedHeaders = Table.PromoteHeaders(CsvData, [PromoteAllScalars=true])
in
    PromotedHeaders
```

### Databricks.Catalogs

Connect to Databricks Unity Catalog (for Databricks users):

```powerquery-m
// Connect to Databricks workspace
let
    Source = Databricks.Catalogs(
        "adb-1234567890123456.7.azuredatabricks.net",
        "/sql/1.0/warehouses/abcdef123456",
        [
            Catalog = "main",
            Database = "sales"
        ]
    ),
    SalesTable = Source{[Name="fact_sales"]}[Data]
in
    SalesTable

// With SQL passthrough
let
    Source = Databricks.Catalogs(
        "adb-1234567890123456.7.azuredatabricks.net",
        "/sql/1.0/warehouses/abcdef123456",
        [
            Catalog = "main",
            Database = "analytics",
            Query = "SELECT * FROM fact_orders WHERE order_date >= '2023-01-01'"
        ]
    )
in
    Source
```

---

## 4. Essential Transformation Functions

### Table.SelectColumns / Table.RemoveColumns

Select or remove columns from a table:

```powerquery-m
// Select specific columns
let
    Source = SalesTable,
    SelectedColumns = Table.SelectColumns(Source, {"OrderID", "OrderDate", "Amount"})
in
    SelectedColumns

// Select columns with error handling for missing columns
let
    Source = SalesTable,
    SelectedColumns = Table.SelectColumns(
        Source,
        {"OrderID", "OrderDate", "Amount"},
        MissingField.Ignore  // or MissingField.UseNull, MissingField.Error
    )
in
    SelectedColumns

// Remove specific columns
let
    Source = SalesTable,
    RemovedColumns = Table.RemoveColumns(Source, {"TempColumn", "CalculatedField"})
in
    RemovedColumns

// Keep only certain columns by removing others
let
    Source = SalesTable,
    ColumnsToRemove = List.RemoveItems(Table.ColumnNames(Source), {"OrderID", "Amount"}),
    Result = Table.RemoveColumns(Source, ColumnsToRemove)
in
    Result
```

### Table.SelectRows (Filtering)

Filter rows based on conditions:

```powerquery-m
// Simple filter
let
    Source = SalesTable,
    FilteredRows = Table.SelectRows(Source, each [Amount] > 1000)
in
    FilteredRows

// Multiple conditions with AND
let
    Source = SalesTable,
    FilteredRows = Table.SelectRows(Source, each
        [Amount] > 1000 and
        [Status] = "Completed" and
        [OrderDate] >= #date(2023, 1, 1)
    )
in
    FilteredRows

// Multiple conditions with OR
let
    Source = SalesTable,
    FilteredRows = Table.SelectRows(Source, each
        [Category] = "Electronics" or [Category] = "Computers"
    )
in
    FilteredRows

// Using List.Contains for IN-style filtering
let
    Source = SalesTable,
    AllowedCategories = {"Electronics", "Computers", "Software"},
    FilteredRows = Table.SelectRows(Source, each
        List.Contains(AllowedCategories, [Category])
    )
in
    FilteredRows

// Text filtering
let
    Source = CustomerTable,
    FilteredRows = Table.SelectRows(Source, each
        Text.Contains([Name], "Corp", Comparer.OrdinalIgnoreCase)
    )
in
    FilteredRows

// Date filtering
let
    Source = SalesTable,
    FilteredRows = Table.SelectRows(Source, each
        [OrderDate] >= Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -12)
    )
in
    FilteredRows

// Null handling in filters
let
    Source = SalesTable,
    NonNullRows = Table.SelectRows(Source, each [Amount] <> null and [Amount] > 0)
in
    NonNullRows
```

### Table.AddColumn

Add calculated columns:

```powerquery-m
// Simple calculated column
let
    Source = SalesTable,
    AddedColumn = Table.AddColumn(Source, "TotalWithTax", each [Amount] * 1.1)
in
    AddedColumn

// With explicit type
let
    Source = SalesTable,
    AddedColumn = Table.AddColumn(
        Source,
        "TotalWithTax",
        each [Amount] * 1.1,
        type number
    )
in
    AddedColumn

// Conditional column
let
    Source = SalesTable,
    AddedColumn = Table.AddColumn(Source, "SizeCategory", each
        if [Amount] >= 10000 then "Large"
        else if [Amount] >= 1000 then "Medium"
        else "Small",
        type text
    )
in
    AddedColumn

// Column based on other columns
let
    Source = OrderDetails,
    AddedColumn = Table.AddColumn(Source, "LineTotal", each
        [Quantity] * [UnitPrice] * (1 - [Discount]),
        type number
    )
in
    AddedColumn

// Using functions in calculated columns
let
    Source = CustomerTable,
    AddedColumn = Table.AddColumn(Source, "YearsSinceJoined", each
        Duration.TotalDays(DateTime.LocalNow() - [JoinDate]) / 365,
        type number
    )
in
    AddedColumn
```

### Table.TransformColumns / Table.TransformColumnTypes

Transform column values and types:

```powerquery-m
// Transform column values
let
    Source = CustomerTable,
    TransformedColumns = Table.TransformColumns(Source, {
        {"Name", Text.Upper},
        {"Email", Text.Lower},
        {"Phone", each Text.Replace(_, "-", "")}
    })
in
    TransformedColumns

// Transform with type preservation
let
    Source = SalesTable,
    TransformedColumns = Table.TransformColumns(Source, {
        {"Amount", each _ * 1.1, type number}
    })
in
    TransformedColumns

// Change column types
let
    Source = ImportedData,
    TypedColumns = Table.TransformColumnTypes(Source, {
        {"OrderDate", type date},
        {"Amount", type number},
        {"OrderID", Int64.Type},
        {"CustomerName", type text},
        {"IsActive", type logical}
    })
in
    TypedColumns

// Change types with culture
let
    Source = EuropeanData,
    TypedColumns = Table.TransformColumnTypes(
        Source,
        {{"Amount", type number}, {"OrderDate", type date}},
        "de-DE"  // German culture for number/date parsing
    )
in
    TypedColumns
```

### Table.RenameColumns

Rename columns:

```powerquery-m
// Rename specific columns
let
    Source = SalesTable,
    RenamedColumns = Table.RenameColumns(Source, {
        {"OrderID", "Order ID"},
        {"CustName", "Customer Name"},
        {"Amt", "Amount"}
    })
in
    RenamedColumns

// Rename with error handling
let
    Source = SalesTable,
    RenamedColumns = Table.RenameColumns(
        Source,
        {{"OldName", "NewName"}},
        MissingField.Ignore
    )
in
    RenamedColumns

// Dynamic rename (prefix all columns)
let
    Source = SalesTable,
    ColumnNames = Table.ColumnNames(Source),
    RenameList = List.Transform(ColumnNames, each {_, "Sales_" & _}),
    RenamedColumns = Table.RenameColumns(Source, RenameList)
in
    RenamedColumns
```

### Table.Group (Aggregation)

Group and aggregate data:

```powerquery-m
// Basic grouping with single aggregation
let
    Source = SalesTable,
    GroupedRows = Table.Group(
        Source,
        {"Category"},
        {{"TotalSales", each List.Sum([Amount]), type number}}
    )
in
    GroupedRows

// Multiple aggregations
let
    Source = SalesTable,
    GroupedRows = Table.Group(
        Source,
        {"Category", "Year"},
        {
            {"TotalSales", each List.Sum([Amount]), type number},
            {"OrderCount", each Table.RowCount(_), Int64.Type},
            {"AvgOrderValue", each List.Average([Amount]), type number},
            {"MinOrder", each List.Min([Amount]), type number},
            {"MaxOrder", each List.Max([Amount]), type number}
        }
    )
in
    GroupedRows

// Distinct count
let
    Source = SalesTable,
    GroupedRows = Table.Group(
        Source,
        {"Category"},
        {
            {"UniqueCustomers", each List.Count(List.Distinct([CustomerID])), Int64.Type}
        }
    )
in
    GroupedRows

// Keep first/last row per group
let
    Source = SalesTable,
    GroupedRows = Table.Group(
        Source,
        {"CustomerID"},
        {
            {"FirstOrder", each Table.First(Table.Sort(_, {"OrderDate", Order.Ascending})), type record},
            {"LastOrder", each Table.Last(Table.Sort(_, {"OrderDate", Order.Ascending})), type record}
        }
    )
in
    GroupedRows

// Group with all rows (for expansion later)
let
    Source = SalesTable,
    GroupedRows = Table.Group(
        Source,
        {"Category"},
        {{"AllData", each _, type table}}
    )
in
    GroupedRows
```

### Table.Join / Table.NestedJoin

Join tables together:

```powerquery-m
// Inner join with Table.NestedJoin
let
    Sales = SalesTable,
    Products = ProductTable,
    JoinedTable = Table.NestedJoin(
        Sales,
        {"ProductID"},
        Products,
        {"ProductID"},
        "ProductDetails",
        JoinKind.Inner
    ),
    ExpandedTable = Table.ExpandTableColumn(
        JoinedTable,
        "ProductDetails",
        {"ProductName", "Category"}
    )
in
    ExpandedTable

// Left outer join (keep all sales, add product info where available)
let
    Sales = SalesTable,
    Products = ProductTable,
    JoinedTable = Table.NestedJoin(
        Sales,
        {"ProductID"},
        Products,
        {"ProductID"},
        "ProductDetails",
        JoinKind.LeftOuter
    ),
    ExpandedTable = Table.ExpandTableColumn(
        JoinedTable,
        "ProductDetails",
        {"ProductName", "Category"}
    )
in
    ExpandedTable

// Join on multiple columns
let
    Sales = SalesTable,
    Regions = RegionTable,
    JoinedTable = Table.NestedJoin(
        Sales,
        {"Country", "State"},
        Regions,
        {"CountryCode", "StateCode"},
        "RegionInfo",
        JoinKind.LeftOuter
    )
in
    JoinedTable

// All join types
// JoinKind.Inner        - Only matching rows
// JoinKind.LeftOuter    - All left rows, matching right rows
// JoinKind.RightOuter   - All right rows, matching left rows
// JoinKind.FullOuter    - All rows from both tables
// JoinKind.LeftAnti     - Left rows with no match in right
// JoinKind.RightAnti    - Right rows with no match in left

// Flat join (Table.Join) - use when you don't need nested expansion
let
    Result = Table.Join(
        Table1, {"Key"},
        Table2, {"Key"},
        JoinKind.Inner
    )
in
    Result
```

### Table.Pivot / Table.Unpivot

Transform between wide and long formats:

```powerquery-m
// Unpivot columns (wide to long)
let
    Source = #table(
        {"Product", "Jan", "Feb", "Mar"},
        {
            {"Widget A", 100, 150, 200},
            {"Widget B", 80, 90, 110}
        }
    ),
    UnpivotedTable = Table.Unpivot(
        Source,
        {"Jan", "Feb", "Mar"},
        "Month",
        "Sales"
    )
in
    UnpivotedTable
// Result: Product, Month, Sales columns

// Unpivot other columns (more dynamic)
let
    Source = SalesWideFormat,
    UnpivotedTable = Table.UnpivotOtherColumns(
        Source,
        {"Product", "Category"},  // Keep these columns
        "Month",                   // New attribute column
        "Sales"                    // New value column
    )
in
    UnpivotedTable

// Pivot (long to wide)
let
    Source = SalesLongFormat,
    PivotedTable = Table.Pivot(
        Source,
        List.Distinct(Source[Month]),  // Column values to pivot
        "Month",                        // Column containing pivot values
        "Sales",                        // Column containing values
        List.Sum                        // Aggregation function
    )
in
    PivotedTable
```

### Table.Sort

Sort table rows:

```powerquery-m
// Single column sort (ascending)
let
    Source = SalesTable,
    SortedTable = Table.Sort(Source, {{"OrderDate", Order.Ascending}})
in
    SortedTable

// Multiple column sort
let
    Source = SalesTable,
    SortedTable = Table.Sort(Source, {
        {"Category", Order.Ascending},
        {"Amount", Order.Descending}
    })
in
    SortedTable

// Sort by calculated value
let
    Source = SalesTable,
    SortedTable = Table.Sort(Source, {
        {each [Quantity] * [UnitPrice], Order.Descending}
    })
in
    SortedTable
```

### Table.Distinct / Table.DistinctRows

Remove duplicate rows:

```powerquery-m
// Remove exact duplicate rows
let
    Source = SalesTable,
    UniqueRows = Table.Distinct(Source)
in
    UniqueRows

// Remove duplicates based on specific columns
let
    Source = SalesTable,
    UniqueRows = Table.Distinct(Source, {"CustomerID", "ProductID"})
in
    UniqueRows

// Keep first occurrence of each distinct combination
let
    Source = Table.Sort(SalesTable, {{"OrderDate", Order.Ascending}}),
    UniqueRows = Table.Distinct(Source, {"CustomerID"})
in
    UniqueRows
```

### Table.ExpandRecordColumn / Table.ExpandTableColumn

Expand nested data structures:

```powerquery-m
// Expand record column
let
    Source = TableWithRecordColumn,
    ExpandedTable = Table.ExpandRecordColumn(
        Source,
        "AddressRecord",
        {"Street", "City", "State", "Zip"},
        {"Address_Street", "Address_City", "Address_State", "Address_Zip"}
    )
in
    ExpandedTable

// Expand table column (from nested join)
let
    Source = JoinedTableWithNestedTables,
    ExpandedTable = Table.ExpandTableColumn(
        Source,
        "NestedTable",
        {"Column1", "Column2", "Column3"}
    )
in
    ExpandedTable

// Dynamic expansion (all columns)
let
    Source = TableWithRecordColumn,
    SampleRecord = Source{0}[RecordColumn],
    FieldNames = Record.FieldNames(SampleRecord),
    ExpandedTable = Table.ExpandRecordColumn(Source, "RecordColumn", FieldNames)
in
    ExpandedTable

// Expand list column
let
    Source = TableWithListColumn,
    ExpandedTable = Table.ExpandListColumn(Source, "ListColumn")
in
    ExpandedTable
```

---

## 5. Type Conversions

### Conversion Functions

```powerquery-m
// Number conversions
let
    TextToNumber = Number.From("123.45"),           // 123.45
    TextToInt = Int64.From("123"),                  // 123
    RoundedNumber = Number.Round(123.456, 2),       // 123.46
    IntegerPart = Number.IntegerDivide(10, 3)       // 3
in
    TextToNumber

// Text conversions
let
    NumberToText = Text.From(123.45),               // "123.45"
    DateToText = Text.From(#date(2023, 6, 15)),     // "6/15/2023"
    FormattedNumber = Number.ToText(1234.5, "N2"),  // "1,234.50"
    FormattedDate = Date.ToText(#date(2023, 6, 15), "yyyy-MM-dd")  // "2023-06-15"
in
    NumberToText

// Date conversions
let
    TextToDate = Date.From("2023-06-15"),           // #date(2023, 6, 15)
    NumberToDate = Date.From(45092),                // Excel serial date
    DateTimeToDate = Date.From(#datetime(2023, 6, 15, 10, 30, 0))  // #date(2023, 6, 15)
in
    TextToDate

// DateTime conversions
let
    TextToDateTime = DateTime.From("2023-06-15 10:30:00"),
    DateToDateTime = DateTime.From(#date(2023, 6, 15)),
    CombineDateTime = #datetime(
        Date.Year(#date(2023, 6, 15)),
        Date.Month(#date(2023, 6, 15)),
        Date.Day(#date(2023, 6, 15)),
        10, 30, 0
    )
in
    TextToDateTime

// Logical conversions
let
    TextToLogical = Logical.From("true"),           // true
    NumberToLogical = Logical.From(1),              // true (0 = false)
    Comparison = 5 > 3                              // true
in
    TextToLogical
```

### Type Declarations in Table.TransformColumnTypes

```powerquery-m
let
    Source = ImportedData,
    TypedTable = Table.TransformColumnTypes(Source, {
        // Basic types
        {"ID", Int64.Type},                    // Whole number
        {"Amount", type number},               // Decimal number
        {"Price", Currency.Type},              // Currency
        {"Rate", Percentage.Type},             // Percentage
        {"Name", type text},                   // Text
        {"IsActive", type logical},            // True/False

        // Date/Time types
        {"OrderDate", type date},              // Date only
        {"CreatedAt", type datetime},          // Date and time
        {"ModifiedTime", type time},           // Time only
        {"Duration", type duration},           // Duration
        {"ZonedTime", type datetimezone},      // DateTime with timezone

        // Binary type
        {"FileContent", type binary}           // Binary data
    })
in
    TypedTable

// Type table for reference
/*
Type Name           | M Type              | Description
--------------------|---------------------|------------------------
Whole Number        | Int64.Type          | 64-bit integer
Decimal Number      | type number         | Double precision float
Currency            | Currency.Type       | Fixed decimal (4 places)
Percentage          | Percentage.Type     | Decimal displayed as %
Text                | type text           | Unicode string
True/False          | type logical        | Boolean
Date                | type date           | Date without time
Time                | type time           | Time without date
DateTime            | type datetime       | Date and time
DateTimeZone        | type datetimezone   | DateTime with timezone
Duration            | type duration       | Time span
Binary              | type binary         | Raw bytes
*/
```

---

## 6. Parameters

### Defining Parameters in M

Parameters can be defined in several ways in Power BI:

```powerquery-m
// Simple parameter definition (in expressions.tmdl or as separate query)
"myserver.database.windows.net" meta [
    IsParameterQuery = true,
    Type = "Text",
    IsParameterQueryRequired = true
]

// Parameter with allowed values
"Production" meta [
    IsParameterQuery = true,
    Type = "Text",
    IsParameterQueryRequired = true,
    List = {"Development", "Staging", "Production"}
]

// Numeric parameter with range
1000 meta [
    IsParameterQuery = true,
    Type = "Number",
    IsParameterQueryRequired = true,
    MinValue = 100,
    MaxValue = 10000
]

// Date parameter
#date(2023, 1, 1) meta [
    IsParameterQuery = true,
    Type = "Date",
    IsParameterQueryRequired = true
]
```

### Using Parameters in Data Source Connections

```powerquery-m
// SQL Server with parameterized server and database
let
    Source = Sql.Database(ServerName, DatabaseName),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data]
in
    Sales

// Parameterized file path
let
    Source = Csv.Document(
        File.Contents(FolderPath & "\sales_" & FileName & ".csv"),
        [Delimiter=",", Encoding=65001]
    )
in
    Source

// API with environment-specific base URL
let
    BaseUrl = if Environment = "Production"
              then "https://api.company.com"
              else "https://api-staging.company.com",
    Source = Web.Contents(BaseUrl & "/v1/orders"),
    Response = Json.Document(Source)
in
    Response
```

### Environment-Specific Configurations

```powerquery-m
// Configuration table approach
let
    // Define environment configurations
    Environments = #table(
        {"Environment", "Server", "Database", "Schema"},
        {
            {"Development", "dev-server", "DevDB", "dev"},
            {"Staging", "staging-server", "StagingDB", "stg"},
            {"Production", "prod-server", "ProdDB", "dbo"}
        }
    ),

    // Get current environment config
    CurrentEnv = Environments{[Environment = EnvironmentParameter]},

    // Use configuration
    Source = Sql.Database(CurrentEnv[Server], CurrentEnv[Database]),
    Data = Source{[Schema = CurrentEnv[Schema], Item = "Sales"]}[Data]
in
    Data

// Conditional logic approach
let
    ServerName = if Environment = "Production"
                 then "prodserver.database.windows.net"
                 else if Environment = "Staging"
                 then "stagingserver.database.windows.net"
                 else "devserver.database.windows.net",

    DatabaseName = if Environment = "Production"
                   then "ProdDB"
                   else "TestDB",

    Source = Sql.Database(ServerName, DatabaseName)
in
    Source
```

---

## 7. Error Handling

### try...otherwise

Handle errors gracefully:

```powerquery-m
// Basic error handling
let
    Source = SalesTable,
    SafeDivision = Table.AddColumn(Source, "Margin", each
        try [Profit] / [Revenue] otherwise 0
    )
in
    SafeDivision

// With specific error replacement
let
    Result = try Number.FromText("not a number") otherwise null
in
    Result

// Capture error details with try (without otherwise)
let
    Result = try Number.FromText("not a number"),
    // Result is a record: [HasError=true, Error=[Reason="...", Message="...", Detail="..."]]
    Value = if Result[HasError] then null else Result[Value]
in
    Value

// Using catch keyword (newer syntax)
let
    Result = try Number.FromText("not a number") catch () => 0
in
    Result

// Catch with error details
let
    Result = try Number.FromText("invalid") catch (e) =>
        if e[Message] = "We couldn't convert to Number."
        then -1
        else error e
in
    Result
```

### Handling Nulls

```powerquery-m
// Check for null
let
    Source = SalesTable,
    FilteredRows = Table.SelectRows(Source, each [Amount] <> null)
in
    FilteredRows

// Replace nulls
let
    Source = SalesTable,
    ReplacedNulls = Table.ReplaceValue(
        Source,
        null,
        0,
        Replacer.ReplaceValue,
        {"Amount"}
    )
in
    ReplacedNulls

// Coalesce (use first non-null value)
let
    Source = SalesTable,
    CoalescedColumn = Table.AddColumn(Source, "DisplayName", each
        [PreferredName] ?? [FirstName] ?? "Unknown"
    )
in
    CoalescedColumn

// Handle nulls in calculations
let
    Source = SalesTable,
    SafeCalculation = Table.AddColumn(Source, "PerUnit", each
        if [Quantity] = null or [Quantity] = 0
        then null
        else [Amount] / [Quantity]
    )
in
    SafeCalculation
```

### Error Records

```powerquery-m
// Access error details
let
    TestResult = try SomeRiskyOperation(),
    Output = if TestResult[HasError] then
        [
            WasError = true,
            Reason = TestResult[Error][Reason],
            Message = TestResult[Error][Message],
            Detail = TestResult[Error][Detail]
        ]
    else
        [WasError = false, Value = TestResult[Value]]
in
    Output

// Raise custom errors
let
    ValidateInput = (value as number) =>
        if value < 0 then
            error Error.Record(
                "InvalidArgument",
                "Value must be non-negative",
                [Provided = value]
            )
        else
            value,

    Result = ValidateInput(-5)
in
    Result

// Try multiple operations
let
    TryPrimarySource = try Sql.Database("primary-server", "DB"),
    TryBackupSource = try Sql.Database("backup-server", "DB"),

    Source = if not TryPrimarySource[HasError]
             then TryPrimarySource[Value]
             else if not TryBackupSource[HasError]
             then TryBackupSource[Value]
             else error "All data sources unavailable"
in
    Source
```

---

## 8. Performance Best Practices

### Query Folding

Query folding translates M transformations into native data source queries (like SQL). This is critical for performance.

**What is Query Folding?**
- Power Query sends transformation logic to the data source
- Data source executes the transformation natively
- Only the final result is returned to Power BI
- Dramatically reduces data transfer and memory usage

**How to Check Query Folding:**
- Right-click a step in Power Query Editor
- Select "View Native Query"
- If grayed out, folding has stopped at that step

**Operations That Typically Fold:**
```powerquery-m
// These operations usually fold to SQL
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Folds: WHERE OrderDate >= '2023-01-01'
    FilteredRows = Table.SelectRows(Sales, each [OrderDate] >= #date(2023, 1, 1)),

    // Folds: SELECT OrderID, CustomerID, Amount
    SelectedColumns = Table.SelectColumns(FilteredRows, {"OrderID", "CustomerID", "Amount"}),

    // Folds: ORDER BY Amount DESC
    SortedRows = Table.Sort(SelectedColumns, {{"Amount", Order.Descending}}),

    // Folds: TOP 1000
    TopRows = Table.FirstN(SortedRows, 1000)
in
    TopRows
```

**Operations That Break Folding:**
```powerquery-m
// These operations typically prevent folding
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // BREAKS FOLDING: Custom M function
    AddedColumn = Table.AddColumn(Sales, "Custom", each
        Text.Combine({[FirstName], " ", [LastName]})
    ),

    // BREAKS FOLDING: Table.Buffer
    BufferedTable = Table.Buffer(Sales),

    // BREAKS FOLDING: Complex M expressions
    ComplexFilter = Table.SelectRows(Sales, each
        List.Contains(MyLocalList, [Category])
    )
in
    AddedColumn
```

**Preserving Query Folding:**
```powerquery-m
// DO: Put foldable operations first
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Step 1: Foldable filter (runs on SQL Server)
    FilteredRows = Table.SelectRows(Sales, each [Amount] > 1000),

    // Step 2: Foldable column selection (runs on SQL Server)
    SelectedColumns = Table.SelectColumns(FilteredRows, {"OrderID", "Amount", "CustomerID"}),

    // Step 3: Non-foldable transformation (runs locally on smaller dataset)
    AddedColumn = Table.AddColumn(SelectedColumns, "Category", each
        if [Amount] > 5000 then "Large" else "Small"
    )
in
    AddedColumn

// DON'T: Put non-foldable operations early
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // This breaks folding early - all data loaded to memory!
    AddedColumn = Table.AddColumn(Sales, "Category", each
        if [Amount] > 5000 then "Large" else "Small"
    ),

    // This filter runs locally on ALL data
    FilteredRows = Table.SelectRows(AddedColumn, each [Category] = "Large")
in
    FilteredRows
```

### Avoiding Table.Buffer

`Table.Buffer` loads the entire table into memory. Use sparingly:

```powerquery-m
// AVOID: Unnecessary buffering
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],
    BufferedSales = Table.Buffer(Sales)  // Loads ALL data to memory!
in
    BufferedSales

// ACCEPTABLE: Buffer when joining same source multiple times
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Buffer if used in multiple joins to avoid multiple queries
    BufferedSales = Table.Buffer(Table.SelectRows(Sales, each [Year] = 2023)),

    Summary1 = Table.Group(BufferedSales, {"Region"}, {{"Total", each List.Sum([Amount])}}),
    Summary2 = Table.Group(BufferedSales, {"Product"}, {{"Total", each List.Sum([Amount])}})
in
    {Summary1, Summary2}
```

### Native Query Usage

Use native queries for complex operations:

```powerquery-m
// Native SQL for complex transformations
let
    Source = Sql.Database(
        "server",
        "database",
        [
            Query = "
                SELECT
                    s.OrderID,
                    s.OrderDate,
                    c.CustomerName,
                    SUM(d.Quantity * d.UnitPrice) as TotalAmount
                FROM Sales.Orders s
                INNER JOIN Sales.Customers c ON s.CustomerID = c.CustomerID
                INNER JOIN Sales.OrderDetails d ON s.OrderID = d.OrderID
                WHERE s.OrderDate >= '2023-01-01'
                GROUP BY s.OrderID, s.OrderDate, c.CustomerName
            "
        ]
    )
in
    Source

// Value.NativeQuery for parameterized native queries
let
    Source = Sql.Database("server", "database"),
    NativeQuery = Value.NativeQuery(
        Source,
        "SELECT * FROM Sales WHERE OrderDate >= @StartDate",
        [StartDate = #date(2023, 1, 1)]
    )
in
    NativeQuery
```

### Incremental Refresh Considerations

```powerquery-m
// Pattern for incremental refresh
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // RangeStart and RangeEnd are special parameters for incremental refresh
    // They must be defined as Date/DateTime parameters
    FilteredRows = Table.SelectRows(Sales, each
        [OrderDate] >= RangeStart and [OrderDate] < RangeEnd
    )
in
    FilteredRows
```

**Important Rules for Incremental Refresh:**
- Parameter names must be exactly `RangeStart` and `RangeEnd` (case-sensitive)
- Parameters must be Date or DateTime type
- Filter must use `>=` on RangeStart and `<` on RangeEnd (or vice versa)
- The filter operation must fold to the data source
- Only one of the operators should include equals (to avoid duplicates)

---

## 9. TMDL Partition Examples

### Basic Table with M Partition

```tmdl
table Sales
    lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890

    column OrderID
        dataType: int64
        formatString: 0
        lineageTag: b2c3d4e5-f6a7-8901-bcde-f12345678901
        summarizeBy: none
        sourceColumn: OrderID

    column OrderDate
        dataType: dateTime
        formatString: Short Date
        lineageTag: c3d4e5f6-a7b8-9012-cdef-123456789012
        summarizeBy: none
        sourceColumn: OrderDate

    column Amount
        dataType: decimal
        formatString: "$#,##0.00"
        lineageTag: d4e5f6a7-b8c9-0123-defa-234567890123
        summarizeBy: sum
        sourceColumn: Amount

    measure 'Total Sales' = SUM(Sales[Amount])
        formatString: "$#,##0.00"
        displayFolder: Metrics
        lineageTag: e5f6a7b8-c9d0-1234-efab-345678901234

    partition 'Sales-partition' = m
        mode: import
        source =
            let
                Source = Sql.Database("myserver.database.windows.net", "AdventureWorks"),
                Sales_Data = Source{[Schema="Sales", Item="SalesOrderHeader"]}[Data],
                FilteredRows = Table.SelectRows(Sales_Data, each [OrderDate] >= #date(2023, 1, 1)),
                SelectedColumns = Table.SelectColumns(FilteredRows, {"SalesOrderID", "OrderDate", "TotalDue"}),
                RenamedColumns = Table.RenameColumns(SelectedColumns, {
                    {"SalesOrderID", "OrderID"},
                    {"TotalDue", "Amount"}
                })
            in
                RenamedColumns
```

### Partition with Parameters

```tmdl
expression ServerName =
    "myserver.database.windows.net" meta [
        IsParameterQuery = true,
        Type = "Text",
        IsParameterQueryRequired = true
    ]
    lineageTag: f6a7b8c9-d0e1-2345-fabc-456789012345

expression DatabaseName =
    "AdventureWorks" meta [
        IsParameterQuery = true,
        Type = "Text",
        IsParameterQueryRequired = true
    ]
    lineageTag: a7b8c9d0-e1f2-3456-abcd-567890123456

table Sales
    lineageTag: b8c9d0e1-f2a3-4567-bcde-678901234567

    // ... columns ...

    partition 'Sales-partition' = m
        mode: import
        source =
            let
                Source = Sql.Database(ServerName, DatabaseName),
                Sales = Source{[Schema="dbo", Item="Sales"]}[Data]
            in
                Sales
```

### Incremental Refresh Partition

```tmdl
expression RangeStart =
    #datetime(2023, 1, 1, 0, 0, 0) meta [
        IsParameterQuery = true,
        Type = "DateTime",
        IsParameterQueryRequired = true
    ]
    lineageTag: c9d0e1f2-a3b4-5678-cdef-789012345678

expression RangeEnd =
    #datetime(2024, 1, 1, 0, 0, 0) meta [
        IsParameterQuery = true,
        Type = "DateTime",
        IsParameterQueryRequired = true
    ]
    lineageTag: d0e1f2a3-b4c5-6789-defa-890123456789

table FactSales
    lineageTag: e1f2a3b4-c5d6-7890-efab-901234567890

    column OrderDate
        dataType: dateTime
        formatString: Short Date
        lineageTag: f2a3b4c5-d6e7-8901-fabc-012345678901
        summarizeBy: none
        sourceColumn: OrderDate
        isAvailableInMDX: false

    partition 'FactSales-partition' = m
        mode: import
        source =
            let
                Source = Sql.Database("server", "database"),
                FactSales = Source{[Schema="dbo", Item="FactSales"]}[Data],
                // Incremental refresh filter - note the boundary operators
                IncrementalFilter = Table.SelectRows(FactSales, each
                    [OrderDate] >= RangeStart and [OrderDate] < RangeEnd
                )
            in
                IncrementalFilter
```

### DirectQuery Partition

```tmdl
table LiveSales
    lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890

    // ... columns ...

    partition 'LiveSales-partition' = m
        mode: directQuery
        source =
            let
                Source = Sql.Database("server", "database"),
                LiveSales = Source{[Schema="dbo", Item="LiveSalesView"]}[Data]
            in
                LiveSales
```

---

## 10. Common Patterns

### Parameterized Database Connection

```powerquery-m
// Reusable connection pattern
let
    // Parameters (defined elsewhere)
    // ServerName = "myserver.database.windows.net"
    // DatabaseName = "MyDatabase"
    // SchemaName = "dbo"

    Source = Sql.Database(ServerName, DatabaseName),

    // Dynamic table selection
    GetTable = (tableName as text) =>
        Source{[Schema = SchemaName, Item = tableName]}[Data],

    // Get specific table
    SalesTable = GetTable("Sales"),

    // Apply standard transformations
    FilteredData = Table.SelectRows(SalesTable, each [IsActive] = true)
in
    FilteredData
```

### Dynamic Date Filtering for Incremental Refresh

```powerquery-m
// Last N days pattern
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Calculate date boundary
    CutoffDate = Date.AddDays(Date.From(DateTime.LocalNow()), -DaysToKeep),

    // Filter to recent data
    FilteredRows = Table.SelectRows(Sales, each [OrderDate] >= CutoffDate)
in
    FilteredRows

// Rolling months pattern
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Start of current month minus N months
    StartDate = Date.StartOfMonth(Date.AddMonths(Date.From(DateTime.LocalNow()), -MonthsToKeep)),

    FilteredRows = Table.SelectRows(Sales, each [OrderDate] >= StartDate)
in
    FilteredRows

// Fiscal year pattern
let
    Source = Sql.Database("server", "database"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Assuming fiscal year starts in July
    CurrentDate = Date.From(DateTime.LocalNow()),
    FiscalYearStart = if Date.Month(CurrentDate) >= 7
                      then #date(Date.Year(CurrentDate), 7, 1)
                      else #date(Date.Year(CurrentDate) - 1, 7, 1),

    FilteredRows = Table.SelectRows(Sales, each [OrderDate] >= FiscalYearStart)
in
    FilteredRows
```

### Combining Multiple Files from a Folder

```powerquery-m
// Combine CSV files from folder
let
    // Get all files in folder
    Source = Folder.Files(FolderPath),

    // Filter to CSV files only
    CsvFiles = Table.SelectRows(Source, each [Extension] = ".csv"),

    // Add column with parsed CSV data
    AddedData = Table.AddColumn(CsvFiles, "Data", each
        let
            // Parse CSV content
            CsvContent = Csv.Document([Content], [Delimiter=",", Encoding=65001]),
            // Promote headers
            WithHeaders = Table.PromoteHeaders(CsvContent, [PromoteAllScalars=true])
        in
            WithHeaders
    ),

    // Remove file metadata columns, keep only Data
    RemovedOtherColumns = Table.SelectColumns(AddedData, {"Data", "Name"}),

    // Expand all tables into one
    ExpandedData = Table.ExpandTableColumn(
        RemovedOtherColumns,
        "Data",
        Table.ColumnNames(RemovedOtherColumns{0}[Data])
    )
in
    ExpandedData

// Combine Excel files with specific sheet
let
    Source = Folder.Files("C:\Data\Monthly Reports"),
    ExcelFiles = Table.SelectRows(Source, each [Extension] = ".xlsx"),
    AddedWorkbooks = Table.AddColumn(ExcelFiles, "Workbook", each
        Excel.Workbook([Content], true, true)
    ),
    AddedData = Table.AddColumn(AddedWorkbooks, "Data", each
        [Workbook]{[Item="Sales", Kind="Sheet"]}[Data]
    ),
    ExpandedData = Table.ExpandTableColumn(
        Table.SelectColumns(AddedData, {"Name", "Data"}),
        "Data",
        Table.ColumnNames(AddedData{0}[Data])
    )
in
    ExpandedData
```

### API Pagination

```powerquery-m
// Page number-based pagination
let
    // Function to get a single page
    GetPage = (pageNum as number) as table =>
        let
            Source = Web.Contents(
                ApiBaseUrl,
                [
                    RelativePath = "/api/orders",
                    Query = [
                        page = Text.From(pageNum),
                        pageSize = "100"
                    ],
                    Headers = [Authorization = "Bearer " & ApiToken]
                ]
            ),
            JsonResponse = Json.Document(Source),
            DataTable = Table.FromRecords(JsonResponse[data])
        in
            DataTable,

    // Generate pages until empty
    AllPages = List.Generate(
        () => [Page = 1, Data = GetPage(1)],
        each Table.RowCount([Data]) > 0,
        each [Page = [Page] + 1, Data = GetPage([Page] + 1)],
        each [Data]
    ),

    // Combine all pages
    CombinedData = Table.Combine(AllPages)
in
    CombinedData

// Cursor-based pagination
let
    GetPageWithCursor = (cursor as nullable text) as record =>
        let
            QueryParams = if cursor = null
                          then [limit = "100"]
                          else [limit = "100", cursor = cursor],
            Source = Web.Contents(
                ApiBaseUrl,
                [
                    RelativePath = "/api/data",
                    Query = QueryParams,
                    Headers = [Authorization = "Bearer " & ApiToken]
                ]
            ),
            JsonResponse = Json.Document(Source)
        in
            JsonResponse,

    AllPages = List.Generate(
        () => [Response = GetPageWithCursor(null), Continue = true],
        each [Continue],
        each [
            Response = GetPageWithCursor([Response][next_cursor]?),
            Continue = [Response][next_cursor]? <> null
        ],
        each Table.FromRecords([Response][data])
    ),

    CombinedData = Table.Combine(AllPages)
in
    CombinedData

// Offset-based pagination
let
    PageSize = 500,

    GetPage = (offset as number) as table =>
        let
            Source = Web.Contents(
                ApiBaseUrl,
                [
                    RelativePath = "/api/records",
                    Query = [
                        offset = Text.From(offset),
                        limit = Text.From(PageSize)
                    ]
                ]
            ),
            JsonResponse = Json.Document(Source),
            DataTable = Table.FromRecords(JsonResponse)
        in
            DataTable,

    // Get first page to determine total
    FirstPage = GetPage(0),
    TotalCount = 5000,  // Or get from API response

    // Calculate number of pages needed
    PageCount = Number.RoundUp(TotalCount / PageSize),

    // Generate all offsets
    Offsets = List.Generate(
        () => 0,
        each _ < TotalCount,
        each _ + PageSize
    ),

    // Get all pages
    AllPages = List.Transform(Offsets, each GetPage(_)),

    // Combine
    CombinedData = Table.Combine(AllPages)
in
    CombinedData
```

### Custom Functions

```powerquery-m
// Define a reusable function
let
    // Function definition
    CleanText = (inputText as nullable text) as nullable text =>
        if inputText = null then null
        else
            let
                Trimmed = Text.Trim(inputText),
                NoExtraSpaces = Text.Combine(
                    List.Select(Text.Split(Trimmed, " "), each _ <> ""),
                    " "
                ),
                ProperCase = Text.Proper(NoExtraSpaces)
            in
                ProperCase,

    // Use the function
    Source = SalesTable,
    CleanedNames = Table.TransformColumns(Source, {
        {"CustomerName", CleanText},
        {"ProductName", CleanText}
    })
in
    CleanedNames

// Function with multiple parameters
let
    CalculateDiscount = (price as number, quantity as number, customerTier as text) as number =>
        let
            BaseDiscount = if quantity >= 100 then 0.15
                          else if quantity >= 50 then 0.10
                          else if quantity >= 10 then 0.05
                          else 0,
            TierBonus = if customerTier = "Gold" then 0.05
                       else if customerTier = "Silver" then 0.02
                       else 0,
            TotalDiscount = BaseDiscount + TierBonus,
            DiscountedPrice = price * (1 - TotalDiscount)
        in
            DiscountedPrice,

    Source = OrderDetails,
    WithDiscount = Table.AddColumn(Source, "FinalPrice", each
        CalculateDiscount([UnitPrice], [Quantity], [CustomerTier])
    )
in
    WithDiscount

// Recursive function for hierarchies
let
    // Build path from child to root
    GetFullPath = (table as table, id as any, pathSoFar as text) as text =>
        let
            CurrentRow = Table.SelectRows(table, each [ID] = id),
            CurrentName = if Table.RowCount(CurrentRow) > 0
                         then CurrentRow{0}[Name]
                         else "",
            ParentID = if Table.RowCount(CurrentRow) > 0
                      then CurrentRow{0}[ParentID]
                      else null,
            NewPath = if pathSoFar = ""
                     then CurrentName
                     else CurrentName & " > " & pathSoFar
        in
            if ParentID = null then NewPath
            else @GetFullPath(table, ParentID, NewPath),

    Source = CategoryHierarchy,
    WithPath = Table.AddColumn(Source, "FullPath", each
        GetFullPath(Source, [ID], "")
    )
in
    WithPath
```

### Date Table Generation

```powerquery-m
// Generate a complete date table
let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2025, 12, 31),

    // Generate list of dates
    DateCount = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, DateCount, #duration(1, 0, 0, 0)),

    // Convert to table
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),

    // Change type
    TypedDate = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),

    // Add date attributes
    AddYear = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), Int64.Type),
    AddMonth = Table.AddColumn(AddYear, "Month", each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonth, "Month Name", each Date.MonthName([Date]), type text),
    AddQuarter = Table.AddColumn(AddMonthName, "Quarter", each Date.QuarterOfYear([Date]), Int64.Type),
    AddDay = Table.AddColumn(AddQuarter, "Day", each Date.Day([Date]), Int64.Type),
    AddDayOfWeek = Table.AddColumn(AddDay, "Day of Week", each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    AddDayName = Table.AddColumn(AddDayOfWeek, "Day Name", each Date.DayOfWeekName([Date]), type text),
    AddWeekOfYear = Table.AddColumn(AddDayName, "Week of Year", each Date.WeekOfYear([Date]), Int64.Type),
    AddIsWeekend = Table.AddColumn(AddWeekOfYear, "Is Weekend", each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical),
    AddYearMonth = Table.AddColumn(AddIsWeekend, "Year-Month", each Date.ToText([Date], "yyyy-MM"), type text),
    AddFiscalYear = Table.AddColumn(AddYearMonth, "Fiscal Year", each
        if Date.Month([Date]) >= 7 then Date.Year([Date]) + 1 else Date.Year([Date]),
        Int64.Type
    ),
    AddFiscalQuarter = Table.AddColumn(AddFiscalYear, "Fiscal Quarter", each
        let
            m = Date.Month([Date])
        in
            if m >= 7 and m <= 9 then 1
            else if m >= 10 and m <= 12 then 2
            else if m >= 1 and m <= 3 then 3
            else 4,
        Int64.Type
    )
in
    AddFiscalQuarter
```

---

## References

- [Microsoft Power Query M Reference](https://learn.microsoft.com/en-us/powerquery-m/)
- [Power Query M Function Reference](https://learn.microsoft.com/en-us/powerquery-m/power-query-m-function-reference)
- [Table.AddColumn](https://learn.microsoft.com/en-us/powerquery-m/table-addcolumn)
- [Table.SelectRows](https://learn.microsoft.com/en-us/powerquery-m/table-selectrows)
- [Table.TransformColumnTypes](https://learn.microsoft.com/en-us/powerquery-m/table-transformcolumntypes)
- [Table.NestedJoin](https://learn.microsoft.com/en-us/powerquery-m/table-nestedjoin)
- [Table.Group](https://powerquery.how/table-group/)
- [Sql.Database](https://learn.microsoft.com/en-us/powerquery-m/sql-database)
- [SharePoint.Files](https://learn.microsoft.com/en-us/powerquery-m/sharepoint-files)
- [Error Handling in M](https://learn.microsoft.com/en-us/power-query/error-handling)
- [Configure Incremental Refresh](https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-configure)
- [Power Query Combine Files](https://learn.microsoft.com/en-us/power-query/combine-files-overview)
