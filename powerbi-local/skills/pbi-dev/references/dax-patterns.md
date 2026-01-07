# DAX Patterns and Best Practices

This reference covers essential DAX patterns, function categories, and performance best practices for Power BI development.

---

## 1. DAX Fundamentals

### Measures vs Calculated Columns

Understanding when to use measures versus calculated columns is fundamental to efficient DAX development.

| Aspect | Calculated Column | Measure |
|--------|-------------------|---------|
| **Evaluation time** | During data refresh | During query time |
| **Storage** | Stored in model (increases size) | Computed on demand |
| **Row context** | Has implicit row context | No implicit row context |
| **Filter context** | Not affected by slicers | Responds to all filters |
| **Use for** | Static values, sorting, relationships | Dynamic aggregations, KPIs |
| **Performance** | Front-loaded (refresh time) | Query-time computation |

**When to Use Calculated Columns:**
- Values needed for relationships between tables
- Values needed for sorting (e.g., month sort order)
- Row-level categorizations that don't change with filters
- Values needed in slicers

**When to Use Measures:**
- Any aggregation (SUM, COUNT, AVERAGE, etc.)
- Calculations that should respond to filter context
- Ratios and percentages
- Time intelligence calculations
- Dynamic KPIs and metrics

```dax
// Calculated Column - evaluated once per row during refresh
Profit Margin Category =
IF(Sales[Profit Margin] > 0.3, "High",
IF(Sales[Profit Margin] > 0.15, "Medium", "Low"))

// Measure - evaluated dynamically based on filter context
Average Profit Margin =
AVERAGE(Sales[Profit Margin])
```

---

### Evaluation Context

DAX has two types of evaluation context that determine how expressions are evaluated.

#### Row Context

Row context exists when DAX iterates over a table, providing access to values in the "current row."

**Row context is created by:**
- Calculated columns (implicit)
- Iterator functions: SUMX, AVERAGEX, COUNTX, FILTER, ADDCOLUMNS, etc.

```dax
// In a calculated column, row context gives access to current row
Line Total = Sales[Quantity] * Sales[Unit Price]

// SUMX creates row context for each iteration
Total Revenue =
SUMX(
    Sales,
    Sales[Quantity] * Sales[Unit Price]  // Row context here
)
```

#### Filter Context

Filter context is the set of filters that restrict which rows are considered for a calculation.

**Filter context is created by:**
- Slicers and visual filters
- Report page filters
- CALCULATE function filter arguments
- Rows/columns in matrix visuals

```dax
// This measure responds to filter context from slicers
Total Sales = SUM(Sales[Amount])

// When a slicer selects "2024", the filter context restricts
// the calculation to only 2024 data
```

---

### Context Transition with CALCULATE

Context transition is the transformation of row context into filter context, performed by CALCULATE and CALCULATETABLE.

**Key Rule:** When CALCULATE is executed inside a row context, it transforms that row context into an equivalent filter context.

```dax
// Without context transition - SUM ignores row context
// Returns the same total for every row
Wrong Total = SUM(Sales[Amount])

// With context transition - CALCULATE converts row context to filter
// Returns amount for current row's context
Correct Total = CALCULATE(SUM(Sales[Amount]))
```

**Important Behaviors:**

1. **Measures automatically invoke CALCULATE:**
   ```dax
   // When you reference a measure inside an iteration,
   // it's automatically wrapped in CALCULATE
   Total by Product =
   SUMX(
       Products,
       [Total Sales]  // Implicitly becomes CALCULATE([Total Sales])
   )
   ```

2. **Context transition filters ALL columns:**
   ```dax
   // Context transition creates filters for all columns in the current row
   // This can be expensive with wide tables
   ```

3. **Ensure unique rows for reliable results:**
   ```dax
   // Context transition is reliable when tables have unique rows
   // (primary key or unique combination of columns)
   ```

**Performance Warning:** Context transition can be expensive because, in each iteration, the model is re-filtered based on all columns in the row context. For a table with 10 columns and 1,000,000 rows, the model is filtered by those 10 columns 1,000,000 times.

