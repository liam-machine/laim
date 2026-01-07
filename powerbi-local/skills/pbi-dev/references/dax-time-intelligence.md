# DAX Time Intelligence Patterns

This reference covers time intelligence patterns, date table requirements, and common time-based calculations for Power BI development.

---

## 1. Date Table Requirements

Time intelligence functions in DAX require a properly configured date table. Without this foundation, time intelligence functions will return incorrect results or fail entirely.

### Essential Requirements

| Requirement | Description |
|-------------|-------------|
| **Continuous dates** | No gaps in the date sequence - every day must be present |
| **Full years** | Must span complete years (Jan 1 to Dec 31 for calendar year) |
| **One row per day** | Each date appears exactly once |
| **Date data type** | Date column must be Date or DateTime (not text or integer) |
| **No blanks** | Date column cannot contain BLANK values |
| **Covers all data** | Range must encompass all dates in fact tables |
| **No time component** | Time should always be 12:00:00 AM (midnight) |

### Required Columns

A well-designed date table includes these columns:

```dax
// Minimal date table with CALENDAR
DateTable =
VAR StartDate = DATE(2020, 1, 1)
VAR EndDate = DATE(2025, 12, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(StartDate, EndDate),
    "Year", YEAR([Date]),
    "Month", MONTH([Date]),
    "MonthName", FORMAT([Date], "MMMM"),
    "MonthShort", FORMAT([Date], "MMM"),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "QuarterNum", INT(FORMAT([Date], "Q")),
    "Day", DAY([Date]),
    "DayOfWeek", WEEKDAY([Date], 2),
    "DayName", FORMAT([Date], "dddd"),
    "WeekNum", WEEKNUM([Date], 2),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "MonthYear", FORMAT([Date], "MMM YYYY"),
    "IsCurrentYear", IF(YEAR([Date]) = YEAR(TODAY()), TRUE(), FALSE()),
    "IsCurrentMonth", IF(YEAR([Date]) = YEAR(TODAY()) && MONTH([Date]) = MONTH(TODAY()), TRUE(), FALSE())
)
```

### Using CALENDARAUTO

CALENDARAUTO automatically determines the date range based on dates in your model:

```dax
// Auto-generates dates spanning all date columns in model
DateTable = CALENDARAUTO()

// With fiscal year ending in June
DateTable = CALENDARAUTO(6)
```

### Mark as Date Table

**Why it matters:** When a table is marked as a date table, DAX automatically applies `REMOVEFILTERS` on the date table when time intelligence functions filter the date column. This ensures time intelligence functions work correctly.

**How to mark:**
1. Select the date table in Model view
2. Right-click > Mark as date table
3. Select the date column as the date column

**When marking is required:**
- If the relationship to your date table uses an Integer key (like DateKey: 20240115)
- For best practice, always mark your date table

**When marking is implicit:**
- If the relationship uses a Date data type column, DAX applies the behavior automatically
- Still recommended to mark for clearer metadata

### Auto Date/Time Considerations

Power BI has an "Auto date/time" feature that creates hidden date tables for each date column.

| Setting | Behavior | Recommendation |
|---------|----------|----------------|
| **Enabled (default)** | Hidden date table per date column | Disable for production models |
| **Disabled** | No auto tables, you provide date table | Recommended for time intelligence |

**Why disable:**
- Hidden tables increase model size
- Can't customize time intelligence calculations
- Inconsistent behavior across visuals
- Less control over date hierarchies

**To disable:** File > Options > Current File > Data Load > Uncheck "Auto date/time"

---

## 2. Standard Time Intelligence Functions

### Year-to-Date Functions

| Function | Description | Example |
|----------|-------------|---------|
| `TOTALYTD` | Year-to-date total | `TOTALYTD([Sales], 'Date'[Date])` |
| `DATESYTD` | Returns dates from year start to current date | `CALCULATE([Sales], DATESYTD('Date'[Date]))` |

```dax
// Year-to-Date Sales
Sales YTD =
TOTALYTD([Total Sales], 'Date'[Date])

// Equivalent using CALCULATE
Sales YTD =
CALCULATE(
    [Total Sales],
    DATESYTD('Date'[Date])
)

// With fiscal year end (e.g., March 31)
Sales Fiscal YTD =
TOTALYTD([Total Sales], 'Date'[Date], "3/31")
```

### Quarter-to-Date Functions

