---
name: architecture-document
description: Big-picture template for the system architecture document.

gates:
  - check: BRD.md exists
    on_fail: STOP, Cannot design architecture without requirements

actions:
  - Fill system overview, layers, data flow, deployment, and technology sections

outputs:
  - .harness-eng/ARCHITECTURE.md

must_do:
  - Align architecture layers with BRD requirements

must_not_do:
  - Leave system boundary undefined
---

# Architecture Document
# Project: <project-name>
# Date: <YYYY-MM-DD>
# Status: Draft | Approved

---

## System Overview
<1-2 sentences: what the system does and how it's structured>

---

## Component Map

```
<visual representation of components and their relationships>
```

| Component | Responsibility | Depends On |
|-----------|---------------|------------|
| <component> | <what it does> | <what it needs> |

---

## Layer Model

| Layer | Purpose | Contains |
|-------|---------|----------|
| <layer> | <purpose> | <what lives here> |

---

## Data Flow

<How data moves through the system>
<API boundaries, message queues, databases>

---

## External Dependencies

| Service | Purpose | Fallback |
|---------|---------|----------|
| <service> | <what it provides> | <what happens if it fails> |

---

## Deployment

- Platform: <Linux / Docker / K8s / Serverless>
- Build: <command from technology.yaml>
- Binary: <output path>

---

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Performance | <latency, throughput targets> |
| Scalability | <concurrent users, data volume> |
| Availability | <uptime target> |

---

## Rejected Approaches

> *Alternative designs considered and why they were rejected.*

- **<approach>**: rejected because <reason>
- **<approach>**: rejected because <reason>

---

## References

| Document | What it provides |
|----------|-----------------|
| `CONSTITUTION.md` | Principles and rules |
| `BRD.md` | Business requirements |
| `domain-ctx.txt` | Domain vocabulary |
| `technology.yaml` | Toolchain and build config |