---

## 2. Essential Function Reference

### Aggregation Functions

| Function | Description | Example |
|----------|-------------|---------|
| `SUM` | Sum of a column | `SUM(Sales[Amount])` |
| `AVERAGE` | Arithmetic mean | `AVERAGE(Sales[Price])` |
| `COUNT` | Count of non-blank values | `COUNT(Sales[OrderID])` |
| `COUNTA` | Count of non-blank values (any type) | `COUNTA(Products[Name])` |
| `COUNTROWS` | Count rows in a table | `COUNTROWS(Sales)` |
| `DISTINCTCOUNT` | Count of unique values | `DISTINCTCOUNT(Sales[CustomerID])` |
| `MIN` | Minimum value | `MIN(Sales[Date])` |
| `MAX` | Maximum value | `MAX(Sales[Date])` |
| `SUMX` | Sum with row-by-row expression | `SUMX(Sales, Sales[Qty] * Sales[Price])` |
| `AVERAGEX` | Average with row-by-row expression | `AVERAGEX(Products, [Total Sales])` |
| `COUNTX` | Count with row-by-row expression | `COUNTX(Sales, IF(Sales[Qty] > 10, 1))` |
| `MINX` | Minimum with row-by-row expression | `MINX(Sales, Sales[Qty] * Sales[Price])` |
| `MAXX` | Maximum with row-by-row expression | `MAXX(Sales, Sales[Qty] * Sales[Price])` |

**When to Use Iterators (X functions):**

```dax
// Use SUM when aggregating a single column
Simple Sum = SUM(Sales[Amount])

// Use SUMX when you need row-level calculations
Calculated Sum = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])

// Use SUMX when aggregating measure values per category
Sales by Category =
SUMX(
    VALUES(Products[Category]),
    [Total Sales]
)
```

---

### Filter Functions

| Function | Description | Example |
|----------|-------------|---------|
| `CALCULATE` | Evaluate expression with modified filter context | `CALCULATE([Sales], 'Date'[Year] = 2024)` |
| `CALCULATETABLE` | Return table with modified filter context | `CALCULATETABLE(Sales, 'Date'[Year] = 2024)` |
| `FILTER` | Return filtered table | `FILTER(Sales, Sales[Amount] > 1000)` |
| `ALL` | Remove all filters from table/columns | `ALL(Products)` |
| `ALLEXCEPT` | Remove all filters except specified columns | `ALLEXCEPT(Products, Products[Category])` |
| `ALLSELECTED` | Remove filters except slicer selections | `ALLSELECTED(Products)` |
| `KEEPFILTERS` | Preserve existing filters when adding new ones | `KEEPFILTERS(Products[Color] = "Red")` |
| `REMOVEFILTERS` | Remove filters (preferred over ALL for clarity) | `REMOVEFILTERS('Date')` |
| `VALUES` | Return distinct values respecting filter context | `VALUES(Products[Category])` |
| `DISTINCT` | Return distinct values from column/table | `DISTINCT(Sales[CustomerID])` |
| `SELECTEDVALUE` | Return single selected value or default | `SELECTEDVALUE('Date'[Year], 2024)` |

**CALCULATE Pattern Examples:**

```dax
// Simple filter
Sales 2024 =
CALCULATE([Total Sales], 'Date'[Year] = 2024)

// Multiple filters (AND logic)
Red Products 2024 =
CALCULATE(
    [Total Sales],
    'Date'[Year] = 2024,
    Products[Color] = "Red"
)

// Remove and add filters
All Products Sales =
CALCULATE([Total Sales], ALL(Products))

// Keep existing filters while adding
Filtered but Keeping =
CALCULATE(
    [Total Sales],
    KEEPFILTERS(Products[Color] = "Red")
)
```

**ALL vs ALLSELECTED vs REMOVEFILTERS:**