| Function | Description | Example |
|----------|-------------|---------|
| `TOTALQTD` | Quarter-to-date total | `TOTALQTD([Sales], 'Date'[Date])` |
| `DATESQTD` | Returns dates from quarter start to current date | `CALCULATE([Sales], DATESQTD('Date'[Date]))` |

```dax
// Quarter-to-Date Sales
Sales QTD =
TOTALQTD([Total Sales], 'Date'[Date])

// Equivalent using CALCULATE
Sales QTD =
CALCULATE(
    [Total Sales],
    DATESQTD('Date'[Date])
)
```

### Month-to-Date Functions

| Function | Description | Example |
|----------|-------------|---------|
| `TOTALMTD` | Month-to-date total | `TOTALMTD([Sales], 'Date'[Date])` |
| `DATESMTD` | Returns dates from month start to current date | `CALCULATE([Sales], DATESMTD('Date'[Date]))` |

```dax
// Month-to-Date Sales
Sales MTD =
TOTALMTD([Total Sales], 'Date'[Date])

// Equivalent using CALCULATE
Sales MTD =
CALCULATE(
    [Total Sales],
    DATESMTD('Date'[Date])
)
```

### Same Period Last Year

| Function | Description | Example |
|----------|-------------|---------|
| `SAMEPERIODLASTYEAR` | Shifts dates back one year | `CALCULATE([Sales], SAMEPERIODLASTYEAR('Date'[Date]))` |
| `DATEADD` | Shifts dates by interval | `CALCULATE([Sales], DATEADD('Date'[Date], -1, YEAR))` |
| `PARALLELPERIOD` | Returns parallel period | `CALCULATE([Sales], PARALLELPERIOD('Date'[Date], -1, YEAR))` |

```dax
// Sales Same Period Last Year
Sales SPLY =
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR('Date'[Date])
)

// Using DATEADD (equivalent)
Sales SPLY =
CALCULATE(
    [Total Sales],
    DATEADD('Date'[Date], -1, YEAR)
)
```

### DATEADD Function

DATEADD shifts dates by a specified interval. Extremely versatile for time intelligence.

```dax
// Syntax: DATEADD(<dates>, <number_of_intervals>, <interval>)
// Intervals: DAY, MONTH, QUARTER, YEAR

// Previous month
Sales Previous Month =
CALCULATE([Total Sales], DATEADD('Date'[Date], -1, MONTH))

// Same quarter last year
Sales Same Quarter LY =
CALCULATE([Total Sales], DATEADD('Date'[Date], -4, QUARTER))

// 30 days ago
Sales 30 Days Ago =
CALCULATE([Total Sales], DATEADD('Date'[Date], -30, DAY))
```

### DATESINPERIOD Function

Returns a table of dates within a specified period from a reference date.

```dax
// Syntax: DATESINPERIOD(<dates>, <start_date>, <number_of_intervals>, <interval>)

// Last 12 months from current selection
Sales Last 12M =
CALCULATE(
    [Total Sales],
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -12,
        MONTH
    )
)

// Last 90 days
Sales Last 90 Days =
CALCULATE(
    [Total Sales],
    DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -90, DAY)
)
```

### PARALLELPERIOD Function

Returns a parallel period shifted by the specified number of intervals.

```dax
// Key difference from DATEADD:
// PARALLELPERIOD returns the ENTIRE period, not just shifted days

// Example: If viewing March 15, 2024:
// DATEADD returns March 15, 2023 (shifted day)
// PARALLELPERIOD returns entire March 2023 (full month)

// Full previous year
Sales Full Previous Year =
CALCULATE([Total Sales], PARALLELPERIOD('Date'[Date], -1, YEAR))

// Full previous quarter
Sales Full Previous Quarter =
CALCULATE([Total Sales], PARALLELPERIOD('Date'[Date], -1, QUARTER))
```

### Previous Period Functions

| Function | Description |
|----------|-------------|
| `PREVIOUSYEAR` | Previous year's dates |
| `PREVIOUSQUARTER` | Previous quarter's dates |
| `PREVIOUSMONTH` | Previous month's dates |
| `PREVIOUSDAY` | Previous day |
| `NEXTYEAR` | Next year's dates |
| `NEXTQUARTER` | Next quarter's dates |
| `NEXTMONTH` | Next month's dates |
| `NEXTDAY` | Next day |

