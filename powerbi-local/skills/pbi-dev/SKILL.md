---
name: pbi-dev
description: >
  Power BI development assistance for semantic models and reports.
  Triggers on "Power BI", "DAX measure", "TMDL", "PBIR", "semantic model",
  "Power Query", "calculation group", "RLS", "row-level security",
  "create measure", "add column", "relationship", "visual", "report page".
auto_trigger: true
---

# Power BI Local Development

Develop Power BI semantic models and reports using local file formats (PBIP, TMDL, PBIR) combined with the Power BI MCP for live model interaction.

## Capabilities Overview

| Capability | Method | When to Use |
|------------|--------|-------------|
| Create/edit measures | TMDL files | Defining DAX business logic |
| Create/edit columns | TMDL files | Calculated columns, data types |
| Create/edit tables | TMDL files | New tables, partitions |
| Create/edit relationships | TMDL files | Model structure |
| Create/edit visuals | PBIR JSON files | Report layout and visualization |
| Create/edit pages | PBIR JSON files | Report structure |
| Execute DAX queries | MCP `execute_dax` | Testing, validation, data exploration |
| Validate TMDL | MCP `validate_tmdl` | Pre-deployment validation |
| Get model metadata | MCP tools | Discovering tables, columns, measures |

## When to Use MCP vs File Editing

### Use MCP Tools For:

- **Querying data**: `execute_dax` to run DAX queries and retrieve results
- **Exploring model**: `get_tables`, `get_measures`, `get_columns` to discover structure
- **Validating changes**: `validate_tmdl` before loading into Power BI Desktop
- **Quick testing**: Verify measure logic before committing to file

### Use Direct File Editing For:

- **Creating/modifying measures**: Edit `.tmdl` files in `definition/tables/`
- **Adding columns**: Edit table `.tmdl` files
- **Defining relationships**: Edit `definition/relationships.tmdl`
- **Building visuals**: Edit PBIR `visual.json` files
- **Page layout**: Edit `page.json` and create visual folders

## PBIP Folder Structure

```
ProjectName/
├── ProjectName.pbip                    # Project entry point
├── ProjectName.SemanticModel/          # Semantic model (TMDL)
│   ├── definition/
│   │   ├── model.tmdl                  # Model-level settings
│   │   ├── tables/
│   │   │   ├── Sales.tmdl              # Table with columns and measures
│   │   │   └── Calendar.tmdl
│   │   ├── relationships.tmdl          # All relationships
│   │   ├── roles/                      # RLS roles
│   │   └── cultures/                   # Translations
│   └── definition.pbism
└── ProjectName.Report/                 # Report (PBIR)
    ├── definition/
    │   ├── report.json                 # Report settings
    │   ├── pages/
    │   │   ├── pages.json              # Page order
    │   │   └── [pageName]/
    │   │       ├── page.json           # Page settings
    │   │       └── visuals/
    │   │           └── [visualName]/
    │   │               └── visual.json # Visual config
    │   └── bookmarks/
    └── definition.pbir
```

## Common Workflows

### 1. Create a New Measure

**Step 1**: Identify the target table by exploring the model:
```
Use MCP get_tables to list available tables
```

**Step 2**: Create the measure in the appropriate TMDL file:
```tmdl
// In definition/tables/Sales.tmdl, add under measures section:

measure 'Total Revenue' = SUM(Sales[Amount])
    formatString: "$#,##0.00"
    displayFolder: Revenue
```

**Step 3**: Validate and test:
```
Use MCP execute_dax:
EVALUATE ROW("Total Revenue", [Total Revenue])
```

### 2. Create a Calculated Column

Edit the table's TMDL file:
```tmdl
// In definition/tables/Sales.tmdl

column 'Profit Margin' =
    DIVIDE([Sales Amount] - [Cost], [Sales Amount])
    dataType: double
    formatString: "0.00%"
    summarizeBy: average
```

### 3. Create a Relationship

Edit `definition/relationships.tmdl`:
```tmdl
relationship 'Sales to Calendar'
    fromColumn: Sales.OrderDate
    toColumn: Calendar.Date
    crossFilteringBehavior: oneDirection
```

### 4. Create a Visual

**Step 1**: Create a visual folder in the page:
```
definition/pages/[pageName]/visuals/[newVisualId]/
```

