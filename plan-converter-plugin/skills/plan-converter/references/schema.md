# features.json Schema Reference

## ID Numbering Convention

Phases use 100-based ID spacing to allow inserting new features without renumbering:

| Phase | ID Range | Example |
|-------|----------|---------|
| Phase 0 (if exists) | F001–F099 | F001, F002, ... F015 |
| Phase 1 | F100–F199 | F100, F101, ... F112 |
| Phase 2 | F200–F299 | F200, F201, ... F208 |
| Phase 3 | F300–F399 | F300, F301, ... |
| Phase N | F{N*100}–F{N*100+99} | ... |

Within a phase, IDs increment by 1 from the phase base. New features inserted later use the next available ID in the range.

**Exception:** If the plan has no explicit phases or only a single phase, use sequential IDs starting at F001.

## Complete Schema

```json
{
  "project": {
    "name": "string (from plan title)",
    "description": "string (from plan overview/vision)",
    "version": "string (default '0.1.0')",
    "platform": "string ('web' | 'ios' | 'android' | 'cross-platform' | 'cli' | 'api')",
    "tech_stack": {
      "key": "value pairs extracted from plan"
    }
  },
  "phases": [
    {
      "id": "phase-N",
      "name": "string",
      "description": "string",
      "order": "number (1-based)",
      "status": "pending"
    }
  ],
  "features": [
    {
      "id": "FXXX",
      "name": "string (concise feature name)",
      "description": "string (what to build, with enough detail for feature-dev agent)",
      "phase": "phase-N",
      "status": "pending | in_progress | completed | skipped",
      "skip": false,
      "dependencies": ["FXXX"],
      "validation_criteria": [
        "string (specific, testable criterion)",
        "Verify in Chrome: navigate to /page and confirm ...",
        "Verify in iOS Simulator: launch app and confirm ..."
      ],
      "implementation_notes": "string (relevant comments, constraints, or guidance from the plan)",
      "category": "string (infrastructure | ui | database | api | auth | testing | deployment | etc.)",
      "estimated_effort": "small | medium | large"
    }
  ],
  "metadata": {
    "generated_from": "plan.md",
    "generated_at": "ISO date string",
    "feature_counts": {
      "total": "number",
      "by_phase": {
        "phase-N": "number"
      }
    }
  }
}
```

## Field Details

### Feature Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique ID following phase-based numbering (F001, F100, etc.) |
| `name` | Yes | Short, descriptive name (imperative form: "Set up X", "Create Y") |
| `description` | Yes | What to build. Include enough context for the feature-dev agent to implement without re-reading the plan. |
| `phase` | Yes | References a phase ID |
| `status` | Yes | Always `"pending"` for new conversions (unless plan marks feature as done) |
| `skip` | Yes | `false` by default. Set to `true` for features explicitly marked as optional/deferred in the plan. |
| `dependencies` | Yes | Array of feature IDs that must complete first. Empty array `[]` if none. |
| `validation_criteria` | Yes | Array of specific, testable criteria. Include platform-appropriate testing instructions. |
| `implementation_notes` | Yes | Relevant comments, constraints, architecture notes, or business rules from the plan. Empty string `""` if none. |
| `category` | No | Feature category for grouping |
| `estimated_effort` | No | Rough size estimate |

### Validation Criteria: Platform-Specific Patterns

**Web apps** (React, Next.js, Vue, etc.):
```json
[
  "Verify in Chrome: navigate to http://localhost:3000/page and confirm element renders",
  "Verify in Chrome: submit form and confirm success message appears",
  "Verify in Chrome: check browser console has no errors"
]
```

**iOS apps** (Swift, SwiftUI):
```json
[
  "Verify in iOS Simulator: launch app and confirm screen loads",
  "Verify in iOS Simulator: tap button and confirm navigation works",
  "App builds without errors in Xcode"
]
```

**Android apps** (Kotlin, Jetpack Compose):
```json
[
  "Verify in Android Emulator: launch app and confirm activity loads",
  "Verify in Android Emulator: tap button and confirm navigation works",
  "App builds without errors in Android Studio"
]
```

**API / CLI / backend** (no UI):
```json
[
  "Run command and verify expected output",
  "API endpoint returns 200 with expected payload",
  "Database migration applies without errors"
]
```

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not started (default for new features) |
| `in_progress` | Currently being implemented |
| `completed` | Done and validated |
| `skipped` | Intentionally skipped (set when `skip: true` and feature is bypassed) |

### Skip Field

- `false` (default): Feature is in the roadmap and will be implemented
- `true`: Feature is deferred, optional, or out-of-scope. The `/next-feature` command will skip these.

Use `skip: true` when the plan marks something as:
- "Nice to have" / "Stretch goal"
- "Future work" / "Post-MVP"
- "Optional" / "If time permits"
- Explicitly deferred to a later version