```dax
// ALL - ignores ALL filters on the table
% of All Products =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL(Products))
)

// ALLSELECTED - respects slicer selections
% of Selected Products =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALLSELECTED(Products))
)

// REMOVEFILTERS - semantic equivalent to ALL, preferred for clarity
% of Total =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], REMOVEFILTERS(Products))
)
```

---

### Table Functions

| Function | Description | Example |
|----------|-------------|---------|
| `SUMMARIZE` | Group by columns from related tables | `SUMMARIZE(Sales, Products[Category])` |
| `SUMMARIZECOLUMNS` | Optimized grouping with measures | See example below |
| `ADDCOLUMNS` | Add calculated columns to table | `ADDCOLUMNS(Products, "Sales", [Total Sales])` |
| `SELECTCOLUMNS` | Select and rename columns | `SELECTCOLUMNS(Sales, "Order", Sales[OrderID])` |
| `UNION` | Combine tables vertically | `UNION(Table1, Table2)` |
| `INTERSECT` | Return common rows | `INTERSECT(Table1, Table2)` |
| `EXCEPT` | Return rows in first table not in second | `EXCEPT(Table1, Table2)` |
| `CROSSJOIN` | Cartesian product of tables | `CROSSJOIN(Dates, Products)` |
| `GENERATE` | For each row, evaluate table expression | `GENERATE(Products, TOPN(3, Sales))` |
| `GENERATEALL` | Like GENERATE, keeps rows with empty results | See documentation |
| `ROW` | Create single-row table | `ROW("Sales", [Total Sales])` |
| `DATATABLE` | Create table with literal values | See example below |

**SUMMARIZECOLUMNS vs SUMMARIZE:**

```dax
// SUMMARIZECOLUMNS - preferred for performance
// Automatically removes blank rows, optimized by engine
SummaryTable =
SUMMARIZECOLUMNS(
    Products[Category],
    'Date'[Year],
    "Total Sales", [Total Sales],
    "Order Count", [Order Count]
)

// SUMMARIZE - older function, use with ADDCOLUMNS for calculations
// Does NOT automatically remove blanks
SummaryTable =
ADDCOLUMNS(
    SUMMARIZE(Sales, Products[Category], 'Date'[Year]),
    "Total Sales", [Total Sales]
)
```

**Important:** SUMMARIZECOLUMNS cannot be used in calculated columns, only in measures and DAX queries.

---

### Logical Functions

| Function | Description | Example |
|----------|-------------|---------|
| `IF` | Conditional evaluation | `IF([Sales] > 1000, "High", "Low")` |
| `SWITCH` | Multiple condition evaluation | `SWITCH([Rating], 1, "Poor", 2, "Fair", "Good")` |
| `AND` | Logical AND (use && in expressions) | `AND([A] > 0, [B] > 0)` |
| `OR` | Logical OR (use \|\| in expressions) | `OR([A] > 0, [B] > 0)` |
| `NOT` | Logical NOT | `NOT([IsActive])` |
| `COALESCE` | Return first non-blank value | `COALESCE([Value1], [Value2], 0)` |
| `IFERROR` | Handle errors | `IFERROR([Calculation], 0)` |
| `ISBLANK` | Test for blank | `IF(ISBLANK([Value]), "No Data", [Value])` |
| `ISERROR` | Test for error | `IF(ISERROR([Calc]), 0, [Calc])` |
| `TRUE` / `FALSE` | Boolean constants | `IF([Active] = TRUE(), ...)` |

**SWITCH Pattern for Multiple Conditions:**

```dax
// SWITCH with values
Rating Label =
SWITCH(
    [Rating],
    1, "Poor",
    2, "Below Average",
    3, "Average",
    4, "Good",
    5, "Excellent",
    "Unknown"  // Default value
)

// SWITCH TRUE pattern for complex conditions
Sales Category =
SWITCH(
    TRUE(),
    [Total Sales] >= 100000, "Enterprise",
    [Total Sales] >= 50000, "Large",
    [Total Sales] >= 10000, "Medium",
    [Total Sales] >= 1000, "Small",
    "Micro"
)
```

