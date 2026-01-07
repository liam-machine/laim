---
description: Test and verify Power BI features
argument-hint: "[measure/visual/relationship to test]"
skill: pbi-test
---

# Power BI Testing

Verify that Power BI measures, visuals, and relationships work correctly.

## Testing Workflow

1. **Identify what to test** (measure, visual, relationship)
2. **Choose test method** (DAX query or screenshot)
3. **Execute test**
4. **Verify results**

## Quick Test Commands

### Test a Measure

Use MCP `execute_dax`:
```dax
EVALUATE ROW("Result", [Your Measure Name])
```

### Test with Filter Context

```dax
EVALUATE
CALCULATETABLE(
    ROW("Result", [Your Measure]),
    Table[Column] = "FilterValue"
)
```

### Compare Values

```dax
EVALUATE
ROW(
    "Actual", [Your Measure],
    "Expected", 12345,
    "Pass", IF([Your Measure] = 12345, "YES", "NO")
)
```

### Test Relationship

```dax
EVALUATE
SUMMARIZECOLUMNS(
    DimTable[Column],
    "Measure", [Your Measure]
)
```

## Testing Methods

| What to Test | Method |
|--------------|--------|
| Measure value | MCP `execute_dax` |
| Measure with filters | MCP `execute_dax` with CALCULATE |
| Visual rendering | Computer use (screenshot) |
| Cross-filtering | Screenshot before/after click |
| Relationship | DAX query across tables |
| RLS | DAX with filter simulation |

## Test Patterns

### Time Intelligence
```dax
EVALUATE
ADDCOLUMNS(
    VALUES('Calendar'[Year]),
    "YTD", [YTD Sales],
    "PY", [PY Sales],
    "YoY", [YoY Growth]
)
```

### Edge Cases
```dax
EVALUATE
ROW(
    "Empty Context", CALCULATE([Measure], FILTER(ALL(Table), FALSE())),
    "Null Values", CALCULATE([Measure], Table[Col] = BLANK())
)
```

### Validation
```dax
EVALUATE
ROW(
    "Measure", [Total Sales],
    "Raw SUM", SUM(Sales[Amount]),
    "Match", IF([Total Sales] = SUM(Sales[Amount]), "YES", "NO")
)
```

## Reference

Full testing methodology: `${CLAUDE_PLUGIN_ROOT}/skills/pbi-test/references/testing-guide.md`

## What Would You Like to Test?

Please specify:
- **Measure name** to test
- **Visual** to verify
- **Relationship** to check
- **Expected values** (if validating)
