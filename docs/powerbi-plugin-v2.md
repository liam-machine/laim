# Power BI Local Development Plugin

**Native-first Power BI development with Claude Code using Microsoft MCP and Computer Use on Windows.**

This document specifies the architecture for a Claude Code plugin that enables local Power BI development, leveraging Microsoft's official MCP servers and Claude's native computer use capabilities.

---

## Overview

### Key Capabilities

| Capability | Method |
|------------|--------|
| Edit DAX measures | Power BI MCP or direct TMDL file editing |
| Edit report layouts | Direct PBIR JSON editing |
| Execute DAX queries | Power BI MCP |
| Preview reports | Claude computer use + Power BI Desktop |
| Take screenshots | Claude computer use |
| Click on visuals/filters | Claude computer use |
| Verify new features work | Claude computer use + MCP DAX execution |
| Deploy to Fabric | Power BI MCP or Fabric Git Integration |

### Requirements

- **Windows 10/11** (Power BI Desktop is Windows-only)
- **Power BI Desktop** (non-Store version recommended)
- **Node.js 18+** for MCP servers
- **Claude Code** with computer use enabled

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              CLAUDE CODE                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────────┐  │
│  │ Native Computer Use     │    │ Microsoft Power BI MCP                  │  │
│  │ (built-in)              │    │ @microsoft/powerbi-modeling-mcp         │  │
│  ├─────────────────────────┤    ├─────────────────────────────────────────┤  │
│  │ • screenshot            │    │ • connect (Desktop, Fabric, TMDL)       │  │
│  │ • mouse_move / click    │    │ • execute_dax                           │  │
│  │ • type / key            │    │ • list_tables / list_measures           │  │
│  │ • scroll                │    │ • create_measure / update_measure       │  │
│  │ • visual understanding  │    │ • import_tmdl / export_tmdl             │  │
│  └───────────┬─────────────┘    │ • deploy_to_fabric                      │  │
│              │                  └──────────────────┬──────────────────────┘  │
│              │                                     │                         │
│              ▼                                     ▼                         │
│       ┌──────────────────────────────────────────────────────────────────┐  │
│       │                    Power BI Desktop                               │  │
│       │                                                                   │  │
│       │  ┌──────────────┐    ┌──────────────────────────────────────┐   │  │
│       │  │ Report View  │    │ Local Analysis Services (SSAS)       │   │  │
│       │  │              │◄───│ localhost:random_port                │   │  │
│       │  │ (Visuals,    │    │                                      │   │  │
│       │  │  Filters,    │    │ ◄── MCP connects here               │   │  │
│       │  │  Pages)      │    │                                      │   │  │
│       │  └──────────────┘    └──────────────────────────────────────┘   │  │
│       └──────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ powerbi-local Plugin                                                   │  │
│  ├───────────────────────────────────────────────────────────────────────┤  │
│  │ pbi:dev           │ References, patterns, best practices              │  │
│  │ pbi:test          │ Verify new features work as expected              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         File System                                    │  │
│  │                                                                        │  │
│  │  MyReport.pbip                                                         │  │
│  │  ├── MyReport.Report/                                                  │  │
│  │  │   └── definition/                                                   │  │
│  │  │       ├── report.json                                               │  │
│  │  │       └── pages/                                                    │  │
│  │  │           └── *.json (PBIR)                                         │  │
│  │  │                                                                     │  │
│  │  └── MyReport.SemanticModel/                                           │  │
│  │      └── definition/                                                   │  │
│  │          ├── model.tmdl                                                │  │
│  │          ├── tables/                                                   │  │
│  │          │   └── *.tmdl                                                │  │
│  │          └── expressions.tmdl (M queries)                              │  │
│  │                                                                        │  │
│  │  Claude reads/writes these files directly                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## MCP Configuration

### Local Power BI Desktop

Connect to a running Power BI Desktop instance on your Windows machine:

```json
{
  "mcpServers": {
    "powerbi": {
      "command": "npx",
      "args": ["-y", "@microsoft/powerbi-modeling-mcp@latest"],
      "description": "Power BI semantic model operations via local Desktop"
    }
  }
}
```

