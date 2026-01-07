# Calculation Groups in Power BI

Calculation groups are a powerful feature that lets you apply dynamic calculations to any measure in your model without duplicating DAX code. They act as modifiers that transform measure results based on user selection.

---

## Table of Contents

1. [What Are Calculation Groups](#1-what-are-calculation-groups)
2. [TMDL Syntax](#2-tmdl-syntax)
3. [Time Intelligence Calculation Group](#3-time-intelligence-calculation-group)
4. [Currency Conversion Pattern](#4-currency-conversion-pattern)
5. [Comparison Periods Pattern](#5-comparison-periods-pattern)
6. [SELECTEDMEASURE Function](#6-selectedmeasure-function)
7. [Format String Expressions](#7-format-string-expressions)
8. [Precedence and Multiple Groups](#8-precedence-and-multiple-groups)
9. [Limitations and Gotchas](#9-limitations-and-gotchas)

---

## 1. What Are Calculation Groups

### Purpose

A calculation group is a set of calculation items that apply transformations to any measure in your model. Instead of creating multiple versions of every measure (Sales, Sales YTD, Sales PY, Sales YoY %), you create one measure and let the calculation group apply the transformation dynamically.

**Without calculation groups:**
```dax
Total Sales = SUM(Sales[Amount])
Total Sales YTD = CALCULATE([Total Sales], DATESYTD('Date'[Date]))
Total Sales PY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
Total Sales YoY = [Total Sales] - [Total Sales PY]
// Repeat for Cost, Profit, Quantity, etc.
```

**With calculation groups:**
- Create one measure per metric
- The calculation group applies YTD, PY, YoY transformations to any measure
- 10 measures + 10 calculation items = 100 possible calculations

### When to Use Calculation Groups

| Use Case | Recommendation |
|----------|----------------|
| Time intelligence across many measures | Use calculation groups |
| Currency conversion | Use calculation groups |
| Budget vs Actual comparisons | Use calculation groups |
| Single measure needing one variation | Use explicit measure |
| Complex calculations with specific logic per measure | Use explicit measures |
| Calculated columns | Cannot use calculation groups |
| Direct Query without aggregations | Evaluate carefully |

### When NOT to Use

- **Calculated columns**: Calculation groups only work with measures
- **Performance-critical single calculations**: Explicit measures can be more efficient
- **When you need measure-specific logic**: Some calculations may need custom handling per measure
- **Simple models with few measures**: Overhead may not be justified

---

## 2. TMDL Syntax

### Basic Structure

In TMDL, calculation groups are defined as special tables with calculation items:

```tmdl
table 'Time Intelligence'
	lineageTag: a1b2c3d4-e5f6-7890-abcd-ef1234567890

	calculationGroup
		precedence: 10

		calculationItem Current = SELECTEDMEASURE()
			ordinal: 0

		calculationItem YTD =
				CALCULATE(
				    SELECTEDMEASURE(),
				    DATESYTD('Date'[Date])
				)
			ordinal: 1

		calculationItem PY =
				CALCULATE(
				    SELECTEDMEASURE(),
				    SAMEPERIODLASTYEAR('Date'[Date])
				)
			ordinal: 2

	column 'Time Calculation'
		dataType: string
		sourceColumn: Name
		sortByColumn: Ordinal
		summarizeBy: none
		lineageTag: b2c3d4e5-f6g7-8901-bcde-f23456789012

	column Ordinal
		dataType: int64
		isHidden
		sourceColumn: Ordinal
		summarizeBy: none
		lineageTag: c3d4e5f6-g7h8-9012-cdef-345678901234
```

### Key Properties

| Property | Description |
|----------|-------------|
| `calculationGroup` | Declares this table as a calculation group |
| `precedence` | Order when multiple calculation groups exist (higher = outer) |
| `calculationItem` | Individual calculation transformation |
| `ordinal` | Display order of items in slicers |
| `sortByColumn: Ordinal` | Ensures slicer shows items in intended order |

### Creating via TMDL View

In Power BI Desktop's TMDL View, use:

```tmdl
createOrReplace table 'Time Intelligence'
    calculationGroup
        precedence: 10

        calculationItem 'Current' = SELECTEDMEASURE()
            ordinal: 0

        calculationItem 'YTD' =
            CALCULATE(
                SELECTEDMEASURE(),
                DATESYTD('Date'[Date])
            )
            ordinal: 1

    column 'Time Calculation'
        dataType: string
        sourceColumn: Name
        summarizeBy: none
```

---

## 3. Time Intelligence Calculation Group

### Complete Time Intelligence Pattern

This comprehensive time intelligence calculation group covers the most common temporal calculations:

```tmdl
table 'Time Intelligence'
    lineageTag: 11111111-2222-3333-4444-555555555555

    calculationGroup
        precedence: 10

        /// Returns the measure value as-is (no transformation)
        calculationItem Current = SELECTEDMEASURE()
            ordinal: 0

        /// Year-to-Date: cumulative from start of year
        calculationItem YTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESYTD('Date'[Date])
                )
            ordinal: 1

        /// Quarter-to-Date: cumulative from start of quarter
        calculationItem QTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESQTD('Date'[Date])
                )
            ordinal: 2

        /// Month-to-Date: cumulative from start of month
        calculationItem MTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESMTD('Date'[Date])
                )
            ordinal: 3

        /// Prior Year: same period one year ago
        calculationItem PY =
                CALCULATE(
                    SELECTEDMEASURE(),
                    SAMEPERIODLASTYEAR('Date'[Date])
                )
            ordinal: 4

        /// Prior Year YTD: year-to-date as of same date last year
        calculationItem PY YTD =
                CALCULATE(
                    SELECTEDMEASURE(),
                    SAMEPERIODLASTYEAR('Date'[Date]),
                    DATESYTD('Date'[Date])
                )
            ordinal: 5

        /// Year-over-Year Change: absolute difference vs prior year
        calculationItem YoY =
                VAR CurrentValue = SELECTEDMEASURE()
                VAR PriorYearValue =
                    CALCULATE(
                        SELECTEDMEASURE(),
                        SAMEPERIODLASTYEAR('Date'[Date])
                    )
                RETURN
                    CurrentValue - PriorYearValue
            ordinal: 6

        /// Year-over-Year Percentage: percentage change vs prior year
        calculationItem YoY % =
                VAR CurrentValue = SELECTEDMEASURE()
                VAR PriorYearValue =
                    CALCULATE(
                        SELECTEDMEASURE(),
                        SAMEPERIODLASTYEAR('Date'[Date])
                    )
                RETURN
                    DIVIDE(
                        CurrentValue - PriorYearValue,
                        PriorYearValue
                    )
            ordinal: 7
            formatStringDefinition = "0.0%;-0.0%;0.0%"

        /// Rolling 12 Months: sum of last 12 complete months
        calculationItem Rolling 12M =
                CALCULATE(
                    SELECTEDMEASURE(),
                    DATESINPERIOD(
                        'Date'[Date],
                        MAX('Date'[Date]),
                        -12,
                        MONTH
                    )
                )
            ordinal: 8

        /// Prior Month: same measure for previous month
        calculationItem PM =
                CALCULATE(
                    SELECTEDMEASURE(),
                    PREVIOUSMONTH('Date'[Date])
                )
            ordinal: 9

        /// Month-over-Month Change
        calculationItem MoM =
                VAR CurrentValue = SELECTEDMEASURE()
                VAR PriorMonthValue =
                    CALCULATE(
                        SELECTEDMEASURE(),
                        PREVIOUSMONTH('Date'[Date])
                    )
                RETURN
                    CurrentValue - PriorMonthValue
            ordinal: 10

    column 'Time Calculation'
        dataType: string
        sourceColumn: Name
        sortByColumn: Ordinal
        summarizeBy: none
        lineageTag: 22222222-3333-4444-5555-666666666666

    column Ordinal
        dataType: int64
        isHidden
        sourceColumn: Ordinal
        summarizeBy: none
        lineageTag: 33333333-4444-5555-6666-777777777777
```

### Using in Reports

Once created:

1. Add the `Time Calculation` column to a slicer
2. Users select "YTD", "PY", "YoY %", etc.
3. All measures in the report automatically transform

---

## 4. Currency Conversion Pattern

### Exchange Rate Table Structure

First, ensure you have an exchange rate table:

```tmdl
table 'Exchange Rates'
    column CurrencyCode
        dataType: string
    column Date
        dataType: dateTime
    column RateToUSD
        dataType: double
    column RateToEUR
        dataType: double
    column RateToGBP
        dataType: double
```

### Currency Conversion Calculation Group

```tmdl
table 'Currency'
    lineageTag: 44444444-5555-6666-7777-888888888888

    calculationGroup
        precedence: 20

        /// Display in local/source currency (no conversion)
        calculationItem 'Local Currency' = SELECTEDMEASURE()
            ordinal: 0

        /// Convert to US Dollars
        calculationItem 'USD' =
                VAR ExchangeRate =
                    CALCULATE(
                        AVERAGE('Exchange Rates'[RateToUSD]),
                        CROSSFILTER('Date'[Date], 'Exchange Rates'[Date], BOTH)
                    )
                RETURN
                    SELECTEDMEASURE() * ExchangeRate
            ordinal: 1
            formatStringDefinition = "$#,##0.00"

        /// Convert to Euros
        calculationItem 'EUR' =
                VAR ExchangeRate =
                    CALCULATE(
                        AVERAGE('Exchange Rates'[RateToEUR]),
                        CROSSFILTER('Date'[Date], 'Exchange Rates'[Date], BOTH)
                    )
                RETURN
                    SELECTEDMEASURE() * ExchangeRate
            ordinal: 2
            formatStringDefinition = "€#,##0.00"

        /// Convert to British Pounds
        calculationItem 'GBP' =
                VAR ExchangeRate =
                    CALCULATE(
                        AVERAGE('Exchange Rates'[RateToGBP]),
                        CROSSFILTER('Date'[Date], 'Exchange Rates'[Date], BOTH)
                    )
                RETURN
                    SELECTEDMEASURE() * ExchangeRate
            ordinal: 3
            formatStringDefinition = "£#,##0.00"

    column 'Display Currency'
        dataType: string
        sourceColumn: Name
        sortByColumn: Ordinal
        summarizeBy: none
        lineageTag: 55555555-6666-7777-8888-999999999999

    column Ordinal
        dataType: int64
        isHidden
        sourceColumn: Ordinal
        summarizeBy: none
        lineageTag: 66666666-7777-8888-9999-aaaaaaaaaaaa
```

### End-of-Day Rate Pattern

For more precise currency conversion using end-of-day rates:

```dax
calculationItem 'USD (EOD)' =
    VAR ExchangeRate =
        CALCULATE(
            SELECTEDVALUE('Exchange Rates'[RateToUSD]),
            TREATAS(VALUES('Date'[Date]), 'Exchange Rates'[Date])
        )
    RETURN
        SELECTEDMEASURE() * ExchangeRate
```

---

## 5. Comparison Periods Pattern

### Budget vs Actual Calculation Group

```tmdl
table 'Comparison'
    lineageTag: 77777777-8888-9999-aaaa-bbbbbbbbbbbb

    calculationGroup
        precedence: 5

        /// Actual values (current data)
        calculationItem Actual = SELECTEDMEASURE()
            ordinal: 0

        /// Budget values from budget table
        calculationItem Budget =
                CALCULATE(
                    SELECTEDMEASURE(),
                    USERELATIONSHIP('Budget'[Date], 'Date'[Date]),
                    'Data Type'[Type] = "Budget"
                )
            ordinal: 1

        /// Forecast values
        calculationItem Forecast =
                CALCULATE(
                    SELECTEDMEASURE(),
                    'Data Type'[Type] = "Forecast"
                )
            ordinal: 2

        /// Variance: Actual - Budget
        calculationItem 'vs Budget' =
                VAR ActualValue = SELECTEDMEASURE()
                VAR BudgetValue =
                    CALCULATE(
                        SELECTEDMEASURE(),
                        'Data Type'[Type] = "Budget"
                    )
                RETURN
                    ActualValue - BudgetValue
            ordinal: 3

        /// Variance %: (Actual - Budget) / Budget
        calculationItem 'vs Budget %' =
                VAR ActualValue = SELECTEDMEASURE()
                VAR BudgetValue =
                    CALCULATE(
                        SELECTEDMEASURE(),
                        'Data Type'[Type] = "Budget"
                    )
                RETURN
                    DIVIDE(ActualValue - BudgetValue, BudgetValue)
            ordinal: 4
            formatStringDefinition = "0.0%;-0.0%;0.0%"

        /// vs Forecast
        calculationItem 'vs Forecast' =
                VAR ActualValue = SELECTEDMEASURE()
                VAR ForecastValue =
                    CALCULATE(
                        SELECTEDMEASURE(),
                        'Data Type'[Type] = "Forecast"
                    )
                RETURN
                    ActualValue - ForecastValue
            ordinal: 5

        /// vs Prior Period (dynamic based on current context)
        calculationItem 'vs Prior Period' =
                VAR CurrentValue = SELECTEDMEASURE()
                VAR PriorValue =
                    CALCULATE(
                        SELECTEDMEASURE(),
                        DATEADD('Date'[Date], -1, MONTH)
                    )
                RETURN
                    CurrentValue - PriorValue
            ordinal: 6

    column 'Comparison Type'
        dataType: string
        sourceColumn: Name
        sortByColumn: Ordinal
        summarizeBy: none
        lineageTag: 88888888-9999-aaaa-bbbb-cccccccccccc

    column Ordinal
        dataType: int64
        isHidden
        sourceColumn: Ordinal
        summarizeBy: none
        lineageTag: 99999999-aaaa-bbbb-cccc-dddddddddddd
```

---

## 6. SELECTEDMEASURE Function

### How SELECTEDMEASURE Works

`SELECTEDMEASURE()` is a placeholder function that gets replaced with whatever measure is being evaluated in the current context.

```dax
// When user views [Total Sales] with YTD calculation item selected:
YTD = CALCULATE(SELECTEDMEASURE(), DATESYTD('Date'[Date]))

// Becomes:
YTD = CALCULATE([Total Sales], DATESYTD('Date'[Date]))
```

### Related Functions

| Function | Purpose |
|----------|---------|
| `SELECTEDMEASURE()` | Returns the current measure value |
| `SELECTEDMEASURENAME()` | Returns the name of the current measure |
| `SELECTEDMEASUREFORMATSTRING()` | Returns the format string of the current measure |
| `ISSELECTEDMEASURE()` | Tests if a specific measure is being evaluated |

### Conditional Logic with ISSELECTEDMEASURE

Apply different calculations to different measures:

```dax
calculationItem 'YTD (Smart)' =
    IF(
        ISSELECTEDMEASURE([Order Count], [Customer Count]),
        // For count measures: use running count
        CALCULATE(
            SELECTEDMEASURE(),
            'Date'[Date] <= MAX('Date'[Date]),
            'Date'[Year] = SELECTEDVALUE('Date'[Year])
        ),
        // For amount measures: use standard DATESYTD
        CALCULATE(
            SELECTEDMEASURE(),
            DATESYTD('Date'[Date])
        )
    )
```

### Passing Measures as Parameters

You can use `SELECTEDMEASURE()` with other DAX functions:

```dax
calculationItem 'Cumulative' =
    VAR CurrentDate = MAX('Date'[Date])
    RETURN
        CALCULATE(
            SELECTEDMEASURE(),
            'Date'[Date] <= CurrentDate,
            ALL('Date')
        )
```

---

## 7. Format String Expressions

### Dynamic Format Strings

Calculation items can override the measure's format string:

```tmdl
calculationItem 'YoY %' =
        VAR CurrentValue = SELECTEDMEASURE()
        VAR PriorYearValue = CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Date'[Date]))
        RETURN DIVIDE(CurrentValue - PriorYearValue, PriorYearValue)
    formatStringDefinition = "0.0%;-0.0%;0.0%"
```

### Preserving Original Format

To keep the original measure's format:

```dax
calculationItem 'YTD' =
        CALCULATE(SELECTEDMEASURE(), DATESYTD('Date'[Date]))
    formatStringDefinition = SELECTEDMEASUREFORMATSTRING()
```

### Conditional Format Strings

Format strings can use DAX expressions:

```tmdl
calculationItem 'Smart Format' =
        SELECTEDMEASURE()
    formatStringDefinition =
        IF(
            CONTAINSSTRING(SELECTEDMEASURENAME(), "%"),
            "0.0%",
            IF(
                CONTAINSSTRING(SELECTEDMEASURENAME(), "Count"),
                "#,##0",
                SELECTEDMEASUREFORMATSTRING()
            )
        )
```

### Common Format String Patterns

| Format | Result | Use For |
|--------|--------|---------|
| `"$#,##0.00"` | $1,234.56 | Currency |
| `"#,##0"` | 1,235 | Whole numbers |
| `"0.0%"` | 12.3% | Percentages |
| `"0.0%;-0.0%;0.0%"` | Positive; Negative; Zero | Signed percentages |
| `"#,##0.00,,\"M\""` | 1.23M | Millions |
| `"#,##0.00,\"K\""` | 1,234.56K | Thousands |

---

## 8. Precedence and Multiple Groups

### How Precedence Works

When multiple calculation groups are used together, precedence determines the order of application:

- **Higher precedence** = Applied **outer** (last)
- **Lower precedence** = Applied **inner** (first, closest to base measure)

```
Result = HighPrecedence( LowPrecedence( BaseMeasure ) )
```

### Example: Time Intelligence + Currency

```tmdl
// Time Intelligence: precedence 10 (inner)
table 'Time Intelligence'
    calculationGroup
        precedence: 10
        calculationItem YTD = CALCULATE(SELECTEDMEASURE(), DATESYTD('Date'[Date]))

// Currency: precedence 20 (outer)
table 'Currency'
    calculationGroup
        precedence: 20
        calculationItem USD = SELECTEDMEASURE() * [Exchange Rate to USD]
```

**Evaluation order:**
1. Base measure: `[Total Sales]`
2. Time Intelligence (precedence 10): `CALCULATE([Total Sales], DATESYTD(...))`
3. Currency (precedence 20): `YTD Result * Exchange Rate`

### Controlling No Selection Behavior

New properties (preview) control what happens when no item is selected:

```tmdl
calculationGroup
    precedence: 10

    /// Expression when no calculation item is selected
    noSelectionExpression = SELECTEDMEASURE()

    /// Expression when multiple items are selected
    multipleOrEmptySelectionExpression = BLANK()

    calculationItem Current = SELECTEDMEASURE()
    calculationItem YTD = CALCULATE(SELECTEDMEASURE(), DATESYTD('Date'[Date]))
```

### Best Practices for Precedence

| Calculation Type | Suggested Precedence | Reasoning |
|-----------------|---------------------|-----------|
| Time Intelligence | 10 | Applied first to aggregate data |
| Comparison (vs Budget) | 15 | Compare time-aggregated values |
| Currency Conversion | 20 | Convert final values |
| Display Formatting | 25 | Format at the end |

---

## 9. Limitations and Gotchas

### Cannot Use with Calculated Columns

Calculation groups only modify measures. They have no effect on:
- Calculated columns
- Row-level calculations
- Table expressions

### Interaction with Explicit Measures

When a measure explicitly references another measure, the calculation group applies to both:

```dax
// If you have:
[Profit] = [Revenue] - [Cost]

// With YTD selected:
// Result is: YTD([Revenue]) - YTD([Cost])
// NOT: YTD([Revenue] - [Cost])
```

**Solution:** Use variables to control evaluation:

```dax
[Profit] =
VAR Rev = [Revenue]
VAR Cst = [Cost]
RETURN Rev - Cst
```

### CALCULATE Modifiers Don't Stack

Calculation items using CALCULATE may conflict with report filters:

```dax
// Calculation item
YTD = CALCULATE(SELECTEDMEASURE(), DATESYTD('Date'[Date]))

// If report has filter: Date[Year] = 2023
// The DATESYTD respects this filter
```

### Visual Totals Behavior

Calculation group items affect totals differently:

| Item Type | Total Behavior |
|-----------|----------------|
| Additive (YTD, sum) | Recalculates for total period |
| Non-additive (YoY %) | May show unexpected results |
| Ratio measures | Should use SUMMARIZE pattern |

### Performance Considerations

- Calculation groups add query complexity
- Complex format string expressions evaluate per cell
- Multiple calculation groups multiply the evaluation paths

### Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Forgetting ordinal | Items appear in random order | Add `ordinal:` to each item |
| Missing date context | Time intelligence returns BLANK | Ensure Date table is properly marked |
| Wrong precedence order | Currency converts before time calc | Set time intelligence lower than currency |
| No default item | Users must always select | Add "Current" item with `SELECTEDMEASURE()` |
| Format string ignored | Shows wrong format | Use `formatStringDefinition` property |

### Testing Calculation Groups

1. **Create a test measure:**
   ```dax
   Test Measure = SUM(Sales[Amount])
   ```

2. **Add calculation group column to matrix rows**

3. **Verify each calculation item produces expected results**

4. **Test with filters to ensure context is correct**

5. **Check format strings display correctly**

---

## References

- [Create calculation groups - Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/transform-model/calculation-groups)
- [Calculation Groups - SQLBI](https://www.sqlbi.com/calculation-groups/)
- [Understanding Calculation Groups - SQLBI](https://www.sqlbi.com/articles/understanding-calculation-groups/)
- [TMDL View in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-tmdl-view)
- [Currency Conversion - DAX Patterns](https://www.daxpatterns.com/currency-conversion/)
- [Time Intelligence - SQLBI](https://www.sqlbi.com/timeintelligence/)
