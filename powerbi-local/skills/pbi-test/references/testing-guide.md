# Power BI Testing Methodology Guide

Comprehensive testing methodology for Power BI measures, visuals, relationships, and security roles.

## Table of Contents

1. [DAX Query Patterns for Testing](#1-dax-query-patterns-for-testing)
2. [Screenshot Comparison Techniques](#2-screenshot-comparison-techniques)
3. [Filter Testing Procedures](#3-filter-testing-procedures)
4. [Relationship Validation Queries](#4-relationship-validation-queries)
5. [Common Test Scenarios](#5-common-test-scenarios)
6. [Performance Testing](#6-performance-testing)
7. [RLS Testing](#7-rls-testing)

---

## 1. DAX Query Patterns for Testing

### Basic Measure Evaluation

Test a measure without any filter context to get the grand total:

```dax
EVALUATE
ROW("Measure Name", [Your Measure])
```

### Single Dimension Test

Test measure against a single dimension:

```dax
EVALUATE
ADDCOLUMNS(
    VALUES(DimensionTable[Column]),
    "Measure Value", [Your Measure]
)
ORDER BY DimensionTable[Column]
```

### Multi-Dimension Test

Test measure across multiple dimensions:

```dax
EVALUATE
SUMMARIZECOLUMNS(
    Dimension1[Column1],
    Dimension2[Column2],
    "Measure", [Your Measure]
)
ORDER BY Dimension1[Column1], Dimension2[Column2]
```

### Filtered Context Test

Test with specific filter applied:

```dax
EVALUATE
CALCULATETABLE(
    ROW("Result", [Your Measure]),
    Table[Column] = "FilterValue"
)
```

### Time Intelligence Test Pattern

Comprehensive time intelligence test:

```dax
EVALUATE
VAR CurrentYear = YEAR(TODAY())
RETURN
ADDCOLUMNS(
    FILTER(
        CROSSJOIN(
            VALUES('Calendar'[Year]),
            VALUES('Calendar'[MonthName])
        ),
        'Calendar'[Year] >= CurrentYear - 2
    ),
    "Sales", [Total Sales],
    "YTD", [YTD Sales],
    "PY", [PY Sales],
    "YoY %", [YoY Growth]
)
ORDER BY 'Calendar'[Year], 'Calendar'[MonthNumber]
```

### Edge Case Tests

**Empty result test:**
```dax
EVALUATE
CALCULATETABLE(
    ROW("Result", [Your Measure]),
    FILTER(ALL(Table), FALSE())  -- Forces empty context
)
```

**Null handling test:**
```dax
EVALUATE
ROW(
    "With Nulls", CALCULATE([Your Measure], Table[Column] = BLANK()),
    "Without Nulls", CALCULATE([Your Measure], Table[Column] <> BLANK())
)
```

**Division by zero test:**
```dax
EVALUATE
ROW(
    "Normal", DIVIDE(100, 10),
    "Zero Divisor", DIVIDE(100, 0),
    "Zero Divisor Alt", DIVIDE(100, 0, -1)  -- Returns alternate
)
```

### Comparison Test Pattern

Compare measure against expected or baseline:

```dax
EVALUATE
VAR Actual = [Your Measure]
VAR Expected = 12345.67  -- Known expected value
VAR Tolerance = 0.01
RETURN
ROW(
    "Actual", Actual,
    "Expected", Expected,
    "Difference", Actual - Expected,
    "Pass", IF(ABS(Actual - Expected) <= Tolerance, "YES", "NO")
)
```

---

## 2. Screenshot Comparison Techniques

### Visual Verification Workflow

1. **Capture baseline screenshot** before making changes
2. **Make the change** (add measure, modify visual, etc.)
3. **Capture comparison screenshot** after change
4. **Compare visually** for expected differences

### What to Look For

| Visual Element | Check For |
|----------------|-----------|
| **Data values** | Correct numbers displayed |
| **Formatting** | Currency, percentage, decimal places |
| **Colors** | Conditional formatting applied correctly |
| **Labels** | Axis labels, data labels, legends |
| **Layout** | Visual size, position, alignment |
| **Interactions** | Cross-filtering effects |
| **Error states** | No error icons or broken visuals |

### Screenshot Checklist

When taking screenshots for verification:

- [ ] Report page is fully loaded (no spinning indicators)
- [ ] Visual is not selected (to see actual render, not selection handles)
- [ ] Slicers are set to expected values
- [ ] No dialogs or popups obscuring the view
- [ ] Zoom level is at 100% for consistent comparison
- [ ] If testing mobile layout, capture mobile preview

### Testing Visual Interactions

To test cross-filtering:

1. Screenshot the page in default state
2. Click on a data point in one visual
3. Screenshot the page showing filtered state
4. Verify other visuals updated appropriately

### Testing Drill-Down

1. Screenshot visual at top level
2. Right-click and drill down
3. Screenshot at each drill level
4. Verify data changes as expected per level

---

## 3. Filter Testing Procedures

### Filter Propagation Test

Verify filters flow correctly through relationships:

```dax
EVALUATE
VAR TotalUnfiltered = CALCULATE([Your Measure], ALL(DimTable))
VAR TotalFiltered = [Your Measure]
RETURN
ROW(
    "Unfiltered Total", TotalUnfiltered,
    "Filtered Total", TotalFiltered,
    "Filter Active", IF(TotalFiltered <> TotalUnfiltered, "YES", "NO")
)
```

### Slicer Effect Test

Test that slicer selections affect measures:

```dax
-- First, query without filter
EVALUATE ROW("No Filter", [Total Sales])

-- Then with filter (simulating slicer)
EVALUATE ROW("With Filter", CALCULATE([Total Sales], Product[Category] = "Electronics"))
```

### Visual Level Filter Test

Verify visual-level filters work:

```dax
-- Simulate visual-level filter
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        Product[Category],
        "Sales", [Total Sales]
    ),
    Product[Category] IN {"Electronics", "Clothing"}  -- Visual filter
)
```

### Page Level Filter Test

```dax
-- Page filter simulation
EVALUATE
CALCULATETABLE(
    ADDCOLUMNS(
        VALUES('Calendar'[Year]),
        "Sales", [Total Sales]
    ),
    'Calendar'[Year] >= 2022  -- Page filter
)
```

### Report Level Filter Test

```dax
-- Report filter simulation (typically status = active)
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        Store[Region],
        "Sales", [Total Sales]
    ),
    Store[Status] = "Active"  -- Report filter
)
```

### Filter Combination Test

Test multiple filters together:

```dax
EVALUATE
ROW(
    "No Filters", CALCULATE([Total Sales], ALL()),
    "Filter 1 Only", CALCULATE([Total Sales], Product[Category] = "A"),
    "Filter 2 Only", CALCULATE([Total Sales], 'Calendar'[Year] = 2024),
    "Both Filters", CALCULATE([Total Sales], Product[Category] = "A", 'Calendar'[Year] = 2024)
)
```

---

## 4. Relationship Validation Queries

### Relationship Existence Test

Check that related data can be accessed:

```dax
EVALUATE
TOPN(5,
    ADDCOLUMNS(
        FactTable,
        "Related Value", RELATED(DimTable[ColumnName])
    )
)
```

### Cardinality Test

Verify one-to-many relationship:

```dax
EVALUATE
VAR DimCount = COUNTROWS(DimTable)
VAR FactWithMatch = COUNTROWS(FILTER(FactTable, NOT ISBLANK(RELATED(DimTable[Key]))))
RETURN
ROW(
    "Dimension Rows", DimCount,
    "Fact Rows with Match", FactWithMatch,
    "Fact Rows Total", COUNTROWS(FactTable),
    "Orphan Facts", COUNTROWS(FactTable) - FactWithMatch
)
```

### Many-to-Many Bridge Test

For M:M relationships through bridge table:

```dax
EVALUATE
ROW(
    "Table A Count", COUNTROWS(TableA),
    "Table B Count", COUNTROWS(TableB),
    "Bridge Count", COUNTROWS(BridgeTable),
    "A to B Connections", CALCULATE(COUNTROWS(BridgeTable), TableA[ID] <> BLANK()),
    "B to A Connections", CALCULATE(COUNTROWS(BridgeTable), TableB[ID] <> BLANK())
)
```

### Cross-Filter Direction Test

Test single vs bidirectional filtering:

```dax
-- With single direction (default)
EVALUATE
ROW(
    "Filter Dim -> Fact", CALCULATE(COUNTROWS(FactTable), DimTable[Category] = "A"),
    "Filter Fact -> Dim", CALCULATE(COUNTROWS(DimTable), FactTable[Amount] > 1000)
)
-- Second row may be unexpected if single direction
```

### Inactive Relationship Test

```dax
EVALUATE
ROW(
    "Active Relationship", [Sales by Order Date],
    "Inactive Relationship", CALCULATE(
        [Total Sales],
        USERELATIONSHIP(FactTable[ShipDate], 'Calendar'[Date])
    )
)
```

### Referential Integrity Test

Check for orphan keys:

```dax
EVALUATE
VAR OrphanFacts =
    COUNTROWS(
        FILTER(
            FactTable,
            ISBLANK(RELATED(DimTable[Key]))
        )
    )
VAR TotalFacts = COUNTROWS(FactTable)
RETURN
ROW(
    "Orphan Records", OrphanFacts,
    "Total Records", TotalFacts,
    "Integrity %", DIVIDE(TotalFacts - OrphanFacts, TotalFacts)
)
```

---

## 5. Common Test Scenarios

### Scenario: New Sales Measure

**Test plan:**

```dax
-- 1. Basic functionality
EVALUATE ROW("Total Sales", [Total Sales])

-- 2. By product category
EVALUATE SUMMARIZECOLUMNS(Product[Category], "Sales", [Total Sales])

-- 3. By time
EVALUATE SUMMARIZECOLUMNS('Calendar'[Year], 'Calendar'[Month], "Sales", [Total Sales])

-- 4. Null handling
EVALUATE ROW("Null Products", CALCULATE([Total Sales], Product[Category] = BLANK()))

-- 5. Verify against raw data
EVALUATE ROW(
    "Measure", [Total Sales],
    "Raw SUM", SUM(Sales[Amount]),
    "Match", IF([Total Sales] = SUM(Sales[Amount]), "YES", "NO")
)
```

### Scenario: YoY Growth Measure

**Test plan:**

```dax
-- 1. Verify PY exists
EVALUATE ROW(
    "CY Sales", [Total Sales],
    "PY Sales", [PY Sales],
    "Has PY Data", IF([PY Sales] > 0, "YES", "NO")
)

-- 2. Calculate expected YoY
EVALUATE
VAR CY = [Total Sales]
VAR PY = [PY Sales]
VAR ExpectedYoY = DIVIDE(CY - PY, PY)
RETURN
ROW(
    "CY", CY,
    "PY", PY,
    "Calculated YoY", ExpectedYoY,
    "Measure YoY", [YoY Growth],
    "Match", IF(ABS(ExpectedYoY - [YoY Growth]) < 0.0001, "YES", "NO")
)

-- 3. Test across years
EVALUATE
ADDCOLUMNS(
    VALUES('Calendar'[Year]),
    "YoY", [YoY Growth]
)
```

### Scenario: New Column Chart Visual

**Test plan:**

1. Verify JSON validates against schema
2. Screenshot: Visual renders without error
3. Test: All category values appear on axis
4. Test: Values match expected measure results
5. Test: Cross-filtering works with slicers
6. Test: Tooltip shows correct data

**DAX to verify data:**
```dax
-- Compare visual data to query
EVALUATE
SUMMARIZECOLUMNS(
    CategoryTable[CategoryName],
    "Chart Value", [Measure Used in Chart]
)
ORDER BY CategoryTable[CategoryName]
```

### Scenario: New Relationship

**Test plan:**

```dax
-- 1. Verify relationship exists
EVALUATE TOPN(3, ADDCOLUMNS(FactTable, "Related", RELATED(DimTable[Key])))

-- 2. Test filter propagation
EVALUATE ROW(
    "Filtered via Dim", CALCULATE(COUNTROWS(FactTable), DimTable[Status] = "Active")
)

-- 3. Check for orphans
EVALUATE ROW(
    "Orphans", COUNTROWS(FILTER(FactTable, ISBLANK(RELATED(DimTable[Key]))))
)

-- 4. Verify counts
EVALUATE ROW(
    "Dim Count", COUNTROWS(DimTable),
    "Fact Count", COUNTROWS(FactTable),
    "Matched Facts", COUNTROWS(FILTER(FactTable, NOT ISBLANK(RELATED(DimTable[Key]))))
)
```

### Scenario: RLS Role

**Test plan:**

```dax
-- 1. Count total rows
EVALUATE ROW("All Rows", COUNTROWS(ALL(FactTable)))

-- 2. Simulate RLS filter
EVALUATE ROW(
    "With RLS", CALCULATE(
        COUNTROWS(FactTable),
        DimTable[Region] = "North"  -- Simulate RLS filter
    )
)

-- 3. Verify data isolation
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        DimTable[Region],
        "Rows", COUNTROWS(FactTable)
    ),
    DimTable[Region] = "North"
)
```

---

## 6. Performance Testing

### Measure Performance Test

```dax
-- Use DAX Studio for actual timing
-- In MCP, observe response time

EVALUATE
VAR Start = NOW()
VAR Result = [Complex Measure]
RETURN
ROW(
    "Result", Result,
    "Timestamp", Start
)
```

### Query Complexity Test

Test measure at various granularities:

```dax
-- Low granularity (fast)
EVALUATE ROW("Total", [Your Measure])

-- Medium granularity
EVALUATE SUMMARIZECOLUMNS(Category[Name], "Value", [Your Measure])

-- High granularity (may be slow)
EVALUATE SUMMARIZECOLUMNS(
    'Calendar'[Date],
    Product[SKU],
    Store[StoreID],
    "Value", [Your Measure]
)
```

### Cardinality Impact Test

```dax
EVALUATE
ROW(
    "Low Cardinality", CALCULATE([Your Measure], VALUES(Dim[LowCardCol])),
    "High Cardinality", CALCULATE([Your Measure], VALUES(Dim[HighCardCol]))
)
```

---

## 7. RLS Testing

### Basic RLS Test

```dax
-- Test what user would see
EVALUATE
CALCULATETABLE(
    TOPN(10, FactTable),
    DimTable[UserRegion] = "USERPRINCIPALNAME()"  -- Replace with actual email
)
```

### Multi-Role Test

```dax
-- Test each role separately
-- Role: SalesManager
EVALUATE ROW(
    "SalesManager View", CALCULATE(
        COUNTROWS(Sales),
        Sales[Territory] IN {"North", "South"}
    )
)

-- Role: RegionalManager
EVALUATE ROW(
    "RegionalManager View", CALCULATE(
        COUNTROWS(Sales),
        Geography[Region] = "West"
    )
)
```

### RLS with Hierarchy Test

```dax
-- Manager sees team data
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        Employee[Name],
        "Sales", [Total Sales]
    ),
    PATHCONTAINS(Employee[ManagerPath], "current-user-id")
)
```

### Dynamic RLS Test

```dax
-- Test DAX-based RLS
EVALUATE
VAR UserEmail = "user@domain.com"  -- Test user
RETURN
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        DimTable[Region],
        "Rows", COUNTROWS(FactTable)
    ),
    FILTER(
        SecurityTable,
        SecurityTable[Email] = UserEmail
    )
)
```

---

## Quick Reference: Test Query Templates

### Single Measure
```dax
EVALUATE ROW("Result", [MeasureName])
```

### Measure by Dimension
```dax
EVALUATE SUMMARIZECOLUMNS(Dim[Col], "Value", [Measure])
```

### Filtered Measure
```dax
EVALUATE CALCULATETABLE(ROW("Result", [Measure]), Table[Col] = "Value")
```

### Compare Two Measures
```dax
EVALUATE ROW("A", [MeasureA], "B", [MeasureB], "Diff", [MeasureA] - [MeasureB])
```

### Time Series
```dax
EVALUATE ADDCOLUMNS(VALUES('Calendar'[Year]), "Value", [Measure])
```

### Relationship Check
```dax
EVALUATE TOPN(5, ADDCOLUMNS(Fact, "Related", RELATED(Dim[Key])))
```

### Orphan Check
```dax
EVALUATE ROW("Orphans", COUNTROWS(FILTER(Fact, ISBLANK(RELATED(Dim[Key])))))
```