```dax
// Previous year
Sales Previous Year =
CALCULATE([Total Sales], PREVIOUSYEAR('Date'[Date]))

// Previous month
Sales Previous Month =
CALCULATE([Total Sales], PREVIOUSMONTH('Date'[Date]))

// Previous day
Sales Previous Day =
CALCULATE([Total Sales], PREVIOUSDAY('Date'[Date]))
```

### FIRSTDATE and LASTDATE

```dax
// First date with sales in current context
First Sale Date = FIRSTDATE(Sales[OrderDate])

// Last date with sales in current context
Last Sale Date = LASTDATE(Sales[OrderDate])

// First date of current selection
First Date Selected = FIRSTDATE('Date'[Date])

// Last date of current selection
Last Date Selected = LASTDATE('Date'[Date])
```

### Opening and Closing Balance Functions

| Function | Description |
|----------|-------------|
| `OPENINGBALANCEYEAR` | Value at start of year |
| `CLOSINGBALANCEYEAR` | Value at end of year |
| `OPENINGBALANCEQUARTER` | Value at start of quarter |
| `CLOSINGBALANCEQUARTER` | Value at end of quarter |
| `OPENINGBALANCEMONTH` | Value at start of month |
| `CLOSINGBALANCEMONTH` | Value at end of month |

```dax
// Opening balance at start of year
Opening Balance YTD =
OPENINGBALANCEYEAR([Account Balance], 'Date'[Date])

// Closing balance at end of month
Closing Balance Month =
CLOSINGBALANCEMONTH([Account Balance], 'Date'[Date])

// With fiscal year end
Opening Balance Fiscal =
OPENINGBALANCEYEAR([Account Balance], 'Date'[Date], "6/30")
```

---

## 3. Common Time Intelligence Measures

### Year-over-Year Growth

```dax
// YoY Growth Amount
Sales YoY Growth =
VAR CurrentSales = [Total Sales]
VAR PriorYearSales =
    CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
RETURN
CurrentSales - PriorYearSales

// YoY Growth Percentage
Sales YoY % =
VAR CurrentSales = [Total Sales]
VAR PriorYearSales =
    CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
RETURN
DIVIDE(CurrentSales - PriorYearSales, PriorYearSales)

// YoY with formatted output
Sales YoY Display =
VAR CurrentSales = [Total Sales]
VAR PriorYearSales =
    CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
VAR Growth = DIVIDE(CurrentSales - PriorYearSales, PriorYearSales)
RETURN
IF(
    ISBLANK(PriorYearSales),
    BLANK(),
    FORMAT(Growth, "+0.0%;-0.0%;0.0%")
)
```

### Year-to-Date Comparison

```dax
// YTD Sales
Sales YTD =
TOTALYTD([Total Sales], 'Date'[Date])

// Prior Year YTD (PYTD)
Sales PYTD =
CALCULATE(
    TOTALYTD([Total Sales], 'Date'[Date]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

// YTD vs PYTD Growth
YTD Growth =
VAR YTD = [Sales YTD]
VAR PYTD = [Sales PYTD]
RETURN
DIVIDE(YTD - PYTD, PYTD)

// Alternative PYTD calculation
Sales PYTD Alt =
CALCULATE(
    [Total Sales],
    DATESYTD(SAMEPERIODLASTYEAR('Date'[Date]))
)
```

### Quarter-to-Date Comparison

```dax
// QTD Sales
Sales QTD =
TOTALQTD([Total Sales], 'Date'[Date])

// Prior Year QTD
Sales PYQTD =
CALCULATE(
    TOTALQTD([Total Sales], 'Date'[Date]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

// QTD Growth %
QTD Growth % =
DIVIDE([Sales QTD] - [Sales PYQTD], [Sales PYQTD])
```

### Month-to-Date Comparison

```dax
// MTD Sales
Sales MTD =
TOTALMTD([Total Sales], 'Date'[Date])

// Prior Year MTD
Sales PYMTD =
CALCULATE(
    TOTALMTD([Total Sales], 'Date'[Date]),
    SAMEPERIODLASTYEAR('Date'[Date])
)

// MTD Growth %
MTD Growth % =
DIVIDE([Sales MTD] - [Sales PYMTD], [Sales PYMTD])
```

### Rolling 12 Months

