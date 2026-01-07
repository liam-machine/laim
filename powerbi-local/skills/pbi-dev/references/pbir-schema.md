# PBIR (Power BI Enhanced Report Format) Schema Reference

This document provides comprehensive schema documentation for the Power BI Enhanced Report Format (PBIR) used in Power BI Desktop Developer Mode. PBIR stores report metadata as properly formatted JSON files, enabling source control, AI-assisted report generation, and programmatic report manipulation.

## Table of Contents

1. [PBIR Folder Structure](#1-pbir-folder-structure)
2. [Visual JSON Structure](#2-visual-json-structure)
3. [Visual Types Reference](#3-visual-types-reference)
4. [Query State Structure](#4-query-state-structure)
5. [Field Reference Patterns](#5-field-reference-patterns)
6. [Common Objects Section](#6-common-objects-section)
7. [Best Practices for AI Generation](#7-best-practices-for-ai-generation)

---

## 1. PBIR Folder Structure

When saving a Power BI Project (PBIP) with the PBIR format enabled, the report metadata is organized into a hierarchical folder structure with separate files for each component.

### Complete Directory Structure

```
ProjectName/
├── ProjectName.pbip                    # Project entry point
├── ProjectName.SemanticModel/          # Data model folder
│   ├── .pbi/
│   │   ├── localSettings.json
│   │   └── cache.abf
│   ├── definition/
│   │   ├── tables/
│   │   ├── relationships/
│   │   ├── roles/
│   │   └── cultures/
│   ├── definition.pbism
│   ├── diagramLayout.json
│   └── .platform
└── ProjectName.Report/                 # Report folder
    ├── .pbi/
    │   └── localSettings.json
    ├── definition/                     # PBIR report definition
    │   ├── report.json                 # Report-level settings
    │   ├── version.json                # PBIR version metadata
    │   ├── reportExtensions.json       # Report extensions (optional)
    │   ├── pages/
    │   │   ├── pages.json              # Page order and active page
    │   │   └── [pageName]/
    │   │       ├── page.json           # Page-level settings
    │   │       └── visuals/
    │   │           └── [visualName]/
    │   │               ├── visual.json  # Visual configuration
    │   │               └── mobile.json  # Mobile layout (optional)
    │   └── bookmarks/
    │       ├── bookmarks.json          # Bookmark metadata
    │       └── [bookmarkName].bookmark.json
    ├── definition.pbir                 # PBIR entry point
    ├── .platform
    └── StaticResources/                # Images and static files
```

### File Descriptions

| File | Required | Description |
|------|----------|-------------|
| `report.json` | Yes | Report metadata: filters, theme, annotations |
| `version.json` | Yes | PBIR version; determines required files |
| `pages/pages.json` | No | Page order and active page |
| `pages/[name]/page.json` | Yes | Page dimensions, filters, background |
| `pages/[name]/visuals/[name]/visual.json` | Yes | Visual type, position, query, formatting |
| `pages/[name]/visuals/[name]/mobile.json` | No | Mobile-specific layout overrides |
| `bookmarks/bookmarks.json` | No | Bookmark groups and order |
| `bookmarks/[name].bookmark.json` | No | Bookmark state and targets |
| `reportExtensions.json` | No | Report-level measures and extensions |

### Naming Convention

By default, pages, visuals, and bookmarks use a **20-character alphanumeric identifier** as their folder/file name:
- Example: `90c2e07d8e84e7d5c026`
- Can be renamed but must contain only: letters, digits, underscores, or hyphens
- Renaming may break external references

### JSON Schema References

All PBIR files include a `$schema` property pointing to Microsoft's public JSON schemas:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json"
}
```

Schema URLs by file type:
- **report.json**: `.../report/1.0.0/schema.json`
- **page.json**: `.../page/1.0.0/schema.json`
- **visual.json**: `.../visualContainer/2.4.0/schema.json`
- **version.json**: `.../versionMetadata/1.0.0/schema.json`

GitHub repository: https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition

---

## 2. Visual JSON Structure

Each visual is stored in its own folder with a `visual.json` file containing the complete visual configuration.

### Core Visual Container Schema

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
  "name": "a1b2c3d4e5f6g7h8i9j0",
  "position": {
    "x": 100,
    "y": 50,
    "z": 1000,
    "width": 400,
    "height": 300,
    "tabOrder": 1
  },
  "visual": {
    "visualType": "clusteredColumnChart",
    "query": {
      "queryState": { ... },
      "sortDefinition": { ... }
    },
    "objects": { ... },
    "drillFilterOtherVisuals": true
  },
  "filterConfig": { ... },
  "isHidden": false,
  "annotations": []
}
```

### Position Object

The `position` object defines the visual's placement on the canvas:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `x` | number | Yes | Horizontal position (left edge) in pixels |
| `y` | number | Yes | Vertical position (top edge) in pixels |
| `width` | number | Yes | Visual width in pixels |
| `height` | number | Yes | Visual height in pixels |
| `z` | number | Yes | Z-index for layering (higher = on top) |
| `tabOrder` | number | No | Keyboard navigation sequence |
| `angle` | number | No | Rotation angle in degrees |

**Standard canvas size**: 1280 x 720 pixels (default)

### Visual Object Structure

The `visual` property contains the visualization configuration:

```json
{
  "visual": {
    "visualType": "clusteredColumnChart",
    "query": {
      "queryState": {
        "Category": { "projections": [...] },
        "Y": { "projections": [...] },
        "Series": { "projections": [...] }
      },
      "sortDefinition": {
        "sort": [...]
      }
    },
    "objects": {
      "categoryAxis": [{ "properties": {...} }],
      "valueAxis": [{ "properties": {...} }],
      "legend": [{ "properties": {...} }],
      "title": [{ "properties": {...} }]
    },
    "drillFilterOtherVisuals": true,
    "vcObjects": { ... }
  }
}
```

### Top-Level Visual Container Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `$schema` | string | Yes | JSON schema URL |
| `name` | string | Yes | Unique identifier (max 50 chars) |
| `position` | object | Yes | Position and dimensions |
| `visual` | object | Yes* | Visual configuration |
| `visualGroup` | object | Yes* | Group container (mutually exclusive with `visual`) |
| `parentGroupName` | string | No | Parent group identifier |
| `filterConfig` | object | No | Visual-level filters |
| `isHidden` | boolean | No | Visibility flag |
| `annotations` | array | No | Custom metadata key-value pairs |
| `howCreated` | string | No | Creation source (Copilot, drag-drop, etc.) |

*Either `visual` or `visualGroup` must be present, but not both.

---

## 3. Visual Types Reference

### Chart Visuals

| visualType | Display Name | Data Roles |
|------------|--------------|------------|
| `clusteredColumnChart` | Clustered Column Chart | Category, Y, Series, Tooltips |
| `clusteredBarChart` | Clustered Bar Chart | Category, Y, Series, Tooltips |
| `stackedColumnChart` | Stacked Column Chart | Category, Y, Series, Tooltips |
| `stackedBarChart` | Stacked Bar Chart | Category, Y, Series, Tooltips |
| `hundredPercentStackedColumnChart` | 100% Stacked Column | Category, Y, Series |
| `hundredPercentStackedBarChart` | 100% Stacked Bar | Category, Y, Series |
| `lineChart` | Line Chart | Category, Y, Series, Tooltips |
| `areaChart` | Area Chart | Category, Y, Series, Tooltips |
| `stackedAreaChart` | Stacked Area Chart | Category, Y, Series |
| `lineClusteredColumnComboChart` | Line and Clustered Column | Category, Y, Y2, Series |
| `lineStackedColumnComboChart` | Line and Stacked Column | Category, Y, Y2, Series |
| `ribbonChart` | Ribbon Chart | Category, Y, Series |
| `waterfallChart` | Waterfall Chart | Category, Y, Breakdown |

### Card and KPI Visuals

| visualType | Display Name | Data Roles |
|------------|--------------|------------|
| `card` | Card | Values |
| `cardVisual` | New Card | Values, Data |
| `multiRowCard` | Multi-row Card | Values |
| `kpi` | KPI | Indicator, Trend, Goals |
| `gauge` | Gauge | Value, Minimum, Maximum, Target |

### Table and Matrix Visuals

| visualType | Display Name | Data Roles |
|------------|--------------|------------|
| `tableEx` | Table | Values |
| `matrix` | Matrix | Rows, Columns, Values |
| `pivotTable` | Pivot Table | Rows, Columns, Values |

### Slicer Visuals

| visualType | Display Name | Data Roles |
|------------|--------------|------------|
| `slicer` | Slicer | Values |
| `advancedSlicerVisual` | Advanced Slicer | Values |

### Pie and Donut Visuals

| visualType | Display Name | Data Roles |
|------------|--------------|------------|
| `pieChart` | Pie Chart | Category, Y, Tooltips |
| `donutChart` | Donut Chart | Category, Y, Tooltips |
| `funnel` | Funnel | Category, Y, Tooltips |
| `treemap` | Treemap | Group, Details, Values |

### Map Visuals

| visualType | Display Name | Data Roles |
|------------|--------------|------------|
| `map` | Map (Bing) | Location, Legend, Size, Tooltips |
| `filledMap` | Filled Map | Location, Legend, Tooltips |
| `azureMap` | Azure Map | Location, Size, Color, Tooltips |
| `shapeMap` | Shape Map | Location, Color |

### Scatter and Bubble Visuals

| visualType | Display Name | Data Roles |
|------------|--------------|------------|
| `scatterChart` | Scatter Chart | X, Y, Size, Legend, Details |

### Other Visuals

| visualType | Display Name | Description |
|------------|--------------|-------------|
| `textbox` | Text Box | Rich text content |
| `image` | Image | Static image from URL |
| `basicShape` | Basic Shape | Rectangle, oval, line, etc. |
| `shape` | Shape | Advanced shapes |
| `actionButton` | Button | Navigation and action button |
| `bookmarkNavigator` | Bookmark Navigator | Bookmark selection buttons |
| `pageNavigator` | Page Navigator | Page navigation tabs |
| `aiNarratives` | Smart Narrative | AI-generated text insights |
| `qnaVisual` | Q&A | Natural language query |
| `decompositionTreeVisual` | Decomposition Tree | AI decomposition analysis |
| `keyDriversVisual` | Key Influencers | Key driver analysis |
| `scriptVisual` | R Visual | R script visualization |
| `pythonVisual` | Python Visual | Python script visualization |

---

## 4. Query State Structure

The `queryState` object defines how data fields are bound to the visual's data roles.

### QueryState Object

```json
{
  "queryState": {
    "Category": {
      "projections": [
        {
          "field": { ... },
          "queryRef": "Sales.ProductCategory",
          "nativeQueryRef": "ProductCategory",
          "displayName": "Product Category"
        }
      ]
    },
    "Y": {
      "projections": [
        {
          "field": { ... },
          "queryRef": "Sales.TotalRevenue",
          "nativeQueryRef": "TotalRevenue"
        }
      ]
    },
    "Series": {
      "projections": [...]
    }
  }
}
```

### Data Role Names by Visual Type

| Visual Type | Data Roles |
|-------------|------------|
| Column/Bar Charts | Category, Y, Series, Tooltips |
| Line Charts | Category, Y, Series, Tooltips |
| Combo Charts | Category, Y, Y2, Series, Tooltips |
| Table | Values (multiple columns) |
| Matrix | Rows, Columns, Values |
| Card | Values |
| Multi-row Card | Values |
| Slicer | Values |
| Pie/Donut | Category, Y, Tooltips |
| Map | Location, Legend, Size, Tooltips |
| Scatter | X, Y, Size, Legend, Details |
| Gauge | Value, Minimum, Maximum, Target |
| KPI | Indicator, Trend, Goals |

### Projection Object Structure

Each projection in the `projections` array represents a field binding:

```json
{
  "field": {
    "Column": {
      "Expression": {
        "SourceRef": { "Entity": "TableName" }
      },
      "Property": "ColumnName"
    }
  },
  "queryRef": "TableName.ColumnName",
  "nativeQueryRef": "ColumnName",
  "displayName": "Custom Display Name",
  "active": true
}
```

| Property | Type | Description |
|----------|------|-------------|
| `field` | object | Field reference (Column, Measure, or Aggregation) |
| `queryRef` | string | Full qualified reference `Table.Field` |
| `nativeQueryRef` | string | Field name used in native queries |
| `displayName` | string | Custom label (null uses field name) |
| `active` | boolean | Whether the field is active |

---

## 5. Field Reference Patterns

### Referencing a Column

```json
{
  "field": {
    "Column": {
      "Expression": {
        "SourceRef": {
          "Entity": "Sales"
        }
      },
      "Property": "ProductName"
    }
  },
  "queryRef": "Sales.ProductName"
}
```

### Referencing a Measure

```json
{
  "field": {
    "Measure": {
      "Expression": {
        "SourceRef": {
          "Entity": "Sales"
        }
      },
      "Property": "Total Revenue"
    }
  },
  "queryRef": "Sales.Total Revenue"
}
```

### Referencing an Aggregated Column

For applying aggregations (Sum, Count, Average, etc.) to columns:

```json
{
  "field": {
    "Aggregation": {
      "Expression": {
        "Column": {
          "Expression": {
            "SourceRef": {
              "Entity": "Sales"
            }
          },
          "Property": "Amount"
        }
      },
      "Function": 0
    }
  },
  "queryRef": "Sum(Sales.Amount)"
}
```

### Aggregation Function Codes

| Function Code | Aggregation |
|---------------|-------------|
| 0 | Sum |
| 1 | Average |
| 2 | Count |
| 3 | Min |
| 4 | Max |
| 5 | CountNonNull |
| 6 | Median |
| 7 | StandardDeviation |
| 8 | Variance |

### Complete Field Reference Examples

**Column with display name override:**
```json
{
  "field": {
    "Column": {
      "Expression": {
        "SourceRef": { "Entity": "Products" }
      },
      "Property": "CategoryName"
    }
  },
  "queryRef": "Products.CategoryName",
  "nativeQueryRef": "CategoryName",
  "displayName": "Product Category"
}
```

**Measure without display name (uses measure name):**
```json
{
  "field": {
    "Measure": {
      "Expression": {
        "SourceRef": { "Entity": "Metrics" }
      },
      "Property": "YTD Sales"
    }
  },
  "queryRef": "Metrics.YTD Sales",
  "nativeQueryRef": "YTD Sales",
  "displayName": null
}
```

**Count aggregation on column:**
```json
{
  "field": {
    "Aggregation": {
      "Expression": {
        "Column": {
          "Expression": {
            "SourceRef": { "Entity": "Orders" }
          },
          "Property": "OrderID"
        }
      },
      "Function": 2
    }
  },
  "queryRef": "Count(Orders.OrderID)"
}
```

---

## 6. Common Objects Section

The `objects` property in a visual contains formatting and configuration settings.

### Object Structure Pattern

```json
{
  "objects": {
    "objectName": [
      {
        "properties": {
          "propertyName": {
            "expr": {
              "Literal": { "Value": "value" }
            }
          }
        },
        "selector": { ... }
      }
    ]
  }
}
```

### Title Object

```json
{
  "title": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "text": { "expr": { "Literal": { "Value": "'Sales by Region'" } } },
        "fontColor": { "solid": { "color": "#252423" } },
        "fontSize": { "expr": { "Literal": { "Value": "14D" } } },
        "fontFamily": { "expr": { "Literal": { "Value": "'Segoe UI'" } } },
        "bold": { "expr": { "Literal": { "Value": "true" } } },
        "italic": { "expr": { "Literal": { "Value": "false" } } },
        "alignment": { "expr": { "Literal": { "Value": "'center'" } } }
      }
    }
  ]
}
```

### Subtitle Object

```json
{
  "subtitle": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "text": { "expr": { "Literal": { "Value": "'FY2024 Q4'" } } },
        "fontColor": { "solid": { "color": "#605E5C" } },
        "fontSize": { "expr": { "Literal": { "Value": "10D" } } }
      }
    }
  ]
}
```

### Background Object

```json
{
  "background": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "color": { "solid": { "color": "#FFFFFF" } },
        "transparency": { "expr": { "Literal": { "Value": "0D" } } }
      }
    }
  ]
}
```

### Border Object

```json
{
  "border": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "color": { "solid": { "color": "#E6E6E6" } },
        "radius": { "expr": { "Literal": { "Value": "5D" } } }
      }
    }
  ]
}
```

### Legend Object

```json
{
  "legend": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "position": { "expr": { "Literal": { "Value": "'Right'" } } },
        "showTitle": { "expr": { "Literal": { "Value": "true" } } },
        "titleText": { "expr": { "Literal": { "Value": "'Categories'" } } },
        "fontColor": { "solid": { "color": "#252423" } },
        "fontSize": { "expr": { "Literal": { "Value": "9D" } } }
      }
    }
  ]
}
```

Legend position values: `'Top'`, `'Bottom'`, `'Left'`, `'Right'`, `'TopCenter'`, `'BottomCenter'`, `'LeftCenter'`, `'RightCenter'`

### Category Axis Object

```json
{
  "categoryAxis": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "showAxisTitle": { "expr": { "Literal": { "Value": "true" } } },
        "titleText": { "expr": { "Literal": { "Value": "'Month'" } } },
        "titleColor": { "solid": { "color": "#252423" } },
        "titleFontSize": { "expr": { "Literal": { "Value": "11D" } } },
        "labelColor": { "solid": { "color": "#252423" } },
        "fontSize": { "expr": { "Literal": { "Value": "9D" } } },
        "labelDisplayUnits": { "expr": { "Literal": { "Value": "0D" } } }
      }
    }
  ]
}
```

### Value Axis Object

```json
{
  "valueAxis": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "showAxisTitle": { "expr": { "Literal": { "Value": "true" } } },
        "titleText": { "expr": { "Literal": { "Value": "'Revenue ($)'" } } },
        "titleColor": { "solid": { "color": "#252423" } },
        "titleFontSize": { "expr": { "Literal": { "Value": "11D" } } },
        "labelColor": { "solid": { "color": "#252423" } },
        "fontSize": { "expr": { "Literal": { "Value": "9D" } } },
        "labelDisplayUnits": { "expr": { "Literal": { "Value": "1000D" } } },
        "gridlineShow": { "expr": { "Literal": { "Value": "true" } } },
        "gridlineColor": { "solid": { "color": "#E6E6E6" } },
        "gridlineStyle": { "expr": { "Literal": { "Value": "'dashed'" } } }
      }
    }
  ]
}
```

Display units: `0D` (Auto), `1D` (None), `1000D` (Thousands), `1000000D` (Millions), `1000000000D` (Billions)

### Data Labels Object

```json
{
  "dataLabels": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "color": { "solid": { "color": "#252423" } },
        "fontSize": { "expr": { "Literal": { "Value": "9D" } } },
        "labelDisplayUnits": { "expr": { "Literal": { "Value": "1000D" } } },
        "labelPrecision": { "expr": { "Literal": { "Value": "1D" } } },
        "position": { "expr": { "Literal": { "Value": "'outsideEnd'" } } }
      }
    }
  ]
}
```

Data label positions: `'auto'`, `'outsideEnd'`, `'insideEnd'`, `'insideBase'`, `'insideCenter'`

### Data Colors Object

```json
{
  "dataPoint": [
    {
      "properties": {
        "fill": { "solid": { "color": "#118DFF" } }
      }
    }
  ]
}
```

For series-specific colors, use a selector:

```json
{
  "dataPoint": [
    {
      "properties": {
        "fill": { "solid": { "color": "#118DFF" } }
      },
      "selector": {
        "data": [
          {
            "dataViewWildcard": {
              "matchingOption": 1
            }
          }
        ]
      }
    }
  ]
}
```

### Common Object Names by Visual Type

| Object Name | Applies To | Description |
|-------------|------------|-------------|
| `title` | All visuals | Visual title configuration |
| `subtitle` | All visuals | Subtitle below title |
| `background` | All visuals | Background color and transparency |
| `border` | All visuals | Border appearance |
| `visualHeader` | All visuals | Header icons and tooltips |
| `general` | All visuals | General properties |
| `categoryAxis` | Charts | X-axis (category axis) |
| `valueAxis` | Charts | Y-axis (value axis) |
| `legend` | Charts | Legend configuration |
| `dataLabels` | Charts | Data point labels |
| `dataPoint` | Charts | Data point colors |
| `plotArea` | Charts | Plot area background |
| `gridlines` | Tables/Matrix | Table gridlines |
| `columnHeaders` | Tables/Matrix | Column header formatting |
| `rowHeaders` | Matrix | Row header formatting |
| `values` | Tables/Matrix | Cell value formatting |
| `total` | Tables/Matrix | Total row formatting |
| `slicerHeader` | Slicer | Slicer header |
| `items` | Slicer | Slicer items list |
| `calloutValue` | Card | Main value display |

---

## 7. Best Practices for AI Generation

### Visual Name Generation

Always generate unique 20-character alphanumeric visual names:

```python
import random
import string

def generate_visual_name():
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(20))

# Example: "a7b3c9d2e4f1g6h8i0j5"
```

### Validation Before Creation

Before creating a visual, validate:

1. **Table/Entity exists** in the semantic model
2. **Column/Measure exists** in the referenced table
3. **Data types are compatible** with the visual type
4. **Required data roles are filled** for the visual type

### Template-Based Generation

Use templates rather than generating from scratch. Start with a known-working visual configuration and modify:

```python
# Base template for clustered column chart
column_chart_template = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
    "name": "",  # Generate unique name
    "position": {"x": 0, "y": 0, "z": 1000, "width": 400, "height": 300},
    "visual": {
        "visualType": "clusteredColumnChart",
        "query": {
            "queryState": {
                "Category": {"projections": []},
                "Y": {"projections": []}
            }
        },
        "objects": {},
        "drillFilterOtherVisuals": True
    }
}
```

### Common Pitfalls to Avoid

1. **Invalid field references**: Always verify Entity and Property names exist
2. **Missing required properties**: Ensure `$schema`, `name`, and `position` are present
3. **Duplicate visual names**: Each visual must have a unique name on the page
4. **Invalid visualType strings**: Use exact internal names (case-sensitive)
5. **Incorrect data role names**: Use the correct role name for each visual type
6. **Missing queryRef**: Always include `queryRef` with projections

### Z-Index Management

Manage visual layering properly:

- Default visuals: z = 0-1000
- Slicers and filters: z = 1000-2000
- Overlays and popups: z = 2000+
- Text boxes and shapes: z = 3000+

### Testing After Creation

After generating visuals programmatically:

1. Open the report in Power BI Desktop to validate JSON parsing
2. Check for schema validation errors in the output pane
3. Verify data bindings render correctly
4. Test interactions (cross-filtering, drillthrough)
5. Use Computer Use or screenshots to visually verify layout

### PBIR Size Limitations

Be aware of these limits:

| Limit | Maximum |
|-------|---------|
| Pages per report | 1,000 |
| Visuals per page | 1,000 |
| Resource package files | 1,000 |
| Total resource file size | 300 MB |
| Total report file size | 300 MB |

### Example: Complete Clustered Column Chart

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
  "name": "k9m2p4q6r8s0t1u3v5w7",
  "position": {
    "x": 50,
    "y": 50,
    "z": 1000,
    "width": 500,
    "height": 350,
    "tabOrder": 1
  },
  "visual": {
    "visualType": "clusteredColumnChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": {
                    "SourceRef": { "Entity": "Sales" }
                  },
                  "Property": "Region"
                }
              },
              "queryRef": "Sales.Region",
              "nativeQueryRef": "Region"
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": { "Entity": "Sales" }
                  },
                  "Property": "Total Revenue"
                }
              },
              "queryRef": "Sales.Total Revenue",
              "nativeQueryRef": "Total Revenue"
            }
          ]
        }
      }
    },
    "objects": {
      "title": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "text": { "expr": { "Literal": { "Value": "'Revenue by Region'" } } }
          }
        }
      ],
      "categoryAxis": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } }
          }
        }
      ],
      "valueAxis": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "labelDisplayUnits": { "expr": { "Literal": { "Value": "1000D" } } }
          }
        }
      ],
      "dataLabels": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "false" } } }
          }
        }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

---

## References

- [Microsoft PBIR Documentation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- [PBIR Schema GitHub Repository](https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition)
- [Power BI Embedded Visual API](https://learn.microsoft.com/en-us/javascript/api/overview/powerbi/create-add-visual)
- [Power BI Theme JSON Schema](https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema)
- [Power BI Visual Scanner API](https://learn.microsoft.com/en-us/power-bi/developer/visuals/scanner-api)
- [Tabular Editor PBIR Scripting](https://tabulareditor.com/blog/c-scripting-pbir)
