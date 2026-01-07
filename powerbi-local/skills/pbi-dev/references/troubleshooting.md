# Power BI Troubleshooting Guide

This guide covers common issues when developing Power BI solutions with Claude Code, the Power BI MCP, TMDL, and PBIR formats.

---

## 1. MCP Connection Issues

### Power BI Desktop Not Detected

**Symptoms:**
- MCP returns "Power BI Desktop is not connected"
- Connection verification fails
- "Unknown server" errors in Claude Code

**Causes and Solutions:**

| Cause | Solution |
|-------|----------|
| Power BI Desktop not running | Open Power BI Desktop and load your .pbix or .pbip file |
| Model not fully loaded | Wait for data model to load completely (verify table count in Data view) |
| Using Microsoft Store version | Install the MSI/EXE version from powerbi.microsoft.com instead |
| Multiple Desktop instances | Close all instances and open only one - MCP connects to most recent |
| TOM_DLL_PATH misconfigured | Set `TOM_DLL_PATH` environment variable to Analysis Services DLL location |
| COM automation blocked | Check Task Manager > Details > PBIDesktop.exe properties |

**Verification Steps:**
1. Open Power BI Desktop
2. Open your .pbix or .pbip file
3. Wait for data model to fully load (check Data view table count)
4. Ensure MCP server is configured in `.claude.json` or `.mcp.json`
5. Completely quit and restart Claude Code (not just close window)

**Store vs MSI Version:**

The Microsoft Store version has limitations with external tools:
- Path and permission restrictions may interfere with MCP connections
- SAP connectors may require moving driver files to `Windows\System32`
- Admin privileges not required, but external tool compatibility is reduced

