# TMDL Examples Reference

This document provides practical, production-ready TMDL examples for common Power BI semantic model patterns. Each example is complete and can be adapted for your models.

## Table of Contents

1. [Complete Table Example](#1-complete-table-example)
2. [Measure Examples](#2-measure-examples)
3. [Relationship Examples](#3-relationship-examples)
4. [Calculated Column Examples](#4-calculated-column-examples)
5. [Calculation Group Examples](#5-calculation-group-examples)
6. [RLS Role Examples](#6-rls-role-examples)
7. [Named Expression Examples](#7-named-expression-examples)

---

## 1. Complete Table Example

### Sales Fact Table

A complete fact table with columns, measures, hierarchies, and partitions:

```tmdl
/// Sales transactions fact table
/// Contains all sales orders from the operational system
table Sales
    lineageTag: e9374b9a-faee-4f9e-b2e7-d9aafb9d6a91

    /// Primary key for sales transactions
    column SalesOrderID
        dataType: int64
        isKey
        sourceColumn: SalesOrderID
        lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890
        summarizeBy: none

    /// Foreign key to Product dimension
    column ProductKey
        dataType: int64
        isHidden
        sourceColumn: ProductKey
        lineageTag: b2c3d4e5-f6a7-8901-bcde-f12345678901
        summarizeBy: none

    /// Foreign key to Customer dimension
    column CustomerKey
        dataType: int64
        isHidden
        sourceColumn: CustomerKey
        lineageTag: c3d4e5f6-a7b8-9012-cdef-123456789012
        summarizeBy: none

    /// Foreign key to Date dimension
    column OrderDateKey
        dataType: int64
        isHidden
        sourceColumn: OrderDateKey
        lineageTag: d4e5f6a7-b8c9-0123-def0-234567890123
        summarizeBy: none

    /// Order date for the transaction
    column 'Order Date'
        dataType: dateTime
        formatString: Short Date
        sourceColumn: OrderDate
        lineageTag: e5f6a7b8-c9d0-1234-ef01-345678901234

    /// Quantity of units sold
    column Quantity
        dataType: int64
        sourceColumn: Quantity
        lineageTag: f6a7b8c9-d0e1-2345-f012-456789012345
        summarizeBy: sum

    /// Unit price at time of sale
    column 'Unit Price'
        dataType: decimal
        formatString: $#,##0.00
        sourceColumn: UnitPrice
        lineageTag: 01234567-89ab-cdef-0123-456789abcdef
        summarizeBy: none

    /// Discount percentage applied
    column 'Discount Pct'
        dataType: double
        formatString: 0.00%
        sourceColumn: DiscountPct
        lineageTag: 12345678-9abc-def0-1234-56789abcdef0
        summarizeBy: none

    /// Line item total before discount
    column 'Line Total'
        dataType: decimal
        formatString: $#,##0.00
        sourceColumn: LineTotal
        lineageTag: 23456789-abcd-ef01-2345-6789abcdef01
        summarizeBy: sum

    /// Total sales revenue
    measure 'Total Sales' = SUM(Sales[Line Total])
        formatString: $#,##0.00
        displayFolder: Revenue
        lineageTag: 34567890-bcde-f012-3456-789abcdef012

    /// Total units sold
    measure 'Total Quantity' = SUM(Sales[Quantity])
        formatString: #,##0
        displayFolder: Volume
        lineageTag: 4567890a-cdef-0123-4567-89abcdef0123

    /// Count of distinct orders
    measure 'Order Count' = DISTINCTCOUNT(Sales[SalesOrderID])
        formatString: #,##0
        displayFolder: Volume
        lineageTag: 567890ab-def0-1234-5678-9abcdef01234

    /// Average order value
    measure 'Average Order Value' =
            DIVIDE(
                [Total Sales],
                [Order Count],
                0
            )
        formatString: $#,##0.00
        displayFolder: Revenue
        lineageTag: 67890abc-ef01-2345-6789-abcdef012345

    partition Sales-Partition = m
        mode: import
        source =
            let
                Source = Sql.Database(#"Server Name", #"Database Name"),
                dbo_Sales = Source{[Schema="dbo",Item="Sales"]}[Data],
                FilteredRows = Table.SelectRows(dbo_Sales, each [OrderDate] >= #date(2020, 1, 1))
            in
                FilteredRows
```

### Product Dimension Table

```tmdl
/// Product dimension table
table Products
    lineageTag: 78901234-5678-9abc-def0-123456789abc

    column ProductKey
        dataType: int64
        isKey
        isHidden
        sourceColumn: ProductKey
        lineageTag: 89012345-6789-abcd-ef01-23456789abcd
        summarizeBy: none

    column 'Product Name'
        dataType: string
        sourceColumn: ProductName
        lineageTag: 9012345a-789a-bcde-f012-3456789abcde

    column 'Product Category'
        dataType: string
        sourceColumn: ProductCategory
        lineageTag: 012345ab-89ab-cdef-0123-456789abcdef

    column 'Product Subcategory'
        dataType: string
        sourceColumn: ProductSubcategory
        lineageTag: 12345abc-9abc-def0-1234-56789abcdef0

    column 'Unit Cost'
        dataType: decimal
        formatString: $#,##0.00
        sourceColumn: UnitCost
        lineageTag: 2345abcd-abcd-ef01-2345-6789abcdef01
        summarizeBy: none

    column 'List Price'
        dataType: decimal
        formatString: $#,##0.00
        sourceColumn: ListPrice
        lineageTag: 345abcde-bcde-f012-3456-789abcdef012
        summarizeBy: none

    /// Count of distinct products
    measure 'Product Count' = DISTINCTCOUNT(Products[ProductKey])
        formatString: #,##0
        lineageTag: 45abcdef-cdef-0123-4567-89abcdef0123

    hierarchy 'Product Hierarchy'
        lineageTag: 5abcdef0-def0-1234-5678-9abcdef01234

        level Category
            lineageTag: 6abcdef1-ef01-2345-6789-abcdef012345
            column: 'Product Category'

        level Subcategory
            lineageTag: 7abcdef2-f012-3456-789a-bcdef0123456
            column: 'Product Subcategory'

        level Product
            lineageTag: 8abcdef3-0123-4567-89ab-cdef01234567
            column: 'Product Name'

    partition Products-Partition = m
        mode: import
        source =
            let
                Source = Sql.Database(#"Server Name", #"Database Name"),
                dbo_Products = Source{[Schema="dbo",Item="Products"]}[Data]
            in
                dbo_Products
```

### Calendar Date Table

```tmdl
/// Date dimension for time intelligence
table Calendar
    lineageTag: 9abcdef4-1234-5678-9abc-def012345678
    dataCategory: Time

    column Date
        dataType: dateTime
        isKey
        formatString: Short Date
        lineageTag: abcdef01-2345-6789-abcd-ef0123456789

    column Year
        dataType: int64
        lineageTag: bcdef012-3456-789a-bcde-f01234567890
        summarizeBy: none

    column Quarter
        dataType: string
        lineageTag: cdef0123-4567-89ab-cdef-012345678901

    column 'Quarter Number'
        dataType: int64
        isHidden
        lineageTag: def01234-5678-9abc-def0-123456789012
        summarizeBy: none

    column Month
        dataType: string
        sortByColumn: 'Month Number'
        lineageTag: ef012345-6789-abcd-ef01-234567890123

    column 'Month Number'
        dataType: int64
        isHidden
        lineageTag: f0123456-789a-bcde-f012-345678901234
        summarizeBy: none

    column 'Day of Week'
        dataType: string
        sortByColumn: 'Day of Week Number'
        lineageTag: 01234567-89ab-cdef-0123-456789abcdef

    column 'Day of Week Number'
        dataType: int64
        isHidden
        lineageTag: 1234567a-9abc-def0-1234-56789abcdef0
        summarizeBy: none

    column 'Is Weekend'
        dataType: boolean
        lineageTag: 234567ab-abcd-ef01-2345-6789abcdef01

    hierarchy 'Date Hierarchy'
        lineageTag: 34567abc-bcde-f012-3456-789abcdef012

        level Year
            lineageTag: 4567abcd-cdef-0123-4567-89abcdef0123
            column: Year

        level Quarter
            lineageTag: 567abcde-def0-1234-5678-9abcdef01234
            column: Quarter

        level Month
            lineageTag: 67abcdef-ef01-2345-6789-abcdef012345
            column: Month

        level Date
            lineageTag: 7abcdef0-f012-3456-789a-bcdef0123456
            column: Date

    partition Calendar-Partition = calculated
        mode: import
        source =
            var MinDate = DATE(2018, 1, 1)
            var MaxDate = DATE(2025, 12, 31)
            return
            ADDCOLUMNS(
                CALENDAR(MinDate, MaxDate),
                "Year", YEAR([Date]),
                "Quarter", "Q" & QUARTER([Date]),
                "Quarter Number", QUARTER([Date]),
                "Month", FORMAT([Date], "MMMM"),
                "Month Number", MONTH([Date]),
                "Day of Week", FORMAT([Date], "dddd"),
                "Day of Week Number", WEEKDAY([Date], 2),
                "Is Weekend", WEEKDAY([Date], 2) >= 6
            )
```

---

## 2. Measure Examples

### Simple Aggregation Measures

```tmdl
/// Sum of sales amount
measure 'Total Sales' = SUM(Sales[Amount])
    formatString: $#,##0.00
    displayFolder: Revenue
    lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890

/// Count of transactions
measure 'Transaction Count' = COUNTROWS(Sales)
    formatString: #,##0
    displayFolder: Volume
    lineageTag: b2c3d4e5-f6a7-8901-bcde-f12345678901

/// Average transaction value
measure 'Average Transaction' = AVERAGE(Sales[Amount])
    formatString: $#,##0.00
    displayFolder: Revenue
    lineageTag: c3d4e5f6-a7b8-9012-cdef-123456789012

/// Minimum order amount
measure 'Min Order' = MIN(Sales[Amount])
    formatString: $#,##0.00
    displayFolder: Revenue
    lineageTag: d4e5f6a7-b8c9-0123-def0-234567890123

/// Maximum order amount
measure 'Max Order' = MAX(Sales[Amount])
    formatString: $#,##0.00
    displayFolder: Revenue
    lineageTag: e5f6a7b8-c9d0-1234-ef01-345678901234

/// Count of distinct customers
measure 'Customer Count' = DISTINCTCOUNT(Sales[CustomerKey])
    formatString: #,##0
    displayFolder: Customers
    lineageTag: f6a7b8c9-d0e1-2345-f012-456789012345
```

### CALCULATE with Filters

```tmdl
/// Sales for current year only
measure 'Current Year Sales' =
        CALCULATE(
            [Total Sales],
            YEAR(Calendar[Date]) = YEAR(TODAY())
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Filtered
    lineageTag: 01234567-89ab-cdef-0123-456789abcdef

/// Sales for specific product category
measure 'Electronics Sales' =
        CALCULATE(
            [Total Sales],
            Products[Category] = "Electronics"
        )
    formatString: $#,##0.00
    displayFolder: Revenue\By Category
    lineageTag: 12345678-9abc-def0-1234-56789abcdef0

/// Sales excluding returns
measure 'Net Sales' =
        CALCULATE(
            [Total Sales],
            Sales[TransactionType] <> "Return"
        )
    formatString: $#,##0.00
    displayFolder: Revenue
    lineageTag: 23456789-abcd-ef01-2345-6789abcdef01

/// Sales with multiple filters
measure 'Premium Customer Sales' =
        CALCULATE(
            [Total Sales],
            Customers[Segment] = "Premium",
            Sales[Amount] > 1000
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Segments
    lineageTag: 34567890-bcde-f012-3456-789abcdef012

/// All sales ignoring filters
measure 'Total Sales All' =
        CALCULATE(
            [Total Sales],
            ALL(Sales)
        )
    formatString: $#,##0.00
    displayFolder: Revenue
    lineageTag: 4567890a-cdef-0123-4567-89abcdef0123

/// Percentage of total
measure 'Sales % of Total' =
        DIVIDE(
            [Total Sales],
            [Total Sales All],
            0
        )
    formatString: 0.00%
    displayFolder: Revenue
    lineageTag: 567890ab-def0-1234-5678-9abcdef01234
```

### Time Intelligence Measures

```tmdl
/// Year-to-Date Sales
measure 'YTD Sales' =
        TOTALYTD(
            [Total Sales],
            Calendar[Date]
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: 67890abc-ef01-2345-6789-abcdef012345

/// Quarter-to-Date Sales
measure 'QTD Sales' =
        TOTALQTD(
            [Total Sales],
            Calendar[Date]
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: 7890abcd-f012-3456-789a-bcdef0123456

/// Month-to-Date Sales
measure 'MTD Sales' =
        TOTALMTD(
            [Total Sales],
            Calendar[Date]
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: 890abcde-0123-4567-89ab-cdef01234567

/// Prior Year Sales
measure 'PY Sales' =
        CALCULATE(
            [Total Sales],
            SAMEPERIODLASTYEAR(Calendar[Date])
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: 90abcdef-1234-5678-9abc-def012345678

/// Prior Year YTD Sales
measure 'PY YTD Sales' =
        CALCULATE(
            [YTD Sales],
            SAMEPERIODLASTYEAR(Calendar[Date])
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: 0abcdef0-2345-6789-abcd-ef0123456789

/// Year-over-Year Growth
measure 'YoY Growth' =
        var CurrentYear = [Total Sales]
        var PriorYear = [PY Sales]
        return
        CurrentYear - PriorYear
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: abcdef01-3456-789a-bcde-f01234567890

/// Year-over-Year Growth Percentage
measure 'YoY Growth %' =
        var CurrentYear = [Total Sales]
        var PriorYear = [PY Sales]
        return
        DIVIDE(
            CurrentYear - PriorYear,
            PriorYear,
            BLANK()
        )
    formatString: 0.00%;-0.00%;--
    displayFolder: Revenue\Time Intelligence
    lineageTag: bcdef012-4567-89ab-cdef-012345678901

/// Rolling 12 Month Sales
measure 'Rolling 12M Sales' =
        CALCULATE(
            [Total Sales],
            DATESINPERIOD(
                Calendar[Date],
                MAX(Calendar[Date]),
                -12,
                MONTH
            )
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: cdef0123-5678-9abc-def0-123456789012

/// Moving Average (3-Month)
measure '3M Moving Avg' =
        AVERAGEX(
            DATESINPERIOD(
                Calendar[Date],
                MAX(Calendar[Date]),
                -3,
                MONTH
            ),
            [Total Sales]
        )
    formatString: $#,##0.00
    displayFolder: Revenue\Time Intelligence
    lineageTag: def01234-6789-abcd-ef01-234567890123
```

### Variables and RETURN

```tmdl
/// Profit margin with variables
measure 'Profit Margin' =
        var TotalRevenue = [Total Sales]
        var TotalCost = SUMX(
            Sales,
            Sales[Quantity] * RELATED(Products[Unit Cost])
        )
        var Profit = TotalRevenue - TotalCost
        return
        DIVIDE(Profit, TotalRevenue, 0)
    formatString: 0.00%
    displayFolder: Profitability
    lineageTag: ef012345-789a-bcde-f012-345678901234

/// Complex ranking measure
measure 'Product Rank by Sales' =
        var CurrentSales = [Total Sales]
        var AllProductSales =
            ADDCOLUMNS(
                ALL(Products[Product Name]),
                "@Sales", [Total Sales]
            )
        var Rank =
            COUNTROWS(
                FILTER(
                    AllProductSales,
                    [@Sales] > CurrentSales
                )
            ) + 1
        return
        Rank
    formatString: #,##0
    displayFolder: Rankings
    lineageTag: f0123456-89ab-cdef-0123-456789abcdef

/// Sales contribution with early exit
measure 'Sales Contribution' =
        var TotalAllSales = [Total Sales All]
        return
        IF(
            ISBLANK(TotalAllSales),
            BLANK(),
            var CurrentSales = [Total Sales]
            return
            DIVIDE(CurrentSales, TotalAllSales)
        )
    formatString: 0.00%
    displayFolder: Revenue
    lineageTag: 01234567-9abc-def0-1234-56789abcdef0
```

### Format String Examples

```tmdl
/// Currency (US Dollars)
measure 'Revenue USD' = [Total Sales]
    formatString: $#,##0.00
    lineageTag: 12345678-abcd-ef01-2345-6789abcdef01

/// Currency (Euros)
measure 'Revenue EUR' = [Total Sales] * 0.92
    formatString: #,##0.00 "EUR"
    lineageTag: 2345678a-bcde-f012-3456-789abcdef012

/// Percentage with 1 decimal
measure 'Growth Rate' = 0.125
    formatString: 0.0%
    lineageTag: 345678ab-cdef-0123-4567-89abcdef0123

/// Percentage with pos/neg/zero
measure 'Change %' = [YoY Growth %]
    formatString: 0.00%;(0.00%);--
    lineageTag: 45678abc-def0-1234-5678-9abcdef01234

/// Whole number with thousands separator
measure 'Units Sold' = SUM(Sales[Quantity])
    formatString: #,##0
    lineageTag: 5678abcd-ef01-2345-6789-abcdef012345

/// Decimal with 4 places
measure 'Conversion Rate' = 0.0325
    formatString: 0.0000
    lineageTag: 678abcde-f012-3456-789a-bcdef0123456

/// Number with K/M/B suffix
measure 'Revenue Short' = [Total Sales]
    formatString: #,##0,,.0 "M"
    lineageTag: 78abcdef-0123-4567-89ab-cdef01234567

/// Custom text suffix
measure 'Days Outstanding' = 45
    formatString: #,##0 "days"
    lineageTag: 8abcdef0-1234-5678-9abc-def012345678
```

---

## 3. Relationship Examples

### One-to-Many Relationship

Standard dimension-to-fact relationship:

```tmdl
relationship 9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d
    fromColumn: Sales.ProductKey
    toColumn: Products.ProductKey

relationship 1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d
    fromColumn: Sales.CustomerKey
    toColumn: Customers.CustomerKey

relationship 2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e
    fromColumn: Sales.OrderDateKey
    toColumn: Calendar.DateKey
```

### Many-to-Many with Bridge Table

For scenarios where a single sale can have multiple salespeople:

```tmdl
/// Bridge table partition (in SalesSalesperson.tmdl)
table SalesSalesperson
    lineageTag: 3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f

    column SalesOrderID
        dataType: int64
        sourceColumn: SalesOrderID
        lineageTag: 4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a

    column SalespersonKey
        dataType: int64
        sourceColumn: SalespersonKey
        lineageTag: 5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b

    partition Bridge-Partition = m
        mode: import
        source =
            let
                Source = Sql.Database(#"Server Name", #"Database Name"),
                dbo_SalesSalesperson = Source{[Schema="dbo",Item="SalesSalesperson"]}[Data]
            in
                dbo_SalesSalesperson
```

```tmdl
/// In relationships.tmdl
/// Sales to Bridge (many-to-one)
relationship 6f7a8b9c-0d1e-2f3a-4b5c-6d7e8f9a0b1c
    fromColumn: Sales.SalesOrderID
    toColumn: SalesSalesperson.SalesOrderID

/// Bridge to Salesperson (many-to-one)
relationship 7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d
    fromColumn: SalesSalesperson.SalespersonKey
    toColumn: Salesperson.SalespersonKey
```

### Bi-Directional Filtering

Enable cross-filtering in both directions:

```tmdl
relationship 8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e
    fromColumn: Sales.ProductKey
    toColumn: Products.ProductKey
    crossFilteringBehavior: bothDirections
```

### Inactive Relationships

For role-playing dimensions (e.g., multiple date columns):

```tmdl
/// Active relationship - Order Date
relationship 9c0d1e2f-3a4b-5c6d-7e8f-9a0b1c2d3e4f
    fromColumn: Sales.OrderDateKey
    toColumn: Calendar.DateKey

/// Inactive relationship - Ship Date
relationship 0d1e2f3a-4b5c-6d7e-8f9a-0b1c2d3e4f5a
    fromColumn: Sales.ShipDateKey
    toColumn: Calendar.DateKey
    isActive: false

/// Inactive relationship - Due Date
relationship 1e2f3a4b-5c6d-7e8f-9a0b-1c2d3e4f5a6b
    fromColumn: Sales.DueDateKey
    toColumn: Calendar.DateKey
    isActive: false
```

To use inactive relationships in measures:

```tmdl
measure 'Sales by Ship Date' =
        CALCULATE(
            [Total Sales],
            USERELATIONSHIP(Sales[ShipDateKey], Calendar[DateKey])
        )
    formatString: $#,##0.00
    displayFolder: Revenue\By Date Type
    lineageTag: 2f3a4b5c-6d7e-8f9a-0b1c-2d3e4f5a6b7c
```

### Security Filtering Behavior

Control RLS filter propagation:

```tmdl
relationship 3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d
    fromColumn: Sales.CustomerKey
    toColumn: Customers.CustomerKey
    crossFilteringBehavior: bothDirections
    securityFilteringBehavior: oneDirection
```

---

## 4. Calculated Column Examples

### Date Calculations

```tmdl
/// Age calculation from birth date
column Age = DATEDIFF(Customers[BirthDate], TODAY(), YEAR)
    dataType: int64
    lineageTag: 4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e
    isDataTypeInferred

/// Days since last purchase
column 'Days Since Last Purchase' =
        DATEDIFF(
            Customers[LastPurchaseDate],
            TODAY(),
            DAY
        )
    dataType: int64
    lineageTag: 5c6d7e8f-9a0b-1c2d-3e4f-5a6b7c8d9e0f
    isDataTypeInferred

/// Fiscal year (July start)
column 'Fiscal Year' =
        var CalendarYear = YEAR(Calendar[Date])
        var CalendarMonth = MONTH(Calendar[Date])
        return
        IF(CalendarMonth >= 7, CalendarYear + 1, CalendarYear)
    dataType: int64
    lineageTag: 6d7e8f9a-0b1c-2d3e-4f5a-6b7c8d9e0f1a
    isDataTypeInferred

/// Week of year
column 'Week Number' = WEEKNUM(Calendar[Date], 2)
    dataType: int64
    lineageTag: 7e8f9a0b-1c2d-3e4f-5a6b-7c8d9e0f1a2b
    isDataTypeInferred
```

### Text Concatenation

```tmdl
/// Full name from first and last
column 'Full Name' = Customers[First Name] & " " & Customers[Last Name]
    dataType: string
    lineageTag: 8f9a0b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c
    isDataTypeInferred

/// Full address
column 'Full Address' =
        Customers[Street Address] & ", " &
        Customers[City] & ", " &
        Customers[State] & " " &
        Customers[Postal Code]
    dataType: string
    lineageTag: 9a0b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c4d
    isDataTypeInferred

/// Product code with category prefix
column 'Product Code' =
        LEFT(Products[Category], 3) & "-" &
        FORMAT(Products[ProductKey], "00000")
    dataType: string
    lineageTag: 0b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d5e
    isDataTypeInferred
```

### Conditional Columns (SWITCH, IF)

```tmdl
/// Customer segment based on total purchases
column 'Customer Segment' =
        var TotalPurchases = CALCULATE(SUM(Sales[Amount]))
        return
        SWITCH(
            TRUE(),
            TotalPurchases >= 10000, "Platinum",
            TotalPurchases >= 5000, "Gold",
            TotalPurchases >= 1000, "Silver",
            "Bronze"
        )
    dataType: string
    lineageTag: 1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e6f
    isDataTypeInferred

/// Age group classification
column 'Age Group' =
        SWITCH(
            TRUE(),
            Customers[Age] < 18, "Under 18",
            Customers[Age] < 25, "18-24",
            Customers[Age] < 35, "25-34",
            Customers[Age] < 45, "35-44",
            Customers[Age] < 55, "45-54",
            Customers[Age] < 65, "55-64",
            "65+"
        )
    dataType: string
    lineageTag: 2d3e4f5a-6b7c-8d9e-0f1a-2b3c4d5e6f7a
    isDataTypeInferred

/// Simple IF condition
column 'Is High Value' = IF(Sales[Amount] > 1000, "Yes", "No")
    dataType: string
    lineageTag: 3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b
    isDataTypeInferred

/// Nested IF for priority
column Priority =
        IF(
            Orders[IsUrgent] = TRUE(),
            "High",
            IF(
                Orders[DueDate] <= TODAY() + 7,
                "Medium",
                "Low"
            )
        )
    dataType: string
    lineageTag: 4f5a6b7c-8d9e-0f1a-2b3c-4d5e6f7a8b9c
    isDataTypeInferred
```

### Numeric Calculations

```tmdl
/// Line item total with discount
column 'Line Total' = Sales[Quantity] * Sales[Unit Price] * (1 - Sales[Discount Pct])
    dataType: decimal
    formatString: $#,##0.00
    lineageTag: 5a6b7c8d-9e0f-1a2b-3c4d-5e6f7a8b9c0d
    isDataTypeInferred

/// Profit calculation using RELATED
column 'Line Profit' =
        Sales[Quantity] * (Sales[Unit Price] - RELATED(Products[Unit Cost]))
    dataType: decimal
    formatString: $#,##0.00
    lineageTag: 6b7c8d9e-0f1a-2b3c-4d5e-6f7a8b9c0d1e
    isDataTypeInferred

/// Rounded value
column 'Rounded Amount' = ROUND(Sales[Amount], 0)
    dataType: int64
    lineageTag: 7c8d9e0f-1a2b-3c4d-5e6f-7a8b9c0d1e2f
    isDataTypeInferred
```

---

## 5. Calculation Group Examples

### Time Intelligence Calculation Group

A comprehensive calculation group for time intelligence patterns:

```tmdl
table 'Time Intelligence'
    lineageTag: 8d9e0f1a-2b3c-4d5e-6f7a-8b9c0d1e2f3a

    calculationGroup
        precedence: 20

        /// Current period - no modification
        calculationItem Current = SELECTEDMEASURE()
            ordinal: 0

        /// Month-to-Date
        calculationItem MTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESMTD('Calendar'[Date])
                )
            ordinal: 1

        /// Quarter-to-Date
        calculationItem QTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESQTD('Calendar'[Date])
                )
            ordinal: 2

        /// Year-to-Date
        calculationItem YTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESYTD('Calendar'[Date])
                )
            ordinal: 3

        /// Prior Year
        calculationItem PY =
                CALCULATE(
                    SELECTEDMEASURE(),
                    SAMEPERIODLASTYEAR('Calendar'[Date])
                )
            ordinal: 4

        /// Prior Year YTD
        calculationItem 'PY YTD' =
                CALCULATE(
                    SELECTEDMEASURE(),
                    SAMEPERIODLASTYEAR('Calendar'[Date]),
                    'Time Intelligence'[Time Calculation] = "YTD"
                )
            ordinal: 5

        /// Year-over-Year Change
        calculationItem YoY =
                var CurrentValue = SELECTEDMEASURE()
                var PriorValue = CALCULATE(
                    SELECTEDMEASURE(),
                    'Time Intelligence'[Time Calculation] = "PY"
                )
                return
                CurrentValue - PriorValue
            ordinal: 6

        /// Year-over-Year Percentage Change
        calculationItem 'YoY %' =
                var CurrentValue = SELECTEDMEASURE()
                var PriorValue = CALCULATE(
                    SELECTEDMEASURE(),
                    'Time Intelligence'[Time Calculation] = "PY"
                )
                return
                DIVIDE(
                    CurrentValue - PriorValue,
                    PriorValue,
                    BLANK()
                )
            ordinal: 7
            formatStringDefinition = "0.00%;-0.00%;--"

        /// YTD Year-over-Year Change
        calculationItem 'YTD YoY' =
                var CurrentYTD = CALCULATE(
                    SELECTEDMEASURE(),
                    'Time Intelligence'[Time Calculation] = "YTD"
                )
                var PriorYTD = CALCULATE(
                    SELECTEDMEASURE(),
                    'Time Intelligence'[Time Calculation] = "PY YTD"
                )
                return
                CurrentYTD - PriorYTD
            ordinal: 8

        /// YTD Year-over-Year Percentage
        calculationItem 'YTD YoY %' =
                var CurrentYTD = CALCULATE(
                    SELECTEDMEASURE(),
                    'Time Intelligence'[Time Calculation] = "YTD"
                )
                var PriorYTD = CALCULATE(
                    SELECTEDMEASURE(),
                    'Time Intelligence'[Time Calculation] = "PY YTD"
                )
                return
                DIVIDE(
                    CurrentYTD - PriorYTD,
                    PriorYTD,
                    BLANK()
                )
            ordinal: 9
            formatStringDefinition = "0.00%;-0.00%;--"

    column 'Time Calculation'
        dataType: string
        sourceColumn: Name
        sortByColumn: Ordinal
        lineageTag: 9e0f1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b

    column Ordinal
        dataType: int64
        isHidden
        sourceColumn: Ordinal
        lineageTag: 0f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c
```

### Currency Conversion Calculation Group

For multi-currency reporting:

```tmdl
table 'Currency Conversion'
    lineageTag: 1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d

    calculationGroup
        precedence: 10

        /// Original currency - no conversion
        calculationItem 'Original Currency' = SELECTEDMEASURE()
            ordinal: 0

        /// Convert to reporting currency
        calculationItem 'Reporting Currency' =
                var OriginalValue = SELECTEDMEASURE()
                var SelectedCurrency = SELECTEDVALUE(
                    Currency[Currency Code],
                    "USD"
                )
                return
                IF(
                    SelectedCurrency = "USD",
                    OriginalValue,
                    SUMX(
                        VALUES('Calendar'[Date]),
                        var DailyValue = CALCULATE(SELECTEDMEASURE())
                        var ExchangeRate = CALCULATE(
                            MAX('Exchange Rates'[Rate to USD])
                        )
                        return
                        DailyValue * ExchangeRate
                    )
                )
            ordinal: 1
            formatStringDefinition =
                    SELECTEDVALUE(
                        Currency[Format String],
                        SELECTEDMEASUREFORMATSTRING()
                    )

        /// Convert to EUR
        calculationItem EUR =
                var USDValue = CALCULATE(
                    SELECTEDMEASURE(),
                    'Currency Conversion'[Conversion] = "Reporting Currency"
                )
                var EURRate = CALCULATE(
                    MAX('Exchange Rates'[Rate to EUR]),
                    'Exchange Rates'[Currency Code] = "USD"
                )
                return
                USDValue * EURRate
            ordinal: 2
            formatStringDefinition = "#,##0.00 EUR"

        /// Convert to GBP
        calculationItem GBP =
                var USDValue = CALCULATE(
                    SELECTEDMEASURE(),
                    'Currency Conversion'[Conversion] = "Reporting Currency"
                )
                var GBPRate = CALCULATE(
                    MAX('Exchange Rates'[Rate to GBP]),
                    'Exchange Rates'[Currency Code] = "USD"
                )
                return
                USDValue * GBPRate
            ordinal: 3
            formatStringDefinition = "#,##0.00 GBP"

    column Conversion
        dataType: string
        sourceColumn: Name
        sortByColumn: Ordinal
        lineageTag: 2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e

    column Ordinal
        dataType: int64
        isHidden
        sourceColumn: Ordinal
        lineageTag: 3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f
```

### Measure Selection Calculation Group

For comparing different measures:

```tmdl
table 'Measure Selection'
    lineageTag: 4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a

    calculationGroup
        precedence: 5

        calculationItem Revenue =
                IF(
                    ISSELECTEDMEASURE([Base Measure]),
                    [Total Sales],
                    SELECTEDMEASURE()
                )
            ordinal: 0

        calculationItem Profit =
                IF(
                    ISSELECTEDMEASURE([Base Measure]),
                    [Total Profit],
                    SELECTEDMEASURE()
                )
            ordinal: 1

        calculationItem 'Unit Sales' =
                IF(
                    ISSELECTEDMEASURE([Base Measure]),
                    [Total Quantity],
                    SELECTEDMEASURE()
                )
            ordinal: 2

        calculationItem 'Order Count' =
                IF(
                    ISSELECTEDMEASURE([Base Measure]),
                    [Order Count],
                    SELECTEDMEASURE()
                )
            ordinal: 3

    column Selection
        dataType: string
        sourceColumn: Name
        sortByColumn: Ordinal
        lineageTag: 5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b

    column Ordinal
        dataType: int64
        isHidden
        sourceColumn: Ordinal
        lineageTag: 6f7a8b9c-0d1e-2f3a-4b5c-6d7e8f9a0b1c
```

---

## 6. RLS Role Examples

### Simple Filter Expression

Basic static RLS filtering:

```tmdl
/// North America region access only
role 'North America Sales'
    modelPermission: read

    tablePermission Sales = Sales[Region] = "North America"

/// Restrict to specific product categories
role 'Consumer Products'
    modelPermission: read

    tablePermission Products = Products[Category] IN {"Electronics", "Home & Garden", "Clothing"}
    tablePermission Sales = TRUE()
```

### Dynamic RLS with USERNAME()

Filter based on the logged-in user:

```tmdl
/// Sales reps see only their own sales
role 'Sales Representative'
    modelPermission: read

    tablePermission Sales =
            Sales[SalesRepEmail] = USERPRINCIPALNAME()

/// Managers see their team's sales
role 'Sales Manager'
    modelPermission: read

    tablePermission Sales =
            var CurrentUser = USERPRINCIPALNAME()
            var ManagerTeam = CALCULATETABLE(
                VALUES(Employees[Email]),
                Employees[ManagerEmail] = CurrentUser
            )
            return
            Sales[SalesRepEmail] IN ManagerTeam ||
            Sales[SalesRepEmail] = CurrentUser
```

### Dynamic RLS with Lookup Table

Using a security mapping table:

```tmdl
/// First, create a security mapping table
table UserSecurityMapping
    lineageTag: 7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d

    column UserEmail
        dataType: string
        sourceColumn: UserEmail
        lineageTag: 8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e

    column RegionAccess
        dataType: string
        sourceColumn: RegionAccess
        lineageTag: 9c0d1e2f-3a4b-5c6d-7e8f-9a0b1c2d3e4f

    partition UserSecurityMapping-Partition = m
        mode: import
        source =
            let
                Source = Excel.Workbook(File.Contents("SecurityMapping.xlsx")),
                UserAccess = Source{[Item="UserAccess",Kind="Sheet"]}[Data]
            in
                UserAccess
```

```tmdl
/// Role using the security mapping
role 'Regional Access'
    modelPermission: read

    tablePermission Sales =
            var CurrentUser = USERPRINCIPALNAME()
            var AllowedRegions = CALCULATETABLE(
                VALUES(UserSecurityMapping[RegionAccess]),
                UserSecurityMapping[UserEmail] = CurrentUser
            )
            return
            Sales[Region] IN AllowedRegions
```

### Multiple Table Permissions

Complex RLS with multiple filtered tables:

```tmdl
role 'Territory Manager'
    modelPermission: read

    /// Filter sales by territory
    tablePermission Sales =
            var CurrentUser = USERPRINCIPALNAME()
            var UserTerritories = CALCULATETABLE(
                VALUES(TerritoryAssignments[TerritoryID]),
                TerritoryAssignments[ManagerEmail] = CurrentUser
            )
            return
            Sales[TerritoryID] IN UserTerritories

    /// Filter customers to those in assigned territories
    tablePermission Customers =
            var CurrentUser = USERPRINCIPALNAME()
            var UserTerritories = CALCULATETABLE(
                VALUES(TerritoryAssignments[TerritoryID]),
                TerritoryAssignments[ManagerEmail] = CurrentUser
            )
            return
            Customers[TerritoryID] IN UserTerritories

    /// Allow all products (no filter)
    tablePermission Products = TRUE()

    /// Filter employees to direct reports only
    tablePermission Employees =
            Employees[ManagerEmail] = USERPRINCIPALNAME() ||
            Employees[Email] = USERPRINCIPALNAME()
```

### Deny All Access Pattern

Explicitly deny access to sensitive data:

```tmdl
role 'Limited Access'
    modelPermission: read

    /// Allow sales data
    tablePermission Sales = TRUE()

    /// Deny access to customer PII
    tablePermission 'Customer PII' = FALSE()

    /// Deny access to financial data
    tablePermission 'Financial Details' = FALSE()
```

---

## 7. Named Expression Examples

### Connection Parameters

```tmdl
/// Server connection parameter
expression ServerName = "sql-prod-01.database.windows.net" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

/// Database name parameter
expression DatabaseName = "ContosoRetailDW" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

/// Environment parameter for dev/test/prod
expression Environment = "Production" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=false]
```

### Date Parameters

```tmdl
/// Start date for data refresh
expression StartDate = #date(2020, 1, 1) meta [IsParameterQuery=true, Type="Date"]

/// End date (dynamic - today)
expression EndDate =
        Date.From(DateTime.LocalNow())
    meta [IsParameterQuery=true, Type="Date"]

/// Fiscal year start month
expression FiscalYearStartMonth = 7 meta [IsParameterQuery=true, Type="Number"]
```

### Shared Queries

```tmdl
/// Shared database connection
expression DatabaseConnection =
        let
            Source = Sql.Database(ServerName, DatabaseName)
        in
            Source

/// Shared date filtering function
expression FilterByDateRange =
        (table as table, dateColumn as text) =>
        let
            Filtered = Table.SelectRows(
                table,
                each Record.Field(_, dateColumn) >= StartDate and
                     Record.Field(_, dateColumn) <= EndDate
            )
        in
            Filtered
```

### Environment-Specific Configuration

```tmdl
/// Connection string based on environment
expression ConnectionString =
        let
            ServerMap = [
                Development = "sql-dev.database.windows.net",
                Test = "sql-test.database.windows.net",
                Production = "sql-prod.database.windows.net"
            ],
            SelectedServer = Record.Field(ServerMap, Environment)
        in
            SelectedServer
    meta [IsParameterQuery=false]
```

---

## Best Practices Summary

### Measure Organization

1. Use `displayFolder` with backslash separators for hierarchy: `Revenue\Time Intelligence`
2. Include `///` descriptions for complex measures
3. Use consistent naming: `Total X`, `X %`, `X YTD`, `X vs PY`

### LineageTag Management

1. Generate new GUIDs for new objects only
2. Preserve lineageTags when renaming objects
3. Never duplicate lineageTags between objects

### Calculation Groups

1. Set appropriate `precedence` (higher = applied later)
2. Include `ordinal` for consistent ordering
3. Use `formatStringDefinition` for percentage calculations

### RLS Security

1. Test roles with "View as Role" in Power BI Desktop
2. Use `USERPRINCIPALNAME()` for Azure AD integration
3. Consider lookup tables for complex security mappings
4. Document security requirements in role descriptions

---

## References

- [Microsoft TMDL Documentation](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview)
- [DAX Reference](https://learn.microsoft.com/en-us/dax/)
- [Calculation Groups Documentation](https://learn.microsoft.com/en-us/analysis-services/tabular-models/calculation-groups)
- [Row-Level Security](https://learn.microsoft.com/en-us/power-bi/enterprise/service-admin-rls)
