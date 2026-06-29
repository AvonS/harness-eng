---
name: oat-css-conventions
description: >
  Always activate when writing HTML templates that use Oat UI. Contains
  verified class names, data attributes, CSS variables, and component
  patterns. Prevents hallucination of non-existent Oat features. All
  information verified against `oat.css` in the project — do NOT assume
  features exist without checking the source.
---

<!-- EDITORIAL GUIDELINES
- Be terse. Use tables and code examples over prose.
- Only include information verified from the project's oat.css source.
- WRONG/CORRECT pairs for pattern matching.
- Never assume classes exist — grep oat.css first.
- This is a GENERIC superset; project-specific paths go in each project.
-->

## Non-Negotiable Rules

- **Verify Before Assuming:** Every Oat class, data attribute, and CSS variable must be confirmed by reading the project's `oat.css` before use. Never assume features based on documentation summaries, naming conventions, or memory of other frameworks.
- **No Custom CSS Duplication:** Before writing a custom CSS rule, check if Oat provides it via a class, `data-*` attribute, or CSS variable. If Oat has it, use Oat.
- **Prefer customization via CSS variables over hardcoding** — if the project needs a different color, radius, or spacing, override the Oat CSS variable rather than writing custom CSS. This keeps everything under Oat's theming system.

## How to Verify Classes

```bash
# Find oat.css in the project — common paths:
find . -name "oat.css" -not -path "*/node_modules/*" 2>/dev/null

# Check if a class exists
grep "\.class-name" <path-to>/oat.css

# List all available classes
grep -oP '\.\w+(?=\s*\{)' <path-to>/oat.css | sort

# List all data attributes
grep -oP 'data-\w+' <path-to>/oat.css | sort -u

# List all CSS variables
grep -oP '--[\w-]+' <path-to>/oat.css | sort -u
```

## Verified Classes

Source: Project's `oat.css` (grep-confirmed)

### Layout
| Class | Purpose | Example |
|-------|---------|---------|
| `.container` | Max-width centered container | `<main class="container">` |
| `.row` | Flexbox row grid | `.row > .col-*` |
| `.col` | Flexible column | `.row > .col` |
| `.col-1` … `.col-12` | Fixed-width column (1–12) | `.row > .col-6` |
| `.col-end` | Push column to end | `.row > .col-end` |
| `.offset-1` … `.offset-6` | Column offset | `.row > .col-5.offset-2` |
| `.hstack` | Horizontal flex container | `.hstack.gap-2` |
| `.vstack` | Vertical flex container | `.vstack.items-center` |
| `.flex` | Display flex | `.flex` |
| `.flex-col` | Flex column direction | `.flex-col` |
| `.group` | Flex group | `.group` |
| `.items-center` | Align items center | `.hstack.items-center` |
| `.justify-center` | Justify content center | `.vstack.justify-center` |
| `.justify-between` | Justify content space-between | `.hstack.justify-between` |
| `.justify-end` | Justify content flex-end | `.hstack.justify-end` |
| `.w-100` | Width 100% | `.w-100` |
| `.w3` | Max-width 1280px | `.w3` |

### Spacing
> Oat only provides these specific spacing values — no `gap-3`, `mt-3`, etc.

| Class | Variable (approx) |
|-------|-------------------|
| `.gap-1` | `var(--space-1)` (~4px) |
| `.gap-2` | `var(--space-2)` (~8px) |
| `.gap-4` | `var(--space-4)` (~16px) |
| `.mt-2` | `var(--space-2)` (~8px) |
| `.mt-4` | `var(--space-4)` (~16px) |
| `.mt-6` | `var(--space-6)` (~24px) |
| `.mb-2` | `var(--space-2)` (~8px) |
| `.mb-4` | `var(--space-4)` (~16px) |
| `.mb-6` | `var(--space-6)` (~24px) |
| `.p-4` | `var(--space-4)` (~16px) |

### Components
| Class | Purpose | Attributes |
|-------|---------|------------|
| `.card` | Card container | — |
| `.badge` | Badge/pill | `data-variant="success\|secondary\|danger\|warning"` |
| `.button` / `.buttons` | Button group container | `role="group"` |
| `.outline` | Outline button variant | — |
| `.ghost` | Ghost button variant | — |
| `.large` | Large button/input | — |
| `.small` | Small button/input | — |
| `.table` | Table wrapper | — |
| `.toast` | Toast notification | `data-variant="success\|danger"` |
| `.toast-container` | Toast stack container | — |
| `.toast-title` | Toast title | — |
| `.toast-message` | Toast message | — |
| `.skeleton` | Skeleton loading placeholder | `[aria-busy=true]` |
| `.icon` | Icon container | — |
| `.line` | Horizontal rule / divider | — |
| `.box` | Box / panel | — |