```dax
// Rolling 12 months from current selection
Sales Rolling 12M =
CALCULATE(
    [Total Sales],
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -12,
        MONTH
    )
)

// Rolling 12 months average
Avg Sales Rolling 12M =
AVERAGEX(
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -12,
        MONTH
    ),
    [Total Sales]
)

// Rolling 12M vs Prior Rolling 12M
Rolling 12M Growth =
VAR Current12M = [Sales Rolling 12M]
VAR Prior12M =
    CALCULATE(
        [Sales Rolling 12M],
        DATEADD('Date'[Date], -1, YEAR)
    )
RETURN
DIVIDE(Current12M - Prior12M, Prior12M)
```

### Same Period Last Year (Various Periods)

```dax
// Sales for same day last year
Sales Same Day LY =
CALCULATE([Total Sales], DATEADD('Date'[Date], -1, YEAR))

// Sales for same week last year
Sales Same Week LY =
CALCULATE([Total Sales], DATEADD('Date'[Date], -364, DAY))

// Sales for same month last year
Sales Same Month LY =
CALCULATE([Total Sales], PARALLELPERIOD('Date'[Date], -12, MONTH))

// Sales for same quarter last year
Sales Same Quarter LY =
CALCULATE([Total Sales], PARALLELPERIOD('Date'[Date], -4, QUARTER))
```

### First and Last Day of Period Values

```dax
// Value on first day of current month
First Day Value =
CALCULATE(
    [Total Sales],
    FIRSTDATE('Date'[Date])
)

// Value on last day of current month
Last Day Value =
CALCULATE(
    [Total Sales],
    LASTDATE('Date'[Date])
)

// Value on first day of year
First Day of Year Value =
CALCULATE(
    [Account Balance],
    FIRSTDATE(DATESYTD('Date'[Date]))
)

// Value on last day of year (for current context)
Last Day of Year Value =
CALCULATE(
    [Account Balance],
    LASTDATE(DATESYTD('Date'[Date]))
)
```

### Period-over-Period Comparisons

```dax
// Month over Month (MoM)
Sales MoM Growth =
VAR CurrentMonth = [Total Sales]
VAR PriorMonth =
    CALCULATE([Total Sales], DATEADD('Date'[Date], -1, MONTH))
RETURN
DIVIDE(CurrentMonth - PriorMonth, PriorMonth)

// Week over Week (WoW)
Sales WoW Growth =
VAR CurrentWeek = [Total Sales]
VAR PriorWeek =
    CALCULATE([Total Sales], DATEADD('Date'[Date], -7, DAY))
RETURN
DIVIDE(CurrentWeek - PriorWeek, PriorWeek)

// Quarter over Quarter (QoQ)
Sales QoQ Growth =
VAR CurrentQtr = [Total Sales]
VAR PriorQtr =
    CALCULATE([Total Sales], DATEADD('Date'[Date], -1, QUARTER))
RETURN
DIVIDE(CurrentQtr - PriorQtr, PriorQtr)
```

---

## 4. Fiscal Calendar Patterns

### Custom Fiscal Year Start

When your fiscal year doesn't start in January, adjust time intelligence functions:

```dax
// Fiscal YTD with June year-end
Sales Fiscal YTD =
TOTALYTD([Total Sales], 'Date'[Date], "6/30")

// Fiscal YTD with September year-end
Sales Fiscal YTD =
TOTALYTD([Total Sales], 'Date'[Date], "9/30")

// Opening balance for fiscal year
Opening Fiscal Balance =
OPENINGBALANCEYEAR([Account Balance], 'Date'[Date], "6/30")
```

### Date Table with Fiscal Periods

```dax
// Extended date table with fiscal periods (July fiscal year start)
FiscalDateTable =
VAR FiscalYearStartMonth = 7
RETURN
ADDCOLUMNS(
    CALENDAR(DATE(2020, 1, 1), DATE(2025, 12, 31)),
    "Fiscal Year",
        IF(MONTH([Date]) >= FiscalYearStartMonth,
           YEAR([Date]) + 1,
           YEAR([Date])),
    "Fiscal Quarter",
        "FQ" &
        SWITCH(
            TRUE(),
            MONTH([Date]) IN {7, 8, 9}, 1,
            MONTH([Date]) IN {10, 11, 12}, 2,
            MONTH([Date]) IN {1, 2, 3}, 3,
            4
        ),
    "Fiscal Month",
        IF(MONTH([Date]) >= FiscalYearStartMonth,
           MONTH([Date]) - FiscalYearStartMonth + 1,
           MONTH([Date]) + (12 - FiscalYearStartMonth + 1))
)
```

