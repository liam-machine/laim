---
description: Power BI development assistance
argument-hint: "[task description]"
skill: pbi-dev
---

# Power BI Development

Develop Power BI semantic models and reports using PBIP format (TMDL + PBIR).

## Capabilities

| Task | Method |
|------|--------|
| Create measures | Edit TMDL files |
| Create visuals | Edit PBIR JSON files |
| Execute DAX | MCP `execute_dax` |
| Validate TMDL | MCP `validate_tmdl` |
| Explore model | MCP `get_tables`, `get_measures` |

## Quick Reference

### Create a Measure

Add to `definition/tables/[TableName].tmdl`:
```tmdl
measure 'Total Sales' = SUM(Sales[Amount])
    formatString: "$#,##0.00"
    displayFolder: Revenue
```

### Create a Visual

1. Create folder: `definition/pages/[page]/visuals/[visualId]/`
2. Add `visual.json` from template
3. Customize field bindings

### Execute DAX Query

Use MCP `execute_dax`:
```dax
EVALUATE ROW("Total Sales", [Total Sales])
```

### Common Operations

| Operation | Command |
|-----------|---------|
| Test measure | `/pbi:test` |
| List tables | MCP `get_tables` |
| List measures | MCP `get_measures` |
| Run DAX | MCP `execute_dax` |

## Reference Documents

- PBIR Schema: `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/pbir-schema.md`
- Troubleshooting: `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/troubleshooting.md`
- Visual Templates: `${CLAUDE_PLUGIN_ROOT}/skills/pbi-dev/references/pbir-templates/`

## Requirements

- Power BI Desktop (MSI version recommended)
- Power BI MCP configured in Claude Code
- PBIP project open in Power BI Desktop