### Animations
| Class | Effect |
|-------|--------|
| `.animate-pop-in` | Scale + fade in (for dialogs) |
| `.animate-slide-in` | Slide in from below |

### Typography
| Class | Purpose |
|-------|---------|
| `.text-light` | Muted secondary text |
| `.text-lighter` | Faint tertiary text |
| `.unstyled` | Remove default list/button styles |
| `.align-center` | Text-align center |
| `.align-left` | Text-align left |
| `.align-right` | Text-align right |

### States
| Class / Attr | Purpose |
|--------------|---------|
| `.error` | Form validation error (color + size) |
| `[aria-current]` | Active/highlighted → `background: var(--accent)` |
| `[aria-busy=true]` | Loading state (combine with `.skeleton`) |
| `[disabled]` | Disabled state (Oat styles natively) |

### Not Available (Common Hallucinations)
These do **NOT** exist in Oat. Do not assume:

- ❌ `.btn`, `.btn-primary` — use plain `<button>` or `.button` (group wrapper)
- ❌ `.danger` class — use `data-variant="danger"` or `var(--danger)` inline
- ❌ `.text-danger`, `.text-success`, `.text-primary` — no color utility classes exist
- ❌ `.text-center` — use `.align-center`
- ❌ `.hide-mobile`, `.show-desktop`, `.hide-tablet` — no responsive visibility classes
- ❌ `.gap-3`, `.mt-3`, `.mb-3` — only specific values (1, 2, 4, 6)
- ❌ `.col-offset-*` — use `.offset-*`

## Verified Data Attributes

| Attribute | Values | Purpose |
|-----------|--------|---------|
| `data-variant` | `secondary`, `success`, `danger`, `warning`, `error`, `avatar` | Component variant (badge, toast, alert, figure). No `primary` variant — default (no variant) is the primary style. |
| `data-sidebar` | (present) | Identifies sidebar element |
| `data-sidebar-layout` | (present) | Sidebar layout wrapper |
| `data-sidebar-open` | (present) | Toggle sidebar visibility |
| `data-tooltip` | string | Tooltip text on hover |
| `data-field` | (present) | Form field wrapper |
| `data-invalid` | (present) | Form field error state |
| `role` | `alert`, `group`, `tablist`, `tab`, `tabpanel` | ARIA roles |

## Verified CSS Variables

### Colors
| Variable | Purpose |
|----------|---------|
| `--primary` / `--primary-foreground` | Primary action color |
| `--secondary` / `--secondary-foreground` | Secondary element |
| `--danger` / `--danger-foreground` | Danger/error red |
| `--success` / `--success-foreground` | Success green |
| `--warning` / `--warning-foreground` | Warning amber |
| `--accent` / `--accent-foreground` | Highlight/accent |
| `--background` / `--foreground` | Page background / default text |
| `--card` / `--card-foreground` | Card background / text |
| `--muted` / `--muted-foreground` | Muted background / text |
| `--faint` / `--faint-foreground` | Faint background / text |
| `--border` | Default border color |
| `--input` | Input field background |
| `--ring` | Focus ring color |

### Typography
| Variable | Purpose |
|----------|---------|
| `--font-sans` | Sans-serif stack |
| `--font-mono` | Monospace stack |
| `--font-normal`, `--font-medium`, `--font-semibold`, `--font-bold` | Font weights |
| `--leading-normal` | Line height |

