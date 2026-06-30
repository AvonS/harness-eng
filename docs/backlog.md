# Harness-Eng Backlog

## Progressive Skills & Context Hub

*   **Progressive Skill Fetching (Init)**: At `/h:init` time, when the technology stack is derived and clear, dynamically fetch only the necessary skills from the `AvonS/harness-eng` repository rather than copying the entire `skills/` folder.
*   **On-Demand Skill Fetching (Build)**: During the `/h:build` phase, if the Jr Programmer detects a gap in knowledge or a missing convention, dynamically fetch the required skill from the upstream repository.
*   **Skill Issue Detection (Review)**: During `/h:review-pre-verify` (and `pre-build`), explicitly check if gaps or failures are due to a missing or outdated skill. If so, recommend fetching or updating the skill.
*   **Context-Hub Integration**: Point the agents to a centralized "Context-Hub" to fetch the absolute latest API documentation for popular frameworks and products, ensuring the harness stays up to date without manual skill updates.

## Archive Idea Backlog (Ponytail Filtered)

*These ideas were extracted from the PI extension archive and filtered through the Ponytail YAGNI principle to ensure they don't over-engineer the canonical file-based harness.*

*   **Read-Only Boundaries**: Instead of creating a complex new `SOUL.md` layer, strictly enforce read-only boundaries (e.g., for the `Sr Tech Lead`) directly in the existing `commands/` templates to prevent silent code rewrites.
*   **Git Hooks for Gate Enforcement**: Instead of relying purely on agent prompts for gates (which agents can ignore), enforce the state machine natively using Git pre-commit hooks (e.g., blocking commits if `design.md` lacks `Ref: APPROVED`).
*   **File-Based Asynchronous Escalation**: Instead of complex chat UI loops, if an agent fails 3 times, have it natively write a simple `BLOCKED.md` file and cleanly exit, allowing the human to review asynchronously.

*(Note: Ideas like SQLite state tracking and dynamic context templating engines were rejected from this backlog as they violate the Ponytail minimal-code philosophy).*

## Fowler Sensors & Context Engineering

*   **Computational Sensors**: Evolve the `harness-check.py` and `sanity-check.sh` tools into strict "Computational Sensors" (as per Martin Fowler). Integrate fast, deterministic tools like ESLint, dependency-cruiser, SAST, and Mutation Testing directly into the automated feedback loops to block the agent from proceeding until quality thresholds are met.
*   **Local CodeGraph (Zero-Bloat Context)**: Instead of relying on heavy, bloated MCP (Model Context Protocol) servers to understand large source repositories, implement a lightweight, local SQLite-based `.codegraph` index. This allows the harness agents to execute fast, deterministic SQL queries to map out the codebase architecture natively and securely.

## BDD Governance (Outer Loop)

*   **"BDD Outside, TDD Inside"**: TDD ensures the code is built right, but BDD ensures the *right code* is built. The harness must govern behavior using concrete examples.
*   **No New Personas**: BDD is a skill, not a persona. It should be taught to the existing agents (e.g., Gatekeeper) rather than creating a bloated "QA Agent".
*   **Silent Failure Recovery**: A failing BDD test shouldn't immediately alert the human. The agent should attempt to fix the implementation. It only escalates (via `BLOCKED.md`) if it breaches the retry limit.

## Web Design Pattern Registry

*A curated shortlist of reference URLs to be used by agents during the `ui-brief` and `design` phases to extract UX patterns without importing heavy framework dependencies.*

*   **[Obsidian](https://obsidian.md/)**: Pattern reference for "connected objects" and graph-like knowledge navigation rather than traditional cards.
*   **[Notion](https://www.notion.com/)**: Pattern reference for flexible "workspace" canvases, drag-and-drop block interactions, and command palettes.
*   **[Basecamp](https://basecamp.com/)**: Pattern reference for prioritizing "time, not just task flow", focusing on chronological activity feeds and calm UX.
*   **[Fizzy](https://www.fizzy.do/)**: Pattern reference for making a board feel "alive and current" through lightweight micro-interactions.
*   **[Dark Factory Architecture](https://www.infralovers.com/blog/2026-02-22-architektur-patterns-dark-factory/)**: Architectural pattern reference for autonomous systems.
*   **[Augmented Coding Patterns](https://lexler.github.io/augmented-coding-patterns/patterns/approved-scenarios/)**: Pattern reference for managing human-in-the-loop approved scenarios.
