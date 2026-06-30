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