### 4-4-5, 4-5-4, and 5-4-4 Calendars

Retail and manufacturing industries often use week-based fiscal calendars. These divide the year into 52 weeks across 4 quarters, with each quarter having 13 weeks distributed as:

| Calendar Type | Period 1 | Period 2 | Period 3 |
|---------------|----------|----------|----------|
| **4-4-5** | 4 weeks | 4 weeks | 5 weeks |
| **4-5-4** | 4 weeks | 5 weeks | 4 weeks |
| **5-4-4** | 5 weeks | 4 weeks | 4 weeks |

**Creating a 445 Calendar:**

The complexity of 4-4-5 calendars requires a specialized date table. Key considerations:

1. Each year has exactly 52 weeks (364 days)
2. A 53rd week is added in some years to realign with the solar calendar
3. Month boundaries align with week boundaries

```dax
// High-level structure for 445 calendar columns
// (Full implementation typically done in Power Query)
445DateTable =
ADDCOLUMNS(
    CALENDAR(DATE(2020, 1, 1), DATE(2025, 12, 31)),
    "445 Year", [Calculated based on week logic],
    "445 Quarter", [Calculated based on week logic],
    "445 Period", [1-12 based on week accumulation],
    "445 Week", [1-52/53 week number],
    "445 Year Week", [Year + Week combination],
    "Period Week In Month", [1-4 or 1-5 week within period]
)
```

**Time Intelligence with 445 Calendar:**

Standard time intelligence functions don't work with 445 calendars. You must use custom patterns:

```dax
// Same period last year for 445 calendar
// Requires a column mapping each date to its corresponding date last year
Sales SPLY 445 =
CALCULATE(
    [Total Sales],
    TREATAS(
        VALUES('Date'[Corresponding Date LY]),
        'Date'[Date]
    )
)

// YTD for 445 using week-based logic
Sales YTD 445 =
CALCULATE(
    [Total Sales],
    FILTER(
        ALL('Date'),
        'Date'[445 Year] = MAX('Date'[445 Year]) &&
        'Date'[445 Week] <= MAX('Date'[445 Week])
    )
)
```

