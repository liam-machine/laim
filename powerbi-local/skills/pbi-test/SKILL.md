---
name: pbi-test
description: >
  Verify that newly developed Power BI features work as expected.
  Triggers on "test measure", "verify calculation", "check visual",
  "does this work", "test relationship", "validate DAX", "is it correct".
auto_trigger: true
---

# Power BI Testing

Verify Power BI measures, visuals, relationships, and calculations work as expected.

## Testing Methods

| Test Type | Method | When to Use |
|-----------|--------|-------------|
| Measure validation | MCP `execute_dax` | Verify DAX calculations |
| Visual verification | Computer use (screenshots) | Confirm visual renders correctly |
| Relationship testing | DAX filter propagation queries | Verify relationships work |
| RLS testing | MCP `execute_dax` with USERPRINCIPALNAME | Test security roles |
| Cross-validation | Compare to expected values | Validate against known data |

## Testing Measures

### Basic Measure Test

Use MCP `execute_dax` to evaluate a measure without filter context:

```dax
EVALUATE
ROW("Measure Name", [Your Measure Name])
```

### Test with Specific Filter Context

```dax
EVALUATE
CALCULATETABLE(
    ROW("Result", [Your Measure]),
    'Calendar'[Year] = 2024,
    'Product'[Category] = "Electronics"
)
```

### Compare Multiple Measures

```dax
EVALUATE
ROW(
    "Total Sales", [Total Sales],
    "Total Cost", [Total Cost],
    "Profit", [Total Sales] - [Total Cost],
    "Margin %", DIVIDE([Total Sales] - [Total Cost], [Total Sales])
)
```

### Test Time Intelligence

```dax
EVALUATE
ADDCOLUMNS(
    VALUES('Calendar'[Year]),
    "YTD Sales", [YTD Sales],
    "PY Sales", [PY Sales],
    "YoY Growth", [YoY Growth]
)
ORDER BY 'Calendar'[Year]
```

### Test with Multiple Dimensions

```dax
EVALUATE
SUMMARIZECOLUMNS(
    'Product'[Category],
    'Geography'[Region],
    "Sales", [Total Sales],
    "Orders", [Order Count]
)
```

## Testing Visuals

### Using Computer Use (Screenshots)

1. **Open Power BI Desktop** with the report loaded
2. **Navigate to the page** containing the visual
3. **Take a screenshot** using computer use capability
4. **Verify**:
   - Visual renders without errors
   - Data appears correctly
   - Formatting matches expectations
   - Labels and titles display properly

### Visual Checklist

- [ ] Visual renders (no error icon)
- [ ] Title displays correctly
- [ ] Data labels show expected values
- [ ] Legend appears if configured
- [ ] Axis labels are readable
- [ ] Colors match theme/expectations
- [ ] Cross-filtering works with other visuals

## Testing Relationships

### Verify Filter Propagation

Test that relationships correctly filter data:

```dax
// Count should be same from both tables if relationship works
EVALUATE
ROW(
    "Sales Count", COUNTROWS(Sales),
    "Sales via Date", CALCULATE(COUNTROWS(Sales), 'Calendar'[Year] = 2024),
    "Dates in 2024", CALCULATE(COUNTROWS('Calendar'), 'Calendar'[Year] = 2024)
)
```

### Check Bidirectional Filtering

```dax
// If relationship is bidirectional, both should filter each other
EVALUATE
ROW(
    "Products with Sales", COUNTROWS(FILTER(Products, [Total Sales] > 0)),
    "Sales with Products", COUNTROWS(FILTER(Sales, RELATED(Products[ProductName]) <> BLANK()))
)
```

### Test Inactive Relationships

```dax
// Use USERELATIONSHIP to test inactive relationships
EVALUATE
ROW(
    "Sales by Order Date", [Total Sales],
    "Sales by Ship Date", CALCULATE([Total Sales], USERELATIONSHIP(Sales[ShipDate], 'Calendar'[Date]))
)
```

### Detect Ambiguous Relationships

```dax
// If this returns unexpected results, check for ambiguous paths
EVALUATE
SUMMARIZECOLUMNS(
    'Calendar'[Year],
    "Sales", [Total Sales],
    "Cost", [Total Cost]
)
```

