---
name: ui-brief
description: >
  UI design brief template for CRs with UI impact.
  Captures product surface, brand direction, colors, layout,
  component inventory, screen contracts, and reference log.
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Confirm CR has UI impact (low/medium/high)."
      on_failure: "Skip UI brief for CRs with no UI impact."
  actions:
    - id: ACT-001
      action: "Fill product surface, brand direction, color system, layout, component inventory."
  must_do:
    - id: MUST-001
      action: "Infer from product context — do not ask open-ended style questions."
  must_not_do:
    - id: NEVER-001
      action: "Do not skip this template for CRs with UI impact."
  outputs:
    - id: OUT-001
      path: "ui-brief.md"
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->


# UI Design Brief

**Feature**: [feature name]
**UI Impact**: none | low | medium | high
**Date**: YYYY-MM-DD
**Analyst**: [agent/human]

---

## 1. Product Surface

- Screens/pages affected:
- Primary user journey:
- Secondary/edge journeys:
- Device classes: mobile | tablet | desktop

## 2. Brand Direction

- Brand adjectives: [e.g. "precise, calm, technical"]
- Non-goals: [e.g. "not playful, not SaaS-purple, not generic admin"]
- Reference products/design systems:
- Visual risk: [e.g. "too dense", "too empty", "too consumer"]

## 3. Typography

- Font family:
- Heading scale:
- Body scale:
- Line height / reading density:
- Code/monospace needs:
- Source model: Radix-style type scale

## 4. Color System

- Accent color:
- Neutral/gray family:
- Background/surface hierarchy:
- Semantic colors: success | warning | destructive | info
- Focus ring color:
- Chart palette (if needed):
- Source model: shadcn semantic tokens + Radix 12-step color thinking

## 5. Shape, Spacing, Elevation

- Radius scale:
- Spacing rhythm:
- Shadow/elevation usage:
- Density: compact | normal | spacious

## 6. Layout System

- Navigation pattern: sidebar | top nav | split pane | wizard | dashboard grid
- Content width / container strategy:
- Grid rules:
- Responsive breakpoints:
- Mobile transformation rules:

## 7. Component Inventory

- Required components: [buttons, forms, tables, cards, dialogs, sheets, command menu, charts, empty states]
- Source library choice: shadcn | Radix Themes | Carbon | Fluent | existing app system
- New custom components allowed: yes | no

## 8. Screen Contracts

For each screen:

### Screen: [name]

- Purpose:
- Layout:
- Primary action:
- Secondary actions:
- Empty/loading/error states:
- Validation states:
- Responsive behavior:
- Accessibility notes:

_(copy this block for each screen)_

## 9. Interaction / Motion

- Navigation transitions:
- Loading behavior:
- Hover/focus/pressed states:
- Toasts/alerts:
- Motion budget: none | subtle | expressive

## 10. Accessibility

- Keyboard path:
- Focus order:
- Color contrast:
- Labels and error messaging:
- Reduced motion:
- Screen reader expectations:

## 11. Implementation Tokens

- CSS variables / theme config:
- Component library setup:
- Files to create/change:
- Do-not-hardcode list:

---

## Reference Use Log

For each reference system consulted:

| Reference | Pattern Extracted | What Applies | What Is Omitted | Minimum Local Implementation |
|-----------|------------------|--------------|-----------------|------------------------------|
|           |                  |              |                 |                              |

**Rule**: A reference can justify a design decision, not a dependency. Adding a UI dependency requires independent justification (stdlib-first principle). Reference → extract pattern → adapt to current stack → implement minimally.