**Resources:** For detailed 445 calendar implementation, see:
- [DAX Patterns - Week-related calculations](https://www.daxpatterns.com/week-related-calculations/)
- [Power BI Calendar-based time intelligence](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables) (Preview feature as of 2025)

---

## 5. Semi-Additive Measures

### Understanding Semi-Additive Measures

Semi-additive measures are values that cannot be summed across all dimensions, typically time. Examples include:

- **Account balances** - Cannot sum January + February balance
- **Inventory levels** - Cannot sum daily inventory counts
- **Headcount** - Cannot sum employee counts across months

| Measure Type | Sum Across Products | Sum Across Regions | Sum Across Time |
|--------------|--------------------|--------------------|-----------------|
| **Additive** (Sales) | Yes | Yes | Yes |
| **Semi-Additive** (Balance) | Yes | Yes | No |
| **Non-Additive** (Percentage) | No | No | No |

### LASTNONBLANK Pattern

LASTNONBLANK returns the last date in the filter context where the expression has a non-blank value.

```dax
// Basic LASTNONBLANK pattern
Account Balance =
CALCULATE(
    SUM(Balances[Balance]),
    LASTNONBLANK(
        'Date'[Date],
        CALCULATE(SUM(Balances[Balance]))
    )
)

// Optimized version using LASTNONBLANKVALUE
Account Balance =
LASTNONBLANKVALUE(
    'Date'[Date],
    CALCULATE(SUM(Balances[Balance]))
)
```

**When LASTNONBLANK is needed:**
- Data is recorded only on certain days (not daily)
- You need the "last known value" even when no data exists for a period

### Inventory and Balance Calculations

```dax
// Closing inventory balance
Closing Inventory =
CALCULATE(
    SUM(Inventory[Quantity]),
    LASTDATE('Date'[Date])
)

// Opening inventory (first day of period)
Opening Inventory =
CALCULATE(
    SUM(Inventory[Quantity]),
    FIRSTDATE('Date'[Date])
)

// Average daily inventory
Avg Daily Inventory =
AVERAGEX(
    VALUES('Date'[Date]),
    CALCULATE(SUM(Inventory[Quantity]))
)

// Last known inventory when data has gaps
Last Known Inventory =
CALCULATE(
    SUM(Inventory[Quantity]),
    LASTNONBLANK(
        'Date'[Date],
        CALCULATE(SUM(Inventory[Quantity]))
    )
)
```

### LASTNONBLANKVALUE vs LASTNONBLANK

LASTNONBLANKVALUE (introduced later) is simpler and often more efficient:

```dax
// Using LASTNONBLANK (older pattern)
Balance V1 =
CALCULATE(
    SUM(Balances[Balance]),
    LASTNONBLANK('Date'[Date], CALCULATE(SUM(Balances[Balance])))
)

// Using LASTNONBLANKVALUE (preferred)
Balance V2 =
LASTNONBLANKVALUE('Date'[Date], CALCULATE(SUM(Balances[Balance])))

// Key difference:
// LASTNONBLANK returns a table (the date)
// LASTNONBLANKVALUE returns the value directly
```

### Multiple Entities with Different Last Dates

When each entity (customer, product, store) may have different last dates:

```dax
// Last known value per entity
Last Known Balance Per Customer =
SUMX(
    VALUES(Customers[CustomerID]),
    CALCULATE(
        LASTNONBLANKVALUE(
            'Date'[Date],
            SUM(Balances[Balance])
        )
    )
)

// Alternative using MAX date per entity
Last Balance Per Store =
VAR LastDates =
    ADDCOLUMNS(
        VALUES(Stores[StoreID]),
        "LastDate",
        CALCULATE(MAX(Inventory[SnapshotDate]))
    )
RETURN
SUMX(
    LastDates,
    VAR CurrentStore = [StoreID]
    VAR CurrentLastDate = [LastDate]
    RETURN
    CALCULATE(
        SUM(Inventory[Quantity]),
        Stores[StoreID] = CurrentStore,
        'Date'[Date] = CurrentLastDate
    )
)
```

### Closing Balance Functions

For fiscal period balances:

```dax
// End of month balance
Month End Balance =
CLOSINGBALANCEMONTH(SUM(Balances[Balance]), 'Date'[Date])

// End of quarter balance
Quarter End Balance =
CLOSINGBALANCEQUARTER(SUM(Balances[Balance]), 'Date'[Date])

// End of year balance
Year End Balance =
CLOSINGBALANCEYEAR(SUM(Balances[Balance]), 'Date'[Date])

// End of fiscal year balance
Fiscal Year End Balance =
CLOSINGBALANCEYEAR(SUM(Balances[Balance]), 'Date'[Date], "6/30")
```

---

## 6. Troubleshooting Time Intelligence

### Why Time Intelligence Returns BLANK

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| All time intelligence is blank | Date table not properly configured | Verify continuous dates, full years |
| SAMEPERIODLASTYEAR blank | Prior year dates not in date table | Extend date table range |
| YTD blank at month level | Date table doesn't cover full year | Ensure Jan 1 to Dec 31 |
| Works in table, blank in card | No date context in visual | Add date field or use CALCULATE |
| Partial blanks | Gaps in fact table data | Check for missing dates in source |

### Common Mistakes with Date Filters

**Mistake 1: Using fact table dates instead of date table**

```dax
// WRONG - Uses fact table dates
Bad YTD = TOTALYTD([Sales], Sales[OrderDate])

// CORRECT - Uses date dimension
Good YTD = TOTALYTD([Sales], 'Date'[Date])
```

**Mistake 2: Conflicting filters**

```dax
// PROBLEM: Filter for 2024 + SAMEPERIODLASTYEAR both applied
// Results in empty filter (2024 AND 2023 = nothing)

// SOLUTION: Use REMOVEFILTERS or ALL to clear date filters first
Sales LY Fixed =
CALCULATE(
    [Total Sales],
    REMOVEFILTERS('Date'),
    SAMEPERIODLASTYEAR('Date'[Date])
)
```

**Mistake 3: Not marking date table**

```dax
// If using integer date key (20240115 format), MUST mark as date table
// Otherwise time intelligence won't work correctly
```

### REMOVEFILTERS vs ALL for Time Intelligence

Both can clear filters, but with subtle differences:

```dax
// ALL - removes filters and returns all rows
// REMOVEFILTERS - only removes filters (preferred for clarity)

// Using ALL
Sales LY =
CALCULATE(
    [Total Sales],
    ALL('Date'),
    DATEADD('Date'[Date], -1, YEAR)
)

// Using REMOVEFILTERS (preferred)
Sales LY =
CALCULATE(
    [Total Sales],
    REMOVEFILTERS('Date'),
    DATEADD('Date'[Date], -1, YEAR)
)

// Key difference: In some contexts, ALL can affect table results
// REMOVEFILTERS only affects filter context, never the table
```

### Debugging Time Intelligence

```dax
// Test 1: Check if dates exist
Date Range Check =
"Min: " & MIN('Date'[Date]) & " Max: " & MAX('Date'[Date])

// Test 2: Check date count
Date Count = COUNTROWS('Date')

// Test 3: Verify SAMEPERIODLASTYEAR dates
SPLY Dates =
CONCATENATEX(
    SAMEPERIODLASTYEAR('Date'[Date]),
    FORMAT([Date], "yyyy-MM-dd"),
    ", "
)

// Test 4: Check for gaps in date table
Gap Check =
VAR MinDate = MIN('Date'[Date])
VAR MaxDate = MAX('Date'[Date])
VAR ExpectedDays = DATEDIFF(MinDate, MaxDate, DAY) + 1
VAR ActualDays = COUNTROWS('Date')
RETURN
IF(ExpectedDays = ActualDays, "No gaps", "Has " & (ExpectedDays - ActualDays) & " gaps")

// Test 5: Verify time intelligence context
Debug TI =
VAR CurrentContext = MAX('Date'[Date])
VAR SPLYContext =
    MAXX(SAMEPERIODLASTYEAR('Date'[Date]), [Date])
RETURN
"Current: " & CurrentContext & " | SPLY: " & SPLYContext
```

### Performance Considerations

1. **Date table size:** Keep it lean - only necessary columns
2. **Avoid row-level time calculations:** Use pre-calculated columns
3. **Use DATESINPERIOD for rolling calculations:** More efficient than FILTER
4. **Cache intermediate results with variables:** Avoid repeated time shifts

```dax
// SLOW - calculates time shift multiple times
Slow Growth =
DIVIDE(
    [Sales] - CALCULATE([Sales], SAMEPERIODLASTYEAR('Date'[Date])),
    CALCULATE([Sales], SAMEPERIODLASTYEAR('Date'[Date]))
)

// FAST - uses variables
Fast Growth =
VAR CurrentSales = [Sales]
VAR PYSales = CALCULATE([Sales], SAMEPERIODLASTYEAR('Date'[Date]))
RETURN
DIVIDE(CurrentSales - PYSales, PYSales)
```

---

## Quick Reference: Time Intelligence Functions

| Category | Function | Purpose |
|----------|----------|---------|
| **YTD** | TOTALYTD, DATESYTD | Year-to-date calculations |
| **QTD** | TOTALQTD, DATESQTD | Quarter-to-date calculations |
| **MTD** | TOTALMTD, DATESMTD | Month-to-date calculations |
| **Prior Period** | SAMEPERIODLASTYEAR, PREVIOUSYEAR/QUARTER/MONTH/DAY | Previous period values |
| **Next Period** | NEXTYEAR/QUARTER/MONTH/DAY | Future period values |
| **Shift** | DATEADD, PARALLELPERIOD | Move dates by interval |
| **Range** | DATESINPERIOD, DATESBETWEEN | Create date ranges |
| **Boundaries** | FIRSTDATE, LASTDATE, STARTOFYEAR/QUARTER/MONTH, ENDOFYEAR/QUARTER/MONTH | Period boundaries |
| **Balance** | OPENINGBALANCE*, CLOSINGBALANCE* | Semi-additive measures |
| **Last Value** | LASTNONBLANK, LASTNONBLANKVALUE | Last non-blank date/value |

---

## Additional Resources

- [SQLBI Time Intelligence](https://www.sqlbi.com/timeintelligence/) - Comprehensive patterns
- [DAX Patterns - Time Patterns](https://www.daxpatterns.com/time-patterns/) - Production-ready patterns
- [DAX Guide - Time Intelligence](https://dax.guide/functions/time-intelligence/) - Function reference
- [Calendar-based Time Intelligence (Preview)](https://www.sqlbi.com/articles/introducing-calendar-based-time-intelligence-in-dax/) - New 2025 features for non-Gregorian calendars