**Step 2**: Create `visual.json` using templates from:
```
${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/pbir-templates/
```

Available templates:
- `clusteredColumnChart.json`
- `lineChart.json`
- `card.json`
- `tableEx.json`
- `slicer.json`
- `pieChart.json`

**Step 3**: Customize field bindings to match your model:
```json
{
  "field": {
    "Measure": {
      "Expression": {
        "SourceRef": { "Entity": "Sales" }
      },
      "Property": "Total Revenue"
    }
  },
  "queryRef": "Sales.Total Revenue"
}
```

### 5. Create Row-Level Security

**Step 1**: Create a role file in `definition/roles/`:
```tmdl
// definition/roles/RegionManager.tmdl

role RegionManager
    modelPermission: read
    tablePermission Sales = [Region] = USERPRINCIPALNAME()
```

### 6. Create a Calculation Group

```tmdl
// definition/tables/TimeIntelligence.tmdl

table TimeIntelligence
    lineageTag: generate-new-guid
    calculationGroup

    column Name
        dataType: string
        lineageTag: generate-new-guid
        summarizeBy: none
        sourceColumn: Name
        isNameInferred: true

    calculationItem YTD = CALCULATE(SELECTEDMEASURE(), DATESYTD('Calendar'[Date]))
    calculationItem PY = CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Calendar'[Date]))
    calculationItem YoY =
        VAR Current = SELECTEDMEASURE()
        VAR Previous = CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Calendar'[Date]))
        RETURN DIVIDE(Current - Previous, Previous)
```

## Reference Documents

Load these for detailed guidance:

| Reference | Path | Use For |
|-----------|------|---------|
| PBIR Schema | `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/pbir-schema.md` | Visual JSON structure |
| M Query Basics | `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/m-query-basics.md` | Power Query M language |
| Calculation Groups | `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/calculation-groups.md` | Time intelligence patterns |
| Troubleshooting | `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/troubleshooting.md` | Error resolution |
| Visual Templates | `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/pbir-templates/` | Starting points for visuals |

## Best Practices

### TMDL Best Practices

1. **Always include lineageTag**: Required for all tables, columns, and measures
2. **Use display folders**: Organize measures logically
3. **Format strings**: Always specify formatString for numeric measures
4. **Comments**: Use `//` for inline DAX documentation
5. **Indentation**: TMDL uses significant indentation - be consistent

### PBIR Best Practices

1. **Generate unique names**: Use 20-character alphanumeric IDs for visuals
2. **Validate JSON**: Ensure proper schema reference in all files
3. **Match field references**: Entity and Property must exactly match model
4. **Z-index management**: Visuals 0-1000, slicers 1000-2000, overlays 2000+

### MCP Best Practices

1. **Query before editing**: Use `get_tables` and `get_measures` to understand model
2. **Validate before loading**: Use `validate_tmdl` after file edits
3. **Test measures**: Use `execute_dax` to verify calculations

---

## Pre-Validation Workflow (IMPORTANT)

**ALWAYS run pre-validation before opening Power BI Desktop.** This catches most errors instantly without needing to launch the application.

### Pre-Validation Checklist

Run these checks AFTER making any changes, BEFORE opening .pbip in Power BI Desktop:

```
PRE-VALIDATION WORKFLOW:

1. TMDL SYNTAX VALIDATION
   ├─ Use MCP: validate_tmdl
   ├─ Check for: syntax errors, invalid references, missing lineageTags
   └─ Fix any errors before proceeding

2. DAX MEASURE VALIDATION (for new/modified measures)
   ├─ Use MCP: execute_dax with EVALUATE ROW("Test", [MeasureName])
   ├─ Check for: DAX errors, unexpected BLANK, division errors
   └─ Test with filter context if measure uses CALCULATE

3. RELATIONSHIP VALIDATION (for new/modified relationships)
   ├─ Use MCP: execute_dax with cross-table query
   │   EVALUATE SUMMARIZECOLUMNS(Dim[Column], "Value", [Measure])
   ├─ Check for: ambiguous relationships, missing data
   └─ Verify filter propagation direction

4. PBIR JSON VALIDATION (for new/modified visuals)
   ├─ Read the visual.json file
   ├─ Validate JSON syntax (no trailing commas, proper brackets)
   ├─ Check field references match model exactly:
   │   - Entity must match table name
   │   - Property must match measure/column name
   │   - queryRef must be "Entity.Property" format
   └─ Verify required fields exist (name, position, visual type)

5. FILE STRUCTURE VALIDATION
   ├─ Verify folder structure is correct
   ├─ Check file encoding (UTF-8)
   └─ Ensure no duplicate lineageTags

ONLY AFTER ALL CHECKS PASS → Open .pbip in Power BI Desktop
```

