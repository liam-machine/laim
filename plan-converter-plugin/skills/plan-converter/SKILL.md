---
name: plan-converter
description: >
  Convert plan.md files into structured features.json files for use with the feature-dev agent
  and /next-feature command. Use this skill when the user asks to "convert a plan to features",
  "generate features.json from plan.md", "create a features file from my plan",
  "turn my plan into features", "parse plan.md", or wants to prepare a project plan for
  feature-by-feature development. Also triggers when the user has a plan.md and mentions
  features.json, feature-dev, or /next-feature.
---

# Plan-to-Features Converter

Convert `plan.md` into a `features.json` that the feature-dev agent and `/next-feature` command consume.

## Conversion Workflow

### 1. Read the Plan

Read the `plan.md` file (or whatever planning document the user specifies).

### 2. Detect Platform

Scan the plan for technology/platform keywords to determine validation style:

| Keywords Found | Platform | Validation Prefix |
|---------------|----------|-------------------|
| SwiftUI, UIKit, iOS, Xcode, Swift, CocoaPods, SPM | `ios` | "Verify in iOS Simulator: ..." |
| Kotlin, Jetpack, Android Studio, Gradle, Android | `android` | "Verify in Android Emulator: ..." |
| React, Next.js, Vue, Angular, HTML, CSS, Vite, webpack, Tailwind, browser | `web` | "Verify in Chrome: ..." |
| Flutter, React Native, Expo, Capacitor | `cross-platform` | Both iOS Simulator and Chrome |
| CLI, terminal, argparse, click, API, REST, GraphQL, FastAPI, Express | `api` | "Run command ..." / "API returns ..." |

If multiple platforms detected, use `cross-platform` and include validation for each.

### 3. Extract Structure

From the plan, extract:

- **Project info**: title, description, tech stack
- **Phases**: numbered sections (Phase 0, Phase 1, etc.), milestones, or version targets
- **Features**: checklist items `- [ ]`, bullet points under phase headings, or described capabilities
- **Dependencies**: when one feature references or requires another
- **Notes**: architecture decisions, constraints, business rules relevant to specific features

### 4. Assign IDs

Use 100-based phase spacing:

- Phase 0 features: F001, F002, F003...
- Phase 1 features: F100, F101, F102...
- Phase 2 features: F200, F201, F202...
- Phase N features: F{N×100}, F{N×100+1}...

If the plan has no phases, use sequential IDs starting at F001.

### 5. Generate Validation Criteria

For each feature, write 2-5 specific, testable validation criteria. Follow the platform detection from step 2.

**Rules:**
- Every UI feature MUST have at least one browser/simulator verification step
- Non-UI features (database, config, infrastructure) use build/run verification
- Be specific: name the URL, screen, element, or expected output
- Include error-case validation where relevant (e.g., "Verify form shows error when field is empty")

### 6. Set Skip and Status

- Mark features as `"skip": true` if the plan says "optional", "stretch goal", "future work", "nice to have", or "post-MVP"
- Mark features as `"status": "completed"` if the plan uses `[x]` checkboxes
- All other features: `"status": "pending"`, `"skip": false`

### 7. Populate Implementation Notes

For each feature, include relevant context from the plan:
- Architecture patterns or folder structures mentioned
- Specific libraries or APIs to use
- Business rules or constraints
- References to other documents or specs
- Any comments or caveats the plan author included

Use empty string `""` if no relevant notes exist.

### 8. Write features.json

Write the file to the project root. See `${CLAUDE_PLUGIN_ROOT}/skills/plan-converter/references/schema.md` for the complete schema and ID numbering reference.

### 9. Summary

After writing, output:
- Total features generated and breakdown by phase
- Platform detected
- Number of features marked as skip
- Number of features already completed (from `[x]` checkboxes)
- Any ambiguities or decisions made during conversion

## Key Principles

- **Feature-dev ready**: Each feature description must have enough context for the feature-dev agent to implement without re-reading the plan. Include the "what" and the "why".
- **Atomic features**: Prefer smaller, independently implementable features. Split large plan sections into multiple features if they contain distinct deliverables.
- **Dependency chains**: If Feature B depends on Feature A's output, add the dependency. Avoid circular dependencies.
- **No information loss**: Every actionable item in the plan should map to a feature. Architecture docs, tech stack, and constraints go into `implementation_notes`.