---

### Text Functions

| Function | Description | Example |
|----------|-------------|---------|
| `CONCATENATE` | Join two strings | `CONCATENATE([First], [Last])` |
| `CONCATENATEX` | Join values from table | `CONCATENATEX(Products, Products[Name], ", ")` |
| `FORMAT` | Convert to formatted text | `FORMAT([Date], "MMMM YYYY")` |
| `LEFT` | Extract left characters | `LEFT([Code], 3)` |
| `RIGHT` | Extract right characters | `RIGHT([Code], 4)` |
| `MID` | Extract middle characters | `MID([Code], 2, 3)` |
| `LEN` | String length | `LEN([Name])` |
| `SEARCH` | Find text position (case-insensitive) | `SEARCH("test", [Text])` |
| `FIND` | Find text position (case-sensitive) | `FIND("Test", [Text])` |
| `SUBSTITUTE` | Replace text | `SUBSTITUTE([Text], "old", "new")` |
| `REPLACE` | Replace by position | `REPLACE([Text], 1, 3, "NEW")` |
| `TRIM` | Remove extra spaces | `TRIM([Text])` |
| `UPPER` / `LOWER` | Change case | `UPPER([Name])` |
| `BLANK` | Return blank value | `IF([Sales] = 0, BLANK(), [Sales])` |

```dax
// Concatenate with separator
Full Name = [First Name] & " " & [Last Name]

// Extract year from code like "2024-001"
Year Code = LEFT(Sales[OrderCode], 4)

// Dynamic label
Sales Label =
FORMAT([Total Sales], "$#,##0") & " (" &
FORMAT([Growth Rate], "0.0%") & " YoY)"
```

---

### Date Functions

| Function | Description | Example |
|----------|-------------|---------|
| `DATE` | Create date from parts | `DATE(2024, 1, 15)` |
| `YEAR` | Extract year | `YEAR([Date])` |
| `MONTH` | Extract month (1-12) | `MONTH([Date])` |
| `DAY` | Extract day | `DAY([Date])` |
| `TODAY` | Current date | `TODAY()` |
| `NOW` | Current date and time | `NOW()` |
| `DATEDIFF` | Difference between dates | `DATEDIFF([Start], [End], DAY)` |
| `DATEADD` | Add interval to date | `DATEADD('Date'[Date], -1, YEAR)` |
| `EOMONTH` | End of month | `EOMONTH([Date], 0)` |
| `EDATE` | Add months to date | `EDATE([Date], 3)` |
| `WEEKDAY` | Day of week (1-7) | `WEEKDAY([Date], 2)` |
| `WEEKNUM` | Week number | `WEEKNUM([Date], 2)` |
| `CALENDAR` | Generate date table | `CALENDAR(DATE(2020,1,1), DATE(2025,12,31))` |
| `CALENDARAUTO` | Auto date table from model | `CALENDARAUTO()` |

```dax
// Days since last order
Days Since Order =
DATEDIFF(MAX(Sales[OrderDate]), TODAY(), DAY)

// End of current month
Month End = EOMONTH(TODAY(), 0)

// First day of current month
Month Start = DATE(YEAR(TODAY()), MONTH(TODAY()), 1)
```

---

## 3. Common Patterns

### Basic Ratio with DIVIDE

Always use DIVIDE instead of the division operator to handle divide-by-zero safely.

```dax
// BAD - can cause errors
Margin % = ([Sales] - [Cost]) / [Sales]

// GOOD - handles zero/blank safely
Margin % =
DIVIDE(
    [Sales] - [Cost],
    [Sales],
    BLANK()  // Optional: value to return when dividing by zero
)

// Alternative with 0 default
Margin % = DIVIDE([Sales] - [Cost], [Sales], 0)
```

---

### Percentage of Total

```dax
// Percentage of grand total
% of Total =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL(Sales))
)

// Percentage of total within current slicer selection
% of Selected =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALLSELECTED())
)

// Percentage of parent (for matrix visuals)
% of Parent =
DIVIDE(
    [Total Sales],
    CALCULATE(
        [Total Sales],
        ALLEXCEPT(Products, Products[Category])
    )
)
```

