---
name: harness-design
description: Collaborator persona - design architecture and interfaces

persona: Collaborator
subagent: true

gates:
  - check: spec.md exists
    on_fail: STOP, run /h:define

preflight:
  - read_spec (requirements, stories)
  - read_constitution (conventions, rules)
  - read_review_pre_build (to act on gap list if returning from failure)

actions:
  - design_architecture (components, boundaries)
  - design_interfaces (APIs, contracts)
  - design_file_layout (where things go)
  - design_ui_brief_if_applicable (UX, components)
  - check_constitution_compliance
  - write_design (design.md with UI brief if applicable)
  - set_ref: PENDING
  - route: to /h:review-pre-build

outputs:
  - design.md with Ref: PENDING

must_do:
  - Follow constitution conventions
  - Design for testability
  - Include error handling
  - Stop and instruct user to run /h:review-pre-build

must_not_do:
  - Skip architecture
  - Present design directly to human for approval
---
