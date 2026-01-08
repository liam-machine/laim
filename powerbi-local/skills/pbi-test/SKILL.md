---
name: pbi-test
description: >
  Verify that newly developed Power BI features work as expected.
  Triggers on "test measure", "verify calculation", "check visual",
  "does this work", "test relationship", "validate DAX", "is it correct",
  "validate power bi", "open pbip", "test my changes".
auto_trigger: true
---

# Power BI Testing

Verify Power BI measures, visuals, relationships, and calculations work as expected.

## Automated Validation Loop

**IMPORTANT**: When Claude makes changes to Power BI files, use this automated loop to validate and self-correct until the report works correctly.

### Step 0: Pre-Validation (BEFORE opening Power BI Desktop)

**Always run pre-validation first - it's much faster than visual validation!**

```
PRE-VALIDATION CHECKS:

1. TMDL VALIDATION
   └─ Use MCP: validate_tmdl
   └─ Fix any syntax errors before proceeding

2. DAX TESTING (for each new/modified measure)
   └─ Use MCP execute_dax: EVALUATE ROW("Test", [MeasureName])
   └─ If error: fix DAX syntax in TMDL file, re-test
   └─ If BLANK unexpectedly: check filter context

3. RELATIONSHIP TESTING (for new/modified relationships)
   └─ Use MCP execute_dax: EVALUATE SUMMARIZECOLUMNS(Dim[Col], "Val", [Measure])
   └─ Verify data flows correctly across relationship

4. JSON VALIDATION (for new/modified visuals)
   └─ Read visual.json file
   └─ Check: valid JSON syntax, Entity/Property match model
   └─ Verify queryRef format: "TableName.MeasureName"

SELF-CORRECTION LOOP (Pre-validation):
   WHILE pre-validation errors exist:
       ├─ Identify error from MCP response
       ├─ Fix the source file (TMDL or JSON)
       ├─ Re-run the validation check
       └─ Continue until all checks pass

ONLY proceed to Step 1 when ALL pre-validation checks pass.
```

### Step 1: Open the PBIP File

Use computer use to open the .pbip file in Power BI Desktop:

```
1. Use computer use to find and double-click the .pbip file in File Explorer
   - Or use keyboard: Win+R, type the full path to the .pbip file, press Enter
   - Or if Power BI Desktop is open: Ctrl+O, navigate to file, open

2. Wait for Power BI Desktop to fully load (watch for loading indicators to disappear)
   - Take a screenshot to confirm the report is loaded
   - Look for: Report canvas visible, no spinning loaders, no error dialogs
```

### Step 2: Capture Baseline Screenshot

```
1. Navigate to the page containing your changes
   - Use Page Navigator pane or click page tabs at bottom

2. Click on empty canvas area to deselect any visual

3. Take screenshot using computer use

4. Analyze the screenshot for:
   - [ ] Report loaded successfully (no error banners)
   - [ ] Visuals render without error icons
   - [ ] Data appears in visuals (not empty/blank)
   - [ ] No "Unable to load" or "Error" messages
   - [ ] Formatting looks correct
```

### Step 3: Identify Issues

After taking a screenshot, analyze for these common issues:

| Visual Indicator | Issue | Likely Cause |
|------------------|-------|--------------|
| Red X icon on visual | Visual error | Invalid field reference, DAX error |
| Yellow warning triangle | Data warning | Missing data, relationship issue |
| Empty visual (no data) | No data returned | Filter too restrictive, wrong field |
| "Error" text | Calculation error | DAX syntax error, circular dependency |
| Broken layout | JSON error | Invalid PBIR visual.json |
| Missing visual | Visual not created | File not saved, JSON missing |

### Step 4: Self-Correction Loop

**If issues are found, iterate until fixed:**