---

### Running Total (Cumulative Sum)

```dax
// Running total by date
Running Total =
CALCULATE(
    [Total Sales],
    FILTER(
        ALL('Date'),
        'Date'[Date] <= MAX('Date'[Date])
    )
)

// Running total within year
YTD Running Total =
CALCULATE(
    [Total Sales],
    FILTER(
        ALL('Date'),
        'Date'[Date] <= MAX('Date'[Date]) &&
        'Date'[Year] = MAX('Date'[Year])
    )
)

// Alternative using DATESYTD (recommended)
YTD Sales =
CALCULATE(
    [Total Sales],
    DATESYTD('Date'[Date])
)
```

---

### Moving Average

```dax
// 3-Month Moving Average
Moving Avg 3M =
AVERAGEX(
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -3,
        MONTH
    ),
    [Total Sales]
)

// 12-Month Rolling Average
Rolling Avg 12M =
VAR PeriodLength = 12
VAR LastDate = MAX('Date'[Date])
VAR DateRange =
    DATESINPERIOD('Date'[Date], LastDate, -PeriodLength, MONTH)
RETURN
AVERAGEX(DateRange, [Total Sales])

// Moving Average with DATESINPERIOD (handles gaps correctly)
Moving Avg 30 Days =
VAR LastVisibleDate = MAX('Date'[Date])
VAR Period =
    DATESINPERIOD('Date'[Date], LastVisibleDate, -30, DAY)
VAR Result =
    CALCULATE(
        DIVIDE(SUM(Sales[Amount]), 30),
        Period
    )
RETURN Result
```

**Important:** When calculating moving averages, DATESINPERIOD divides by the fixed period length, while AVERAGEX divides by the count of non-blank values. Choose based on your business requirement.

---

### Rank and TopN

```dax
// Rank products by sales
Product Rank =
IF(
    HASONEVALUE(Products[ProductName]),
    RANKX(
        ALL(Products[ProductName]),
        [Total Sales],
        ,
        DESC,
        DENSE
    )
)

// Dynamic TopN with measure
TopN Products Sales =
CALCULATE(
    [Total Sales],
    TOPN(
        10,
        ALL(Products[ProductName]),
        [Total Sales],
        DESC
    )
)

// TopN with "Others" category
Sales with Others =
VAR TopCount = 5
VAR CurrentProduct = SELECTEDVALUE(Products[ProductName])
VAR TopProducts =
    TOPN(TopCount, ALL(Products[ProductName]), [Total Sales], DESC)
VAR IsTopProduct = CurrentProduct IN TopProducts
RETURN
IF(
    IsTopProduct,
    [Total Sales],
    IF(CurrentProduct = "Others",
        CALCULATE([Total Sales], EXCEPT(ALL(Products[ProductName]), TopProducts)))
)
```

---

### Parent-Child Hierarchy Flattening

Use the PATH functions to flatten parent-child hierarchies into separate level columns.

```dax
// In a table with EmployeeID and ManagerID columns:

// Create the path (calculated column)
Path = PATH(Employee[EmployeeID], Employee[ManagerID])
// Returns: "1|5|23|156" (root to current)

// Extract each level (calculated columns)
Level1 = PATHITEM(Employee[Path], 1, INTEGER)
Level2 = PATHITEM(Employee[Path], 2, INTEGER)
Level3 = PATHITEM(Employee[Path], 3, INTEGER)
Level4 = PATHITEM(Employee[Path], 4, INTEGER)

// Get depth
Depth = PATHLENGTH(Employee[Path])

// Get names for each level (requires lookup)
Level1 Name =
LOOKUPVALUE(
    Employee[EmployeeName],
    Employee[EmployeeID],
    PATHITEM(Employee[Path], 1, INTEGER)
)

// Check if employee reports to specific manager
Reports To Manager =
PATHCONTAINS(Employee[Path], [ManagerToCheck])
```