### Direct TMDL Project (No Desktop Required)

For editing PBIP/TMDL files without opening Power BI Desktop:

```json
{
  "mcpServers": {
    "powerbi-tmdl": {
      "command": "npx",
      "args": [
        "-y", "@microsoft/powerbi-modeling-mcp@latest",
        "--mode", "tmdl",
        "--path", "./MyReport.SemanticModel"
      ],
      "description": "Direct TMDL folder editing"
    }
  }
}
```

---

## Power BI MCP Capabilities

The Microsoft Power BI Modeling MCP provides these tools:

### Connection Management

| Tool | Description |
|------|-------------|
| `connect` | Connect to Desktop instance or TMDL folder |
| `disconnect` | Disconnect from current model |
| `list_connections` | Show all active connections |
| `get_model_info` | Get database name, compatibility level, size |

### Model Exploration

| Tool | Description |
|------|-------------|
| `list_tables` | List all tables with row counts |
| `list_columns` | List columns for a table with types |
| `list_measures` | List measures with expressions |
| `list_relationships` | Show model relationships |
| `list_calculation_groups` | List calculation groups and items |
| `list_roles` | List RLS roles and expressions |

### Model Modification

| Tool | Description |
|------|-------------|
| `create_measure` | Add new measure with DAX |
| `update_measure` | Modify existing measure |
| `delete_measure` | Remove a measure |
| `create_calculated_column` | Add calculated column |
| `create_table` | Create new table from DAX |
| `create_relationship` | Add relationship between tables |
| `create_role` | Add RLS role with filter expressions |

### DAX Execution

| Tool | Description |
|------|-------------|
| `execute_dax` | Run DAX query, return results |
| `evaluate_measure` | Test measure with specific filter context |
| `get_dependencies` | Show measure/column dependencies |

### TMDL Operations

| Tool | Description |
|------|-------------|
| `export_tmdl` | Export model to TMDL folder |
| `import_tmdl` | Import TMDL folder to model |
| `validate_tmdl` | Syntax check TMDL files |

---

## Claude Computer Use for UI Interaction

For interactive Power BI development, Claude uses native computer use capabilities to interact with Power BI Desktop.

### Common Operations

**Navigate to a page:**
```
Claude takes a screenshot, identifies the page tab "Sales Overview",
clicks on it, waits for render, takes another screenshot to verify.
```

**Test a slicer:**
```
Claude screenshots the report, identifies the Region slicer,
clicks "West", waits for visuals to update, screenshots result,
analyzes the chart values to verify filtering worked.
```

**Verify a measure change:**
```
Claude uses MCP to update measure DAX,
uses computer use to screenshot the visual showing that measure,
compares before/after to confirm the change took effect.
```

### Why Native Computer Use

| Aspect | Benefit |
|--------|---------|
| Element finding | AI visual understanding - no brittle selectors |
| Adaptability | Works across Power BI Desktop versions |
| Debugging | Natural language explanation of what it sees |
| Maintenance | Zero maintenance - no scripts to update |
| Setup | Built into Claude Code |

---

## Plugin Structure

```
powerbi-local/
├── .claude-plugin/
│   └── plugin.json
│
├── skills/
│   ├── pbi-dev/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── tmdl-syntax.md           # TMDL language reference
│   │       ├── tmdl-examples.md         # Common patterns
│   │       ├── pbir-schema.md           # PBIR JSON structure (comprehensive)
│   │       ├── dax-patterns.md          # DAX best practices
│   │       ├── dax-time-intelligence.md # Time intel patterns
│   │       ├── calculation-groups.md    # Calc group syntax
│   │       ├── rls-patterns.md          # Row-level security
│   │       ├── m-query-basics.md        # Power Query in PBIP
│   │       ├── troubleshooting.md       # Common errors and solutions
│   │       │
│   │       └── pbir-templates/          # Visual JSON templates
│   │           ├── clusteredColumnChart.json
│   │           ├── lineChart.json
│   │           ├── card.json
│   │           ├── tableEx.json
│   │           ├── slicer.json
│   │           └── pieChart.json
│   │
│   └── pbi-test/
│       ├── SKILL.md
│       └── references/
│           └── testing-guide.md         # How to verify features work
│
├── commands/
│   ├── pbi.md                           # /pbi command
│   └── pbi-test.md                      # /pbi:test command
│
└── mcp-config-example.json              # Example MCP configuration
```

