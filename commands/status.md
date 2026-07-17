---
name: harness-status
description: Display current project state

persona: Manager
subagent: false
reason: Read-only operation

gates:
  - check: .harness-eng/ exists
    on_fail: STOP, run /h:init

actions:
  - read: version.txt
  - read: .harness-eng/PHASES.md
  - read: .harness-eng/SLICE_LOG.md
  - scan: specs/active/*
  - scan: deferred.md in active features
  - read: .harness-eng/handover.yaml (if exists)
  - display_formatted_status_report: version, phases progress, active specs, deferred item counts, recent commits, handover view
  - render_json: output raw status JSON to stdout if --json is passed
  - render_html: write static HTML status to .harness-eng/status/index.html if --html is passed

must_do:
  - Show complete state snapshot
  - Include last 3 SLICE_LOG entries
  - Support JSON output via --json
  - Support self-contained static HTML output via --html
  - Render current handover.yaml state

must_not_do:
  - Modify anything
  - Run tests or a build
  - Make network calls
  - Start a server
  - Invoke LLM review
  - Open a subprocess that might download dependencies
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

