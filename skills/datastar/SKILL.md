---
name: datastar-conventions
description: >
  Always activate when using DataStar for SSE-driven UI. Contains correct
  attribute syntax, CDN URLs, SDK helpers, and common patterns. Prevents
  common integration mistakes like wrong attribute format or GET vs POST.
---

<!-- EDITORIAL GUIDELINES
- Be terse. Use tables and code examples over prose.
- Only include information that prevents common mistakes.
- WRONG/CORRECT pairs for pattern matching.
-->

## Non-Negotiable Rules

- **Read Official Docs:** Before designing or writing new Datastar integrations, read the official docs (https://data-star.dev) to ensure correct API usage.
- **Mandatory SDK Wrapper:** Never import the Datastar SDK (e.g. `github.com/starfederation/datastar-go/...`) directly into handler functions (such as in `cmd/`). Wrap the SDK in a thin local package (e.g. `pkg/sse/`) that exposes standard library patterns.

## Asset Loading

Two options for loading DataStar JS and OAT CSS:

### Option A: Embedded (Recommended for production)

Embed assets in the Go binary — no external dependencies, works in air-gapped environments:

```go
import "embed"

//go:embed assets/*
var Assets embed.FS

func AssetHandler() http.Handler {
    subFS, _ := fs.Sub(Assets, "assets")
    return http.StripPrefix("/static/", http.FileServer(http.FS(subFS)))
}

// In main.go
mux.Handle("GET /static/", ui.AssetHandler())
```

```html
<!-- HTML references local static files -->
<link rel="stylesheet" href="/static/oat.css">
<script type="module" src="/static/datastar.js"></script>
```

**Assets to embed:**
- `assets/datastar.js` — from SDK or CDN download
- `assets/oat.css` — OAT component styles
- `assets/oat.js` — OAT component logic (if needed)

### Option B: CDN (Development only)

Use CDN for quick prototyping — requires internet access:

```html
<!-- Check go.mod for SDK version, then use matching CDN -->
<script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@{VERSION}/bundles/datastar.js"></script>

<!-- Example for v1.0.0-RC.7 -->
<script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js"></script>
```

**When to use CDN:**
- Local development with internet
- Prototyping and demos
- Not for production or air-gapped servers

**When to use embedded:**
- Production deployments
- Air-gapped / highly secured servers
- Single binary requirement
- No external network access

## Attribute Syntax

DataStar v5+ uses **colon syntax** for attributes:

| Attribute | Syntax | Example |
|-----------|--------|---------|
| Signals | `data-signals` | `data-signals="{ count: 0 }"` |
| Text binding | `data-text` | `data-text="$count"` |
| Click handler | `data-on:click` | `data-on:click="@post('/api')"` |
| Submit handler | `data-on:submit` | `data-on:submit.prevent="@post('/api')"` |
| Key handler | `data-on:keydown.enter` | `data-on:keydown.enter="@post('/api')"` |

```html
<!-- WRONG -->
<div data-signals-count="0">
<button data-on-click="@get('/api')">

<!-- CORRECT -->
<div data-signals="{ count: 0 }">
<button data-on:click="@post('/api')">
```

## Signals Format

Signals are always JSON objects:

```html
<!-- WRONG — attribute syntax -->
<div data-signals-count="0">
<div data-signals-count="$initialValue">

<!-- CORRECT — JSON format -->
<div data-signals="{ count: 0 }">
<div data-signals="{ count: $initialValue, name: '' }">
```

## Actions (GET vs POST)

DataStar sends signals with **POST**, not GET:

```html
<!-- WRONG — GET doesn't send signals -->
<button data-on:click="@get('/increment')">

<!-- CORRECT — POST sends signals in request body -->
<button data-on:click="@post('/increment')">

<!-- GET is for actions that don't need signals -->
<button data-on:click="@get('/logout')">
```

## Go SDK Helpers

### Create SSE Writer

```go
import "github.com/starfederation/datastar-go/datastar"

// Create SSE writer from HTTP handler
sse := datastar.NewSSE(w, r)
```

### Read Signals from Client

```go
// Define signal structure
type MySignals struct {
    Count int    `json:"count"`
    Name  string `json:"name"`
}

// Read signals from request
var signals MySignals
if err := datastar.ReadSignals(r, &signals); err != nil {
    http.Error(w, err.Error(), http.StatusBadRequest)
    return
}
```

### Patch DOM Elements

```go
// Update HTML fragment (morphs existing DOM)
sse.PatchElements(`<div id="counter">Count: 42</div>`)
```

### Merge Signals to Client

```go
// Update client-side signal state
sse.MarshalAndPatchSignals(map[string]any{
    "count": signals.Count + 1,
})
```

### Complete Handler Example

```go
mux.HandleFunc("POST /increment", func(w http.ResponseWriter, r *http.Request) {
    // 1. Read signals from client
    var signals CounterSignals
    if err := datastar.ReadSignals(r, &signals); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    // 2. Process
    nextCount := signals.Count + 1

    // 3. Create SSE writer
    sse := datastar.NewSSE(w, r)

    // 4. Patch DOM if needed
    sse.PatchElements(`<span id="count">${nextCount}</span>`)

    // 5. Update client signals
    sse.MarshalAndPatchSignals(map[string]any{
        "count": nextCount,
    })
})
```

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| `data-signals-count="0"` | `data-signals="{ count: 0 }"` |
| `data-on-click="@get('/api')"` | `data-on:click="@post('/api')"` |
| `data-on-click="$$get('/api')"` | `data-on:click="@get('/api')"` (no $$) |
| `data-text="count"` | `data-text="$count"` (with $) |
| Manual SSE formatting | Use `datastar.NewSSE(w, r)` |
| `fmt.Fprintf(w, "data: ...")` | Use `sse.PatchElements()` or `sse.MarshalAndPatchSignals()` |

## SDK Wrapper Pattern (Option C)

Wrap the official SDK in thin packages that provide your own API surface:

```go
// pkg/sse/sse.go — Thin wrapper around datastar-go
package sse

import (
    "context"
    "net/http"
    "github.com/starfederation/datastar-go/datastar"
)

type SSEWriter struct {
    gen *datastar.ServerSentEventGenerator
}

func NewSSE(w http.ResponseWriter, r *http.Request) *SSEWriter {
    return &SSEWriter{gen: datastar.NewSSE(w, r)}
}

func (s *SSEWriter) PatchFragment(id, html string) error {
    return s.gen.PatchElements(html)
}

func (s *SSEWriter) MergeSignals(signals map[string]any) error {
    return s.gen.MarshalAndPatchSignals(signals)
}

func ReadSignals(r *http.Request, dest any) error {
    return datastar.ReadSignals(r, dest)
}
```

**Rule:** Wrapping the SDK is mandatory. The wrapper must align with standard library formats (e.g. `http.ResponseWriter` / `http.Handler` concepts) to decouple core app code from the external Datastar library API.


## References

- Official docs: https://data-star.dev
- Go SDK: https://github.com/starfederation/datastar-go
- Examples: https://data-star.dev/examples
- Reference: https://data-star.dev/reference