---

## Skill Definitions

### pbi-dev (SKILL.md)

```yaml
---
name: pbi-dev
description: >
  Power BI development assistance for semantic models and reports.
  Triggers on "Power BI", "DAX measure", "TMDL", "PBIR", "semantic model",
  "Power Query", "calculation group", "RLS", "row-level security".
auto_trigger: true
---

# Power BI Development

This skill provides guidance and references for Power BI development using PBIP format.

## Capabilities

- **Semantic Model (TMDL)**: Tables, measures, relationships, calculation groups
- **Report Layout (PBIR)**: Pages, visuals, filters, themes
- **DAX**: Measures, calculated columns, query execution
- **Power Query (M)**: Data source expressions in .pq files
- **Security**: Row-level security roles and filters

## MCP Integration

This skill works with the Microsoft Power BI MCP for:
- Executing DAX queries against live models
- Creating and modifying measures
- Importing/exporting TMDL folders

## References

Load references as needed:
- `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/tmdl-syntax.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/dax-patterns.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/pbir-schema.md`
```

### pbi-test (SKILL.md)

```yaml
---
name: pbi-test
description: >
  Verify that newly developed Power BI features work as expected.
  Triggers on "test measure", "verify calculation", "check visual",
  "does this work", "test relationship", "validate DAX".
auto_trigger: true
---

# Power BI Feature Testing

This skill helps verify that newly developed features work as the user expects.

## What It Tests

- **Measures**: Do they return the expected values?
- **Calculated columns**: Are calculations correct?
- **Relationships**: Does filtering propagate correctly?
- **Visuals**: Do they display the right data?
- **Filters/Slicers**: Do interactions work as intended?

## Verification Methods

### 1. DAX Query Execution
Use MCP to execute DAX queries and verify measure results:
```dax
EVALUATE
ROW(
    "Total Sales", [Total Sales],
    "YoY Growth", [YoY Growth]
)
```

### 2. Visual Inspection
Use computer use to:
- Screenshot the visual showing the new feature
- Read values displayed in cards, charts, tables
- Confirm the visual renders without errors

### 3. Filter Testing
Verify relationships work by:
- Clicking slicer values
- Checking that related visuals update
- Comparing DAX results with/without filters

### 4. Cross-Validation
Compare multiple sources:
- DAX query result vs visual display
- Filtered vs unfiltered totals
- Different time periods

## Example Workflow

User: "I added a YoY Growth measure, does it work?"

Claude:
1. Uses MCP to execute DAX query for the measure
2. Uses computer use to find a visual showing YoY Growth
3. Compares the DAX result with the displayed value
4. Tests with different filter contexts
5. Reports whether the measure works correctly
```

---

## Workflow Examples

### Example 1: Add a Measure

```
User: "Add a YoY Growth measure to the Sales table"

Claude:
1. Uses Power BI MCP to connect to the open Desktop instance
2. Uses MCP list_measures to see existing measures
3. Uses MCP create_measure with DAX:

   YoY Growth =
   VAR CurrentSales = [Total Sales]
   VAR PriorYearSales = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
   RETURN
   DIVIDE(CurrentSales - PriorYearSales, PriorYearSales)

4. Uses computer use to screenshot the report
5. Visually confirms the measure appears in the field list
6. Reports success
```

### Example 2: Test Filter Interaction

```
User: "Verify the Region slicer filters the Sales chart correctly"

Claude:
1. Uses computer use to screenshot current state
2. Uses computer use to click "West" in Region slicer
3. Waits for visuals to update
4. Uses computer use to screenshot filtered state
5. Uses MCP execute_dax to get filtered total:

   EVALUATE
   SUMMARIZECOLUMNS(
     "Sales", [Total Sales]
   )

6. Compares DAX result with visual chart value
7. Reports pass/fail with evidence
```