---

### Handling Blanks vs Zeros

```dax
// Replace BLANK with zero for calculations
Sales No Blanks =
IF(ISBLANK([Total Sales]), 0, [Total Sales])

// Using COALESCE (cleaner syntax)
Sales No Blanks = COALESCE([Total Sales], 0)

// Return BLANK instead of zero (for visuals)
Sales Hide Zero =
IF([Total Sales] = 0, BLANK(), [Total Sales])

// Treat both BLANK and zero as "no value"
Has Sales =
NOT(ISBLANK([Total Sales])) && [Total Sales] <> 0

// Sum with BLANK handling
Combined Value =
COALESCE([Value1], 0) + COALESCE([Value2], 0)
```

**BLANK Propagation Rules:**
- BLANK + Number = Number (BLANK treated as 0)
- BLANK * Number = BLANK
- BLANK / Number = BLANK
- Number / BLANK = BLANK (with DIVIDE, returns alternate result)

---

## 4. Performance Best Practices

### Avoid Iterators When Aggregators Exist

```dax
// SLOW - iterates every row
Bad Total = SUMX(Sales, Sales[Amount])

// FAST - direct aggregation
Good Total = SUM(Sales[Amount])

// SLOW - unnecessary iteration
Bad Count = COUNTX(Sales, Sales[OrderID])

// FAST - direct count
Good Count = COUNTROWS(Sales)
```

**When iterators ARE appropriate:**
- Row-level calculations: `SUMX(Sales, Sales[Qty] * Sales[Price])`
- Aggregating measure values: `SUMX(VALUES(Products), [Total Sales])`
- Complex conditional logic per row

---

### Use Variables to Avoid Repeated Calculations

```dax
// BAD - calculates [Total Sales] three times
Growth % =
DIVIDE(
    [Total Sales] - CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date])),
    CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
)

// GOOD - calculates each value once
Growth % =
VAR CurrentSales = [Total Sales]
VAR PriorYearSales =
    CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
RETURN
DIVIDE(CurrentSales - PriorYearSales, PriorYearSales)
```

**Benefits of Variables:**
- Improved readability
- Single calculation for reused values
- Easier debugging (can return VAR values to test)
- Better query plan optimization

---

### SUMMARIZECOLUMNS vs SUMMARIZE

| Aspect | SUMMARIZECOLUMNS | SUMMARIZE |
|--------|------------------|-----------|
| Performance | Better optimized | Less optimized |
| Blank rows | Auto-removed | Included |
| Calculated columns | Supports directly | Use with ADDCOLUMNS |
| Usage context | Measures, DAX queries | Any context |
| Calculated columns | Cannot use in | Can use in |

```dax
// Preferred for measures and queries
SUMMARIZECOLUMNS(
    Products[Category],
    "Sales", [Total Sales],
    "Cost", [Total Cost]
)

// Use SUMMARIZE + ADDCOLUMNS when SUMMARIZECOLUMNS won't work
ADDCOLUMNS(
    SUMMARIZE(Sales, Products[Category]),
    "Sales", [Total Sales]
)
```

---

### DISTINCTCOUNT Optimization

DISTINCTCOUNT can be one of the most expensive operations. Optimization strategies:

```dax
// Standard DISTINCTCOUNT
Customer Count = DISTINCTCOUNT(Sales[CustomerID])

// Alternative using COUNTROWS + VALUES (sometimes faster)
Customer Count = COUNTROWS(VALUES(Sales[CustomerID]))

// For rolling distinct counts, consider materialization
Rolling Distinct =
VAR MaterializedTable =
    ADDCOLUMNS(
        SUMMARIZE(Sales, 'Date'[Date], Sales[CustomerID]),
        "HasCustomer", 1
    )
RETURN
SUMX(
    FILTER(MaterializedTable, [Date] >= [StartDate]),
    [HasCustomer]
)
```