## Testing RLS

### Test RLS Filter Expression

```dax
// Simulate RLS filter for a specific user
EVALUATE
CALCULATETABLE(
    TOPN(10, Sales),
    PATHCONTAINS("domain\username", [Region])
)
```

### Verify Row Count with RLS

```dax
// Compare total vs filtered
EVALUATE
ROW(
    "All Rows", COUNTROWS(ALL(Sales)),
    "Visible Rows", COUNTROWS(Sales)
)
```

## Cross-Validation Techniques

### Compare Aggregations

```dax
// Sum of parts should equal total
EVALUATE
ROW(
    "Total", [Total Sales],
    "Sum of Categories", SUMX(VALUES(Product[Category]), [Total Sales]),
    "Difference", [Total Sales] - SUMX(VALUES(Product[Category]), [Total Sales])
)
```

### Verify Against Source Data

```dax
// Compare measure to raw aggregation
EVALUATE
ROW(
    "Measure Result", [Total Sales],
    "Direct SUM", SUM(Sales[Amount]),
    "Match", IF([Total Sales] = SUM(Sales[Amount]), "YES", "NO")
)
```

### Historical Comparison

```dax
// Compare current calculation to historical values
EVALUATE
ADDCOLUMNS(
    CALENDAR(DATE(2020,1,1), DATE(2024,12,31)),
    "Year", YEAR([Date]),
    "Month", MONTH([Date]),
    "Sales", [Total Sales]
)
```

## Test Patterns for Common Scenarios

### New Measure Checklist

1. **Blank context test**: Does it return expected total?
2. **Single filter test**: Does it filter correctly?
3. **Multiple filter test**: Do combined filters work?
4. **Edge case test**: Empty data, null values, division by zero
5. **Performance test**: Does it calculate quickly?

### New Visual Checklist

1. **Field binding test**: Do all fields show data?
2. **Filter interaction test**: Does cross-filtering work?
3. **Drill-down test**: Does drill hierarchy work?
4. **Mobile layout test**: Does it render on mobile?
5. **Export test**: Can it be exported to PDF/PowerPoint?

### New Relationship Checklist

1. **Cardinality test**: Is the relationship 1:M, M:1, M:M?
2. **Direction test**: Does filter flow in expected direction?
3. **Null handling test**: How are missing keys handled?
4. **Performance test**: Does it slow down queries?

## Error Diagnosis

### Measure Returns BLANK

```dax
// Debug: Check if underlying data exists
EVALUATE
ROW(
    "Has Data", IF(COUNTROWS(Sales) > 0, "YES", "NO"),
    "Has Amount", IF(COUNTROWS(FILTER(Sales, Sales[Amount] <> BLANK())) > 0, "YES", "NO"),
    "Filter Context", CONCATENATEX(VALUES(Product[Category]), Product[Category], ", ")
)
```

### Unexpected Value

```dax
// Debug: Break down calculation step by step
EVALUATE
ROW(
    "Step 1 - Raw Sum", SUM(Sales[Amount]),
    "Step 2 - After Filter", CALCULATE(SUM(Sales[Amount]), Product[Category] = "A"),
    "Step 3 - Final Measure", [Total Sales]
)
```

### Circular Dependency

```dax
// Test each component separately
EVALUATE ROW("Component 1", [Measure1])

EVALUATE ROW("Component 2", [Measure2])

// If one fails, that's where the circular dependency is
```

## Reference

For comprehensive testing methodology, load:
```
${CLAUDE_PLUGIN_ROOT}/skills/pbi-test/references/testing-guide.md
```

## Quick Test Commands

### Test a single measure:
```
Use MCP execute_dax: EVALUATE ROW("Result", [MeasureName])
```

### Test with filters:
```
Use MCP execute_dax: EVALUATE CALCULATETABLE(ROW("Result", [MeasureName]), Table[Column] = "Value")
```

### Test visual rendering:
```
Use computer use to take screenshot of Power BI Desktop
```

### Test relationship:
```
Use MCP execute_dax: EVALUATE SUMMARIZECOLUMNS(DimTable[Column], "Value", [Measure])
```