### Example 3: Verify a New Relationship Works

```
User: "I added a relationship between Products and Sales. Does it work?"

Claude:
1. Uses MCP to list relationships and confirm the new one exists
2. Uses MCP to execute DAX query with a filter on Products:

   EVALUATE
   CALCULATETABLE(
       SUMMARIZE(Sales, "Total", [Total Sales]),
       Products[Category] = "Electronics"
   )

3. Uses computer use to click "Electronics" in a Product Category slicer
4. Reads the Total Sales value from the visual
5. Compares DAX result with displayed value
6. Reports: "The relationship is working correctly - filtering by
   Electronics shows $X in both the DAX query and the visual."
```

### Example 4: Verify a New Visual Shows Correct Data

```
User: "I added a card visual for Average Order Value. Is it showing the right number?"

Claude:
1. Uses MCP to execute DAX for the expected value:

   EVALUATE
   ROW("AOV", DIVIDE([Total Sales], [Order Count]))

2. Uses computer use to screenshot the report
3. Locates the new card visual and reads the displayed value
4. Compares: "The DAX query returns $127.50 and the card shows $127.50 -
   the visual is displaying the correct value."
```

### Example 5: Edit TMDL Directly

```
User: "Update the Total Sales measure to exclude returns"

Claude:
1. Reads the Sales.tmdl file directly
2. Finds the Total Sales measure definition
3. Updates the DAX expression:

   Total Sales =
   CALCULATE(
       SUMX(Sales, Sales[Quantity] * Sales[UnitPrice]),
       Sales[IsReturn] = FALSE
   )

4. Saves the file
5. Power BI Desktop auto-reloads the model
6. Uses MCP to query the new value and verify it changed
7. Uses computer use to confirm visuals updated
```

---

## Setup Instructions

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Windows | 10/11 | Power BI Desktop is Windows-only |
| Power BI Desktop | Latest | Non-Store version recommended |
| Node.js | 18+ | For MCP servers |
| Claude Code | Latest | With computer use enabled |

### Installation

```bash
# 1. Install Power BI MCP
npm install -g @microsoft/powerbi-modeling-mcp

# 2. Install plugin
/plugin install powerbi-local@liam-machine/laim

# 3. Configure MCP (add to ~/.claude.json or project .mcp.json)
```

Example MCP configuration:
```json
{
  "mcpServers": {
    "powerbi": {
      "command": "npx",
      "args": ["-y", "@microsoft/powerbi-modeling-mcp@latest"]
    }
  }
}
```

### Power BI Desktop Configuration

1. **Enable PBIP format:**
   - File → Options → Preview Features
   - Check "Power BI Project (.pbip) save option"
   - Check "Store semantic model in TMDL format"

2. **Enable enhanced report format (PBIR):**
   - File → Options → Preview Features
   - Check "Store reports using enhanced metadata format (PBIR)"

3. **Save your report as PBIP:**
   - File → Save As → Power BI Project (*.pbip)

---

## File Formats

### PBIP Project Structure

```
MyReport.pbip                    # Project pointer file
├── MyReport.Report/
│   ├── definition/
│   │   ├── report.json          # Report metadata
│   │   └── pages/
│   │       ├── page1.json       # Page definition (PBIR)
│   │       └── page2.json
│   └── StaticResources/
│       └── images/              # Embedded images
│
└── MyReport.SemanticModel/
    └── definition/
        ├── model.tmdl           # Model metadata
        ├── tables/
        │   ├── Sales.tmdl       # Table + measures
        │   └── Date.tmdl
        ├── relationships.tmdl   # Relationship definitions
        └── expressions.tmdl     # M/Power Query expressions
```

### TMDL Example