```
REPEAT:
    1. IDENTIFY the specific error from screenshot

    2. DIAGNOSE root cause:
       - If DAX error: Check measure syntax in TMDL file
       - If visual error: Check visual.json structure
       - If data missing: Check relationships and filters
       - If layout broken: Validate JSON against schema

    3. FIX the issue:
       - Edit the relevant TMDL or JSON file
       - Save the file

    4. REFRESH in Power BI Desktop:
       - Computer use: Click "Refresh" button in ribbon
       - Or: Press Ctrl+Shift+R (refresh all)
       - Or: For model changes, close and reopen .pbip

    5. SCREENSHOT again to verify fix

    6. ANALYZE new screenshot:
       - If issue persists: Go to step 2, try different fix
       - If new issue appears: Add to fix list, continue
       - If all issues resolved: Exit loop, report success

UNTIL: All visuals render correctly with expected data
```

### Step 5: Final Validation

Once visuals look correct, perform data validation:

```
1. Use MCP execute_dax to query the measure values
2. Compare DAX results to values shown in screenshot
3. If values match: Validation complete
4. If values differ: Investigate filter context differences
```

## Testing Methods

| Test Type | Method | When to Use |
|-----------|--------|-------------|
| Measure validation | MCP `execute_dax` | Verify DAX calculations |
| Visual verification | Computer use (screenshots) | Confirm visual renders correctly |
| Relationship testing | DAX filter propagation queries | Verify relationships work |
| RLS testing | MCP `execute_dax` with USERPRINCIPALNAME | Test security roles |
| Cross-validation | Compare to expected values | Validate against known data |
| **Full validation** | **Automated loop (above)** | **After any Claude changes** |

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

---

## Complete Validation Workflow

**Use this workflow after making ANY changes to Power BI files to automatically validate and self-correct.**

### Prerequisites

- Power BI Desktop installed on Windows
- Computer use capability enabled
- PBIP file path known

### Full Automated Workflow

```
WORKFLOW: validate_powerbi_changes

INPUT: pbip_file_path (path to .pbip file)
INPUT: changes_made (list of files/items changed)

0. PRE-VALIDATION (Fast - no Power BI Desktop needed)
   ├─ For TMDL changes:
   │   ├─ Use MCP: validate_tmdl
   │   └─ LOOP: Fix errors → re-validate → until clean
   │
   ├─ For measure changes:
   │   ├─ Use MCP execute_dax: EVALUATE ROW("Test", [MeasureName])
   │   └─ LOOP: Fix DAX → re-test → until works
   │
   ├─ For relationship changes:
   │   ├─ Use MCP execute_dax with cross-table query
   │   └─ LOOP: Fix relationship → re-test → until works
   │
   ├─ For visual JSON changes:
   │   ├─ Read and validate JSON syntax
   │   ├─ Verify Entity/Property match model
   │   └─ LOOP: Fix JSON → re-read → until valid
   │
   └─ GATE: All pre-validation must pass before proceeding
           If stuck after 5 attempts, report to user

1. OPEN POWER BI FILE (Only after pre-validation passes)
   ├─ Use computer use: screenshot current desktop state
   ├─ Locate .pbip file:
   │   └─ computer_use: Win+E to open Explorer
   │   └─ computer_use: navigate to pbip_file_path
   │   └─ computer_use: double-click the .pbip file
   ├─ Wait for Power BI Desktop to launch
   │   └─ computer_use: screenshot every 3-5 seconds
   │   └─ Check for: Power BI window visible, loading complete
   └─ Confirm loaded:
       └─ computer_use: screenshot
       └─ Verify: Report canvas visible, no error dialogs

2. NAVIGATE TO CHANGED CONTENT
   ├─ For each page with changes:
   │   └─ computer_use: click page tab or use Page Navigator
   │   └─ computer_use: screenshot the page
   └─ For model changes (measures, relationships):
       └─ computer_use: open Model view (click Model icon in left sidebar)
       └─ computer_use: screenshot to verify structure

3. CAPTURE AND ANALYZE
   ├─ computer_use: screenshot current view
   ├─ Analyze screenshot for errors:
   │   ├─ Red X icons = Visual errors
   │   ├─ Yellow triangles = Warnings
   │   ├─ Empty visuals = No data
   │   ├─ Error dialogs = Fatal errors
   │   └─ Broken layout = JSON issues
   └─ Record all issues found

4. SELF-CORRECTION LOOP
   ├─ WHILE issues exist:
   │   │
   │   ├─ For EACH issue:
   │   │   ├─ Diagnose: Read relevant file (TMDL/JSON)
   │   │   ├─ Fix: Edit the file to correct the issue
   │   │   └─ Save: Write the corrected file
   │   │
   │   ├─ Refresh Power BI:
   │   │   ├─ If TMDL change:
   │   │   │   └─ computer_use: Ctrl+Shift+R (refresh)
   │   │   │   └─ OR: Close and reopen .pbip for model changes
   │   │   └─ If JSON change:
   │   │       └─ computer_use: Ctrl+Shift+R (refresh)
   │   │
   │   ├─ Wait for refresh complete:
   │   │   └─ computer_use: screenshot to check loading state
   │   │
   │   ├─ Re-analyze:
   │   │   └─ computer_use: screenshot
   │   │   └─ Check if issues resolved
   │   │   └─ Check for NEW issues introduced
   │   │
   │   └─ Update issue list
   │
   └─ EXIT when: No errors visible in screenshot

5. DATA VALIDATION
   ├─ For each measure changed:
   │   ├─ Use MCP execute_dax to query measure value
   │   ├─ Compare to value shown in visual (from screenshot)
   │   └─ If mismatch: investigate filter context
   └─ For relationships:
       └─ Use MCP execute_dax with cross-table query to verify

6. FINAL CONFIRMATION
   ├─ computer_use: screenshot full report
   ├─ Verify all visuals render correctly
   ├─ Report validation status to user:
   │   ├─ SUCCESS: All changes validated, report works correctly
   │   └─ PARTIAL: Some issues remain (list them)
   └─ Provide summary of iterations and fixes made

OUTPUT: validation_result (success/partial/failed)
OUTPUT: fixes_applied (list of corrections made)
OUTPUT: final_screenshot (proof of working state)
```