### Spacing
| Variable | Approx |
|----------|--------|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-7` | 28px |
| `--space-8` | 32px |
| `--space-9` | 36px |
| `--space-10` | 40px |

### Other
| Variable | Purpose |
|----------|---------|
| `--radius-full` | Full border-radius (circle/pill) |
| `--radius-large` | Large border-radius |
| `--shadow-medium` | Medium box-shadow |
| `--container-max` | Max container width |
| `--container-pad` | Container padding |
| `--grid-cols` | Grid column count |
| `--grid-gap` | Grid gap |
| `--z-modal` | Modal z-index |

## Dark Mode

Oat supports dark mode via `data-theme="dark"` on `<body>`:

```html
<body data-theme="dark">
```

Override dark-theme variables by scoping inside `[data-theme="dark"]`:

```css
[data-theme="dark"] {
  --background: rgb(9 9 11);
  --foreground: rgb(250 250 250);
  /* ... override any variable */
}
```

**WRONG:** `@media (prefers-color-scheme: dark) { ... }` — use Oat's `data-theme` attribute instead.

---

## Customizing Oat

> If the project needs behaviour or styling beyond what Oat provides, use Oat's customization paths rather than hardcoding custom CSS/JS. This keeps things under Oat's theming system and avoids maintenance burden.

### Theming via CSS Variable Overrides

All Oat colors, spacing, radii, and shadows are CSS variables. Override them in your project's CSS file loaded **after** Oat's CSS:

```css
/* In your project's CSS, after oat.css */
:root {
  --primary: #574747;
  --primary-foreground: #fafafa;
  --danger: #df514c;
  --radius-large: 12px;
}
```

See `--theme.css` in Oat's source for the full list of overridable variables.

### Selective Component Loading

Oat components can be loaded individually. The minimum required files are:

```
00-base.css
01-theme.css
base.js
→ your project-specific CSS here
→ individual component CSS/JS as needed
```

### Extensions (Third Party)

For features not in core Oat, use community extensions instead of writing custom code:

| Extension | Purpose | Size |
|-----------|---------|------|
| `oat-chips` | Chip/tag component with dismissible filters, colors, toggle selection | ~1KB |
| `oat-animate` | Declarative animation triggers (`ot-animate`): on-load, hover, in-view | ~1KB |
| `oat-table` | Semantic table enhancement: sort, filter, row selection | — |
| `oat-upload` | Dropzone, file previews, validation, removal, progress for `<input type="file">` | — |

Find extensions at https://oat.ink/extensions/ — open a PR to list your own.

---

## Migration Notes

When migrating from custom CSS to Oat:

| Remove (custom) | Replace with (Oat) |
|-----------------|-------------------|
| Custom button classes | `<button>` with optional `.outline` / `.ghost` / `data-variant` |
| `.badge-*` classes | `.badge` with `data-variant` |
| Custom alert boxes | `[role=alert]` with `data-variant` |
| `.scoreboard-container`, custom panels | `.card` wrapper |
| Custom table grids | `.vstack` + `.hstack` flexbox |
| `.active-turn`, `.selected-*` | `[aria-current="true"]` |
| Custom winner/status cells | `<mark>` (Oat styles it with warning tint) |
| `.btn.red`, `.text-danger` | `style="color: var(--danger)"` |
| Custom modals/dialogs | `<dialog class="animate-pop-in">` |
| Color utility classes | `data-variant` or inline `style="color: var(--primary)"` |

---

## Common Patterns

### Badge with Variant
```html
<span class="badge" data-variant="success">Active</span>
<span class="badge" data-variant="secondary">Idle</span>
<span class="badge" data-variant="danger">Error</span>
```

### Button Variants
```html
<button class="large">Primary Action</button>
<button class="outline">Secondary</button>
<button class="ghost small">Ghost</button>
<button data-variant="danger">Delete</button>
```
Note: Oat doesn't have `.btn` or `.btn-primary` — use plain `<button>` or `.button` (group wrapper).

### Card
```html
<div class="card">
    <h4>Title</h4>
    <p>Content</p>
</div>
```

### Alert
```html
<div role="alert" data-variant="success">
    <p>Operation completed successfully.</p>
</div>
```

### Dialog
```html
<dialog class="animate-pop-in" id="my-dialog">
    <header><h3>Title</h3></header>
    <form>
        <!-- body -->
        <footer>
            <button class="outline" formmethod="dialog">Cancel</button>
            <button type="submit">Confirm</button>
        </footer>
    </form>
</dialog>
```

### Toast
```html
<div class="toast" data-variant="success">
    <div class="toast-title">Notification</div>
    <div class="toast-message">Action completed.</div>
</div>
```

### Sidebar Layout
```html
<div data-sidebar-layout data-sidebar-open>
    <aside data-sidebar>
        <nav>
            <ul>
                <li><a href="#" aria-current="page">Active Section</a></li>
            </ul>
        </nav>
    </aside>
    <main>
        <!-- Content -->
    </main>
</div>
```

### Colored Text (No `.text-danger` exists)
Since Oat has no `.text-danger` utility class, use one of:

**Option A: Inline style** (no custom CSS needed)
```html
<span style="color: var(--danger); font-weight: 600;">Warning</span>
```

**Option B: 1-line custom CSS class** (if used frequently)
```css
.red-text { color: var(--danger); }
```

### Active State / Current Selection
Oat styles `[aria-current]` with `background: var(--accent)`.

```html
<tr aria-current="true">
    <td>Item 1</td>
</tr>
```

## References

| Resource | Link |
|----------|------|
| Oat CSS GitHub | https://github.com/knadh/oat |
| Oat documentation | https://oat.ink/ |
| Extensions | https://oat.ink/extensions/ |
| Customization guide | https://oat.ink/customizing/ |
| Data-Star (paired framework) | `skills/datastar/SKILL.md` |