**Optimization Tips:**
1. Reduce column cardinality where possible
2. Consider approximate distinct count for large datasets
3. Use aggregation tables for frequently-needed distinct counts
4. Test with DAX Studio to compare approaches
5. Filter data before applying DISTINCTCOUNT

---

### Avoiding Circular Dependencies

Circular dependencies occur when calculated columns or measures reference each other.

```dax
// PROBLEM: Circular dependency
// Column A references Column B, Column B references Column A

// SOLUTION 1: Use measures instead of calculated columns
// Measures are evaluated at query time, avoiding compile-time cycles

// SOLUTION 2: Use ALLEXCEPT to break dependency
Calculation =
CALCULATE(
    [Base Measure],
    ALLEXCEPT(Table, Table[KeyColumn])
)

// SOLUTION 3: Use ALLNOBLANKROW instead of ALL
Calculation =
CALCULATE(
    SUM(Table[Value]),
    ALLNOBLANKROW(Table[Category])
)

// SOLUTION 4: Restructure with variables
Result =
VAR BaseValue = [Value Without Dependency]
RETURN
BaseValue * [Multiplier]
```

---

## 5. Format Strings

### Common Format String Patterns

| Purpose | Format String | Example Output |
|---------|---------------|----------------|
| Currency (US) | `"$#,##0.00"` | $1,234.56 |
| Currency (no decimals) | `"$#,##0"` | $1,235 |
| Currency (negative in parens) | `"$#,##0.00;($#,##0.00)"` | ($1,234.56) |
| Percentage | `"0.0%"` | 12.5% |
| Percentage (2 decimals) | `"0.00%"` | 12.50% |
| Number with commas | `"#,##0"` | 1,234,567 |
| Number (2 decimals) | `"#,##0.00"` | 1,234.57 |
| Integer | `"0"` | 1235 |
| Short date | `"M/d/yyyy"` | 1/15/2024 |
| Long date | `"MMMM d, yyyy"` | January 15, 2024 |
| Month year | `"MMM yyyy"` | Jan 2024 |
| Month name | `"MMMM"` | January |
| Day name | `"dddd"` | Monday |
| Time | `"h:mm AM/PM"` | 3:45 PM |
| ISO date | `"yyyy-MM-dd"` | 2024-01-15 |

### Using FORMAT Function

```dax
// Format as currency
Formatted Sales = FORMAT([Total Sales], "$#,##0.00")

// Format as percentage
Formatted Growth = FORMAT([Growth Rate], "0.0%")

// Format date
Formatted Date = FORMAT([Date], "MMMM d, yyyy")

// Dynamic format based on value
Dynamic Format =
VAR Sales = [Total Sales]
RETURN
SWITCH(
    TRUE(),
    Sales >= 1000000, FORMAT(Sales / 1000000, "#,##0.0") & "M",
    Sales >= 1000, FORMAT(Sales / 1000, "#,##0.0") & "K",
    FORMAT(Sales, "#,##0")
)
```

**Important:** FORMAT returns a TEXT value. This means:
- The result cannot be used in further calculations
- Charts may not work correctly with FORMAT output
- Use FORMAT only for display purposes
- Consider dynamic format strings for measures (maintains numeric type)

### Predefined Format Strings

```dax
// Use predefined formats for locale-aware formatting
FORMAT([Value], "Currency")      // Uses user's locale
FORMAT([Value], "Percent")       // Percentage with locale
FORMAT([Date], "Short Date")     // Locale-appropriate short date
FORMAT([Date], "Long Date")      // Locale-appropriate long date
FORMAT([Value], "Scientific")    // Scientific notation
```

---

## Additional Resources

- [DAX Guide](https://dax.guide/) - Comprehensive DAX function reference
- [DAX Patterns](https://www.daxpatterns.com/) - SQLBI patterns library
- [SQLBI Articles](https://www.sqlbi.com/articles/) - In-depth DAX articles
- [The Definitive Guide to DAX](https://www.sqlbi.com/books/the-definitive-guide-to-dax/) - Comprehensive book by Marco Russo and Alberto Ferrari