```tmdl
table Sales
    lineageTag: abc123-def456

    column ProductID
        dataType: int64
        sourceColumn: ProductID
        lineageTag: col-123

    column Amount
        dataType: decimal
        sourceColumn: Amount
        lineageTag: col-456

    measure 'Total Sales' = SUM(Sales[Amount])
        formatString: "$#,##0"
        displayFolder: "Revenue"

    measure 'YoY Growth' =
        VAR CurrentSales = [Total Sales]
        VAR PriorYear = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
        RETURN DIVIDE(CurrentSales - PriorYear, PriorYear)
        formatString: "0.0%"
        displayFolder: "Growth"
```

---

## Limitations

| Limitation | Reason | Notes |
|------------|--------|-------|
| Windows only | Power BI Desktop is Windows-only | Use VM if on macOS/Linux |
| PBIR is preview | GA expected Q3 2026 | Recommended for new projects |
| Desktop must be open | MCP connects to running instance | Or use TMDL-only mode |

---

## Known Limitations & Warnings

> **Important:** The Microsoft Power BI Modeling MCP is currently in **Public Preview**. Implementation may significantly change prior to GA. Review all generated code before use.

### MCP Server Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Public Preview Status** | APIs may change, features may be unstable | Pin to specific version, test thoroughly |
| **Report Layer Blindness** | MCP cannot modify reports, only semantic models | Use PBIR JSON editing for visuals |
| **Rename Operations Break Reports** | Using batch_rename_tables/columns breaks visual field references | Avoid renames on models with reports, or manually update PBIR |
| **No Mac ARM/Silicon Support** | Cannot run natively on Apple Silicon | Use Parallels, VMware Fusion, or Windows 365 |
| **Authentication Issues** | Fabric workspace connectivity has known AADSTS errors | Check GitHub issues for workarounds |

### DAX Quality Considerations

| Consideration | Details |
|---------------|---------|
| **Human Review Required** | All generated DAX should be validated by a human before production use |
| **Complex DAX Unreliable** | Filter propagation, context transitions, and advanced patterns may have subtle errors |
| **Time Intelligence Assumptions** | Generated time intelligence assumes properly configured date tables |
| **Performance Not Guaranteed** | Generated DAX may not be optimized; review with DAX Studio |

### PBIR Visual Creation Limitations

| Limitation | Details |
|------------|---------|
| **No MCP Tools for Reports** | Visuals must be created via direct JSON file editing |
| **Schema Complexity** | PBIR visual.json has complex, partially-documented schema |
| **No Live Feedback** | Changes require Power BI Desktop refresh to see results |
| **Template Approach Recommended** | Generate visuals by cloning templates, not from scratch |

### Known GitHub Issues (as of January 2026)

| Category | Issue Examples |
|----------|----------------|
| Authentication | Token generation failures, AADSTS500113 errors with Fabric |
| Platform | No Mac ARM support, admin rights required on some systems |
| Connection | Chinese character filename failures, SSAS parsing issues |
| Integration | Tools not visible in some clients, MCP discovery issues |

### Best Practices

1. **Always back up** your PBIP folder before making MCP-driven changes
2. **Never use batch rename** operations on models with existing reports
3. **Review all generated DAX** - treat it as a starting point, not final code
4. **Use version control** - PBIP format is Git-friendly, commit frequently
5. **Test incrementally** - verify each change before making the next
6. **Use TMDL-only mode** for semantic model work when possible (more stable)

---

## References

### Official Microsoft Resources
- [Power BI Modeling MCP](https://github.com/microsoft/powerbi-modeling-mcp)
- [Power BI Desktop Projects (PBIP)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [TMDL Overview](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview)
- [PBIR Enhanced Report Format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)

### Community Resources
- [Tabular Editor MCP Integration](https://tabulareditor.com/blog/ai-agents-that-work-with-power-bi-semantic-model-mcp-servers)
- [Power BI MCP Setup Guide](https://medium.com/@michael.hannecke/power-bi-modeling-mcp-server-step-by-step-implementation-guide-b7209d6d2506)
- [SQLBI DAX Patterns](https://www.daxpatterns.com/)

### Claude Code
- [Claude Computer Use](https://docs.anthropic.com/en/docs/build-with-claude/computer-use)
- [MCP Protocol](https://modelcontextprotocol.io/)