**Recommendation:** Always use the MSI installer from [powerbi.microsoft.com](https://powerbi.microsoft.com/desktop) for development workflows.

---

### Authentication Failures (Fabric Connection)

**AADSTS500113 Error:**

```
Error: AADSTS500113: No reply address is registered for the application
```

**Cause:** The Azure AD App Registration used by the MCP server for Fabric authentication lacks a configured Redirect URI.

**Solutions:**

1. **Check Microsoft's documentation** - This may be a known limitation during MCP rollout:
   > "Connecting to a Semantic Model in a Fabric workspace may not work in your tenant due to the ongoing rollout of the client ID used for authentication."

2. **If using custom app registration:**
   - Go to Azure Portal > Microsoft Entra ID > App registrations
   - Find your application
   - Navigate to Authentication under Manage
   - Add the correct Redirect URI that matches your application's callback URL

3. **Additional steps if CORS blocking:**
   - Add `login.microsoft.com` to your allowed CORS list
   - This resolved issues for some users even with correct redirect URIs

**Token Generation Failures:**

| Symptom | Solution |
|---------|----------|
| Token refresh fails | Re-authenticate in Power BI Desktop first |
| MFA required error | Complete MFA in browser, then retry MCP connection |
| Conditional access blocks | Ensure device meets tenant security policies |

---

### Platform-Specific Issues

**Windows Requirements:**

| Requirement | Notes |
|-------------|-------|
| Windows 10/11 | Power BI Desktop is Windows-only |
| Admin rights (MSI install) | Required for initial installation |
| Admin rights (runtime) | Not required for normal operation |
| External tools access | May need to enable in Power BI options |

**macOS/Apple Silicon:**

Power BI Desktop does not have a native macOS version. Alternatives:

| Option | Notes |
|--------|-------|
| Parallels Desktop | Run Windows 11 ARM with x64 emulation |
| VMware Fusion | Another virtualization option for M1/M2/M3 Macs |
| Windows 365 Cloud PC | Stream Windows from the cloud |
| Power BI Service (web) | Limited authoring capabilities in browser |

**WSL Considerations:**

- Power BI Desktop runs in Windows, not in WSL
- MCP server can run in either Windows or WSL
- If running MCP in WSL, ensure proper localhost network access
- File paths must be Windows paths when connecting to Desktop

---

## 2. TMDL Errors

### Syntax Errors

**Common TMDL Syntax Mistakes:**

| Error | Cause | Fix |
|-------|-------|-----|
| `InvalidLineType` | Wrong encoding or newline style | Use UTF-8 with CRLF on Windows |
| Parsing error | Incorrect indentation | TMDL uses indentation for structure |
| Invalid path | Colon in filename (localization issue) | Rename tabs/files to remove colons |

**Compatibility Level Errors:**

```
Error: The database compatibility level of 1550 is below the minimal compatibility level of 1567
```

**Fix:** Create a dummy calculation group and enable "Dynamic Format Strings" to raise compatibility level to 1601.

**Unsupported Partitions Error:**

```
Error: ...unsupported partitions...
```

**Fix:** The model needs at least one Power Query expression. Create a dummy table using "Enter data" feature.

---

### Lineage Tag Issues

**Duplicated Lineage Tags:**

When copying TMDL code between models, lineage tags get duplicated.

**Problem:**
```tmdl
measure 'Total Sales' = SUM(Sales[Amount])
    lineageTag: abc123-def456  // Copied from another model!
```

**Solution:**
1. Remove the `lineageTag` line before pasting
2. Deploy the model - Power BI will generate a new unique tag
3. Or use the VS Code TMDL extension's "Generate lineage tag" code action

**Missing Required Properties:**

Power BI Desktop will display an error if required properties are missing:

```
Error: There's a problem with the definition content in your Power BI Project
```

**Common missing properties:**
- `lineageTag` on tables, columns, measures
- `sourceColumn` on columns
- `dataType` on columns

Use the TMDL View's built-in error diagnostics or VS Code TMDL extension to identify issues.

---

### DAX Expression Errors

**Invalid Column/Measure References:**

```
Error: A single value for column cannot be determined
```

**Cause:** Column reference without row context or aggregation.

**Fix:** Use aggregation functions (SUM, COUNT, etc.) or ensure row context exists.

**Context Transition Issues:**

```
Error: The expression contains columns from multiple tables
```

**Cause:** CALCULATE filter predicate references columns from multiple tables.

**Fix:** Use FILTER function to create a table filter instead:
```dax
// Wrong
CALCULATE([Sales], Products[Category] = "A" && Sales[Amount] > 100)

// Correct
CALCULATE(
    [Sales],
    FILTER(Products, Products[Category] = "A"),
    FILTER(Sales, Sales[Amount] > 100)
)
```

**Circular Dependency Detection:**

```
Error: A circular dependency was detected
```

**Common causes:**
1. Two calculated columns referencing each other
2. Multiple CALCULATE expressions in calculated columns
3. Measure referencing itself indirectly

**Solutions:**
1. Use `ALLEXCEPT` to restrict context transition dependencies
2. Convert calculated columns to measures
3. Use variables to break dependency cycles
4. Use `ALLNOBLANKROW` instead of `ALL` in predicates

---

### Validation Failures

**How to Validate TMDL Before Loading:**

1. **Power BI Desktop TMDL View:**
   - Open TMDL view (View > TMDL view)
   - Errors appear in Problems pane
   - Hover over squiggles for detailed messages

2. **VS Code TMDL Extension:**
   - Install Microsoft TMDL extension
   - Open .tmdl files - validation is automatic
   - Use code actions (light bulb) for quick fixes

3. **MCP validate_tmdl Tool:**
   ```
   Use the validate_tmdl MCP tool to check syntax before importing
   ```

4. **Tabular Editor:**
   - Open TMDL folder in Tabular Editor
   - Check for validation errors in Messages pane

---

## 3. PBIR/Report Issues

### Visual Not Rendering

**Symptoms:**
- Visual shows error icon
- Visual placeholder appears but no data
- "Can't display this visual" message

**Common Causes:**

| Cause | Fix |
|-------|-----|
| Invalid visual.json structure | Validate against schema using VS Code |
| Missing required properties | Check schema URL in visual.json for requirements |
| Field reference mismatches | Ensure column/measure names match model exactly |
| Visual type not available | Check if custom visual is installed |

**Validation with VS Code:**

PBIR JSON files include schema URLs. VS Code provides:
- IntelliSense for available properties
- Validation errors for wrong property types
- Red squiggles for schema violations

---

### Report Won't Load

**Blocking Errors:**

These prevent Power BI Desktop from opening the report:
- Invalid JSON schema
- Missing required properties
- Syntax errors in JSON files

**Fix:** Open the problematic file in VS Code and inspect schema errors.

**Non-Blocking Errors:**

These are automatically fixed by Power BI Desktop:
- Invalid `activePageName` configuration
- Minor metadata inconsistencies

**Common Problem Files:**

| File | Common Issues |
|------|---------------|
| `report.json` | Invalid metadata, wrong schema version |
| `pages.json` | Missing page references, invalid page names |
| `visual.json` | Field bindings don't match model |

**Schema Version Mismatches:**

If report was created in newer Power BI Desktop version:
1. Check the schema version in JSON files
2. Update Power BI Desktop to latest version
3. Or manually adjust schema version (risky)

---

### Changes Not Appearing

**Power BI Desktop Caching:**

Power BI Desktop caches model and report data. Changes may not appear immediately.

**Solutions:**

| Symptom | Fix |
|---------|-----|
| TMDL changes not reflected | Save and wait for auto-reload, or close/reopen report |
| PBIR changes not visible | Close and reopen the .pbip project |
| Measure values seem stale | Refresh visuals (right-click > Refresh) |
| Model structure outdated | Close Power BI Desktop completely and reopen |

**Auto-Refresh Limitations:**

- TMDL changes typically auto-reload when files are saved
- PBIR (report) changes may require closing and reopening
- Some changes require full Desktop restart

**After External Editing:**

If you edit PBIR files outside Power BI Desktop:
1. Save all changes
2. Close Power BI Desktop completely
3. Reopen the .pbip file
4. Check for error messages about file modifications

---

## 4. Common DAX Issues

### Measure Returns Blank

**Checklist:**

1. **Missing relationships:**
   - Check Model view for relationships between tables
   - Verify relationship direction and cardinality

2. **Filter context problems:**
   - Are filters excluding all data?
   - Use DAX query to test without visual filters:
     ```dax
     EVALUATE ROW("Value", [Your Measure])
     ```

3. **CALCULATE usage errors:**
   - Conflicting filters eliminating all rows
   - Filter on date table for "this year" + filter on fact table for "last year" = empty

4. **BLANK propagation:**
   - BLANK * anything = BLANK
   - BLANK / anything = BLANK
   - Use `COALESCE` or `IF(ISBLANK(...))` to handle

**Debugging Steps:**

```dax
// Test measure without any filter context
EVALUATE ROW("Result", [Your Measure])

// Test with specific filter
EVALUATE
CALCULATETABLE(
    ROW("Result", [Your Measure]),
    'Date'[Year] = 2024
)
```

---

### Time Intelligence Not Working

**Date Table Requirements:**

| Requirement | Description |
|-------------|-------------|
| Continuous dates | No gaps in date sequence |
| One row per day | Each date appears exactly once |
| Date column | Must be Date or DateTime data type |
| Covers all data | Range must encompass all fact table dates |
| Marked as date table | Required for proper time intelligence |

**Common Mistakes:**

1. **Not marking as date table:**
   - Right-click table > Mark as date table
   - Select the date column

2. **Using dates from fact table:**
   - Always use dates from the Date dimension table
   - Create relationships to Date table

3. **Missing date context:**
   - PREVIOUSMONTH returns BLANK without date context
   - Ensure date field is in visual or filter

**Fix with ALL Function:**

If time intelligence returns wrong values:
```dax
Fixed Sales YTD =
CALCULATE(
    SUM(Sales[Amount]),
    DATESYTD('Calendar'[Date]),
    ALL('Calendar')  // Remove conflicting filters
)
```

---

### Performance Problems

**Avoid Row-by-Row Iteration:**

| Slow Pattern | Fast Alternative |
|--------------|------------------|
| `SUMX(table, IF(...))` | `CALCULATE(SUM(), FILTER())` |
| Nested SUMX | Use variables to store intermediate results |
| Complex FILTER in iterator | Pre-filter with CALCULATETABLE |

**SUMX vs SUM Patterns:**

```dax
// Slow - iterates every row
Total = SUMX(Sales, Sales[Qty] * Sales[Price])

// Fast - if you have a calculated column
Total = SUM(Sales[LineTotal])

// Balanced - use variables
Total =
VAR SalesTable = Sales
RETURN SUMX(SalesTable, [Qty] * [Price])
```

**Variable Usage for Optimization:**

```dax
// Calculate expensive values once
Optimized Measure =
VAR TotalSales = [Total Sales]
VAR TotalCost = [Total Cost]
VAR OrderCount = [Order Count]
RETURN
DIVIDE(TotalSales - TotalCost, OrderCount)
```

---

## 5. Relationship Problems

### Filter Not Propagating

**Cross-Filter Direction Settings:**

| Direction | Behavior |
|-----------|----------|
| Single | Filters flow from "one" to "many" side only |
| Both | Filters flow in both directions |

**Check relationship settings:**
1. Open Model view
2. Double-click relationship line
3. Check "Cross filter direction"

**Inactive Relationships:**

- Only one active relationship between tables
- Additional relationships are inactive
- Use USERELATIONSHIP to activate:
  ```dax
  Sales by Ship Date =
  CALCULATE(
      [Total Sales],
      USERELATIONSHIP(Sales[ShipDate], 'Date'[Date])
  )
  ```

**Ambiguous Paths:**

Power BI prevents filter ambiguity:
- Cannot have two bidirectional relationships that create multiple filter paths
- Error: "There is already an existing bidirectional relationship"

**Solution:** Use CROSSFILTER in DAX instead of model-level bidirectional:
```dax
Filtered Value =
CALCULATE(
    [Measure],
    CROSSFILTER(Table1[Key], Table2[Key], BOTH)
)
```

---

### Many-to-Many Issues

**Composite Model Requirements:**

Many-to-many relationships create "limited relationships":
- Not materialized (slower performance)
- Require careful filter handling

**Bridge Table Pattern:**

For proper many-to-many handling:

```
Customer ─── CustomerProduct ─── Product
    1:*           *:1
```

1. Create bridge table with foreign keys from both tables
2. Create one-to-many from Customer to Bridge
3. Create many-to-one from Bridge to Product
4. Set ONE relationship as bidirectional
5. Hide the bridge table from report view

**Performance Considerations:**

- Bridge tables add query complexity
- Use only when necessary
- Consider denormalization for performance-critical reports

---

## 6. Recovery Procedures

### Reverting Changes

**Git Integration with PBIP:**

PBIP format enables proper version control:

```bash
# View what changed
git diff

# Revert specific file
git checkout -- MyReport.SemanticModel/definition/tables/Sales.tmdl

# Revert all changes
git checkout -- .

# Go back to previous commit
git reset --hard HEAD~1
```

**Manual Backup Restoration:**

If not using Git:
1. Check `%LOCALAPPDATA%\Microsoft\Power BI Desktop\TempSaves`
2. Previous versions may be available
3. Copy .pbix files from backup location

**TMDL Folder Recovery:**

If TMDL folder is corrupted:
1. Keep a known-good backup of the SemanticModel folder
2. Replace corrupted files from backup
3. Validate with VS Code TMDL extension before opening

---

### When Things Break

**Report Won't Open:**

1. Check `pages.json` for valid page references
2. Validate JSON syntax in all definition files
3. Look for schema errors in VS Code
4. Check Power BI Desktop error message for specific file

**Model Won't Load:**

1. Validate TMDL syntax using VS Code extension
2. Check `model.tmdl` for basic errors
3. Verify all table files in `tables/` folder
4. Look for circular dependency errors

**Visual Errors:**

1. Identify the problematic visual folder in `pages/[page]/visuals/`
2. Check `visual.json` against schema
3. If unfixable, delete the entire visual folder
4. Recreate the visual in Power BI Desktop

**Emergency Recovery:**

If nothing else works:
1. Export to PBIX format (if possible)
2. Create new PBIP project
3. Rebuild report incrementally
4. Use TMDL export/import to recover semantic model

---

## Quick Reference: Error Messages

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| "Power BI Desktop is not connected" | Desktop not running or wrong version | Open Desktop, load file, use MSI version |
| "AADSTS500113" | Azure AD redirect URI missing | Check app registration in Azure Portal |
| "Circular dependency detected" | Self-referencing calculations | Use variables, convert to measures |
| "Compatibility level too low" | Old model format | Enable Dynamic Format Strings |
| "InvalidLineType" | Encoding or newline issues | Use UTF-8 with CRLF |
| "A single value cannot be determined" | Missing aggregation | Add SUM, COUNT, etc. |
| "Columns from multiple tables" | Invalid CALCULATE predicate | Use separate FILTER for each table |

---

## Additional Resources

- [Power BI MCP GitHub Issues](https://github.com/microsoft/powerbi-modeling-mcp/issues)
- [TMDL Documentation](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview)
- [PBIR Report Format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- [SQLBI DAX Articles](https://www.sqlbi.com/articles/)
- [Microsoft Fabric Community](https://community.fabric.microsoft.com/)