### Quick Validation Commands

**Validate after measure change:**
```
1. Open pbip file using computer use
2. Screenshot the visual using the measure
3. Run: MCP execute_dax: EVALUATE ROW("Result", [ChangedMeasure])
4. Compare screenshot value to DAX result
```

**Validate after visual change:**
```
1. Open pbip file using computer use
2. Navigate to page with visual
3. Screenshot and verify:
   - Visual renders (no error icon)
   - Data appears correctly
   - Formatting matches expectation
```

**Validate after relationship change:**
```
1. Open pbip file using computer use
2. Open Model view, screenshot to verify relationship line exists
3. Run: MCP execute_dax: EVALUATE SUMMARIZECOLUMNS(Dim[Col], "Value", [Measure])
4. Verify filter propagation works
```

### Computer Use Actions Reference

**Requires `computer-control` MCP server. Install with:**
```bash
claude mcp add computer-control -- uvx computer-control-mcp@latest
```

| Action | MCP Tool | Example |
|--------|----------|---------|
| Take screenshot | `screenshot` | Capture current screen state |
| Move mouse | `mouse_move` | Move to coordinates (x, y) |
| Click | `mouse_click` | Click at current position |
| Double-click | `mouse_double_click` | Open files |
| Type text | `type_text` | Enter file paths, text |
| Press key | `press_key` | Ctrl+O, Ctrl+S, Enter |
| Key combo | `hotkey` | Ctrl+Shift+R (refresh) |
| Get window list | `get_windows` | Find Power BI Desktop |
| Focus window | `focus_window` | Bring window to front |
| OCR screen | `ocr` | Read text from screenshot |

### Example Computer Use Sequence

```
1. screenshot                     # See current state
2. get_windows                    # Find "Power BI Desktop" window
3. focus_window "Power BI"        # Bring to front
4. hotkey ["ctrl", "o"]           # Open file dialog
5. type_text "C:\path\to\report.pbip"
6. press_key "enter"              # Open file
7. screenshot                     # Wait and verify loaded
8. ocr                            # Read any error messages
```

### Max Iterations

To prevent infinite loops, limit self-correction to **5 iterations**. If issues persist after 5 attempts:

1. Report the remaining issues to the user
2. Provide diagnostic information (screenshots, error messages)
3. Ask for user guidance on how to proceed