### Quick Pre-Validation Commands

**Validate TMDL syntax:**
```
Use MCP: validate_tmdl
```

**Test a measure:**
```
Use MCP execute_dax:
EVALUATE ROW("Result", [YourMeasure])
```

**Test measure with filters:**
```
Use MCP execute_dax:
EVALUATE CALCULATETABLE(ROW("Result", [YourMeasure]), Table[Column] = "Value")
```

**Test relationship:**
```
Use MCP execute_dax:
EVALUATE SUMMARIZECOLUMNS(DimTable[Key], "FactCount", COUNTROWS(FactTable))
```

**Validate JSON visuals (read and check):**
```
Read visual.json, verify:
- Valid JSON syntax
- "Entity" matches table name exactly
- "Property" matches measure name exactly
- All required visual properties present
```

### Pre-Validation Error Reference

| Error Type | How to Detect | Quick Fix |
|------------|---------------|-----------|
| TMDL syntax error | `validate_tmdl` fails | Check indentation, quotes, keywords |
| DAX error | `execute_dax` returns error | Check DAX syntax, column references |
| Missing lineageTag | `validate_tmdl` warns | Add `lineageTag: generate-guid` |
| Invalid relationship | Cross-table query fails | Check column names, cardinality |
| JSON syntax error | JSON parse fails | Check commas, brackets, quotes |
| Field reference error | Won't catch until PBI opens | Match Entity/Property to model exactly |
| Circular dependency | `execute_dax` error | Trace measure dependencies |

### When Pre-Validation Isn't Enough

Some issues can ONLY be detected by opening Power BI Desktop:

- Visual rendering/layout issues
- Theme and formatting appearance
- Cross-filtering interactions
- Custom visual compatibility
- Mobile layout rendering

For these, use the full validation workflow in `pbi-test` skill after pre-validation passes.

---

## Known Limitations

### Power BI Desktop Requirements

- **Windows only**: Power BI Desktop requires Windows
- **MSI version recommended**: Store version has external tool limitations
- **Model must be loaded**: MCP requires active Power BI Desktop session

### TMDL Limitations

- **Encoding**: Use UTF-8 with CRLF on Windows
- **No colons in names**: Colons in table/column names cause localization issues
- **Compatibility level**: May need to enable Dynamic Format Strings for full feature support

### PBIR Limitations

- **Auto-reload**: Some changes require closing and reopening Power BI Desktop
- **Schema versions**: Ensure PBIR schema matches your Power BI Desktop version
- **Custom visuals**: Must be installed in Power BI Desktop to render

## Quick Reference: DAX Patterns

### Aggregations
```dax
// Basic measures
Total Sales = SUM(Sales[Amount])
Order Count = COUNTROWS(Sales)
Average Sale = AVERAGE(Sales[Amount])
Distinct Customers = DISTINCTCOUNT(Sales[CustomerID])
```

### Time Intelligence
```dax
// Requires properly configured date table
YTD Sales = TOTALYTD([Total Sales], 'Calendar'[Date])
PY Sales = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Calendar'[Date]))
YoY Growth = DIVIDE([Total Sales] - [PY Sales], [PY Sales])
```

### Filtering
```dax
// CALCULATE with filters
Sales USA = CALCULATE([Total Sales], Geography[Country] = "USA")
Sales Last 30 Days = CALCULATE([Total Sales], DATESINPERIOD('Calendar'[Date], TODAY(), -30, DAY))
```

### Context Modification
```dax
// Remove filters
All Sales = CALCULATE([Total Sales], ALL(Sales))
Sales % of Total = DIVIDE([Total Sales], [All Sales])
```

## Error Resolution

For common errors and solutions, load the troubleshooting guide:
```
${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/troubleshooting.md
```

Common issues:
- MCP connection failures
- TMDL syntax errors
- Lineage tag conflicts
- DAX circular dependencies
- Visual rendering problems
