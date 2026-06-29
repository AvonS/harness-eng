---
name: git-conventions
description: >
  Always activate for all git operations in this project — branching, committing,
  creating PRs. Enforces the harness-eng branching model and commit conventions.
  Use when creating branches, writing commit messages, or creating pull requests.
---

## Branch Model (enforced)

```
main                           ← protected, phase gates + hotfixes only
  └── phase/<phase-id>-<slug>  ← one per phase, forks from main
        ├── feature/<FID>-<slug>    ← Track 1: planned features
        ├── cr/<CRID>-<slug>        ← Track 2: change requests
        └── bugfix/<BID>-<slug>     ← Track 3: P1/P2 bugs

hotfix/<BID>-<slug>            ← P0 critical only, forks from main
```

## Branch Creation Rules

| Track | Base branch | Naming |
|-------|------------|--------|
| New phase | `main` | `phase/phase-N-<slug>` |
| Feature | current phase branch | `feature/F0NN-<slug>` |
| CR (minor) | current phase branch | `cr/CR-NNN-<slug>` |
| Bug P1/P2 | current phase branch | `bugfix/BUG-NNN-<slug>` |
| Bug P0 | `main` | `hotfix/BUG-NNN-<slug>` |

```bash
# Always pull before branching
git checkout <base>
git pull origin <base>
git checkout -b <new-branch>
git push -u origin <new-branch>
```

## Commit Message Convention

```
<type>(<id>): <description>

Types:
  feat     — feature implementation (task-level)
  test     — test code
  fix      — bug fix
  spec     — harness artefacts (proposal, design, tasks, acceptance)
  verify   — verification report
  cr       — change request implementation
  chore    — STATUS.md, branch cleanup, dependency bumps
  hotfix   — P0 critical fix
  docs     — documentation only

Examples:
  feat(F001): implement user authentication service - task 1.1
  test(F001): unit tests for user token validation - task 1.2
  fix(BUG-002): prevent connection pool deadlock under concurrent load
  spec(F002): proposal and design for notification engine
  verify(F001): all 4 acceptance criteria passing - ready for review
  chore: STATUS.md — F001 done, phase-1 at 3/5 features complete
  hotfix(BUG-001): correct boundary check in memory buffer allocator
```

## PR Rules

- **Feature → Phase**: title `feat(FXXX): <title> [VERIFIED]` · label `feature,verified`
- **Phase → Main**: title `Phase N: <name> [GATE APPROVED]` · label `phase-gate`
- **Hotfix → Main**: title `hotfix(BUG-NNN): <title> [P0]` · label `hotfix,p0`
- **Bugfix → Phase**: title `fix(BUG-NNN): <title> [VERIFIED]` · label `bugfix`

## Post-Merge Cleanup (always)

```bash
git checkout <base-branch>
git pull origin <base-branch>
git branch -d <merged-branch>
git push origin --delete <merged-branch>
```

## Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| Committing directly to `main` | Always PR |
| Committing directly to phase branch | Feature branch → PR |
| Forgetting to delete merged branches | Always delete after merge |
| `git commit -m "fix"` | Full commit message with type and ID |
| `git push --force` on shared branches | Never force push to phase/* or main |
| Merge commit messages | Use PR title — squash or rebase merge |

## .gitignore (required in every repo)

```gitignore
# Secrets — never commit
*.env
.env
.env.*
config.yaml
config.yml
*.key
*.pem
secrets/

# Build artifacts
bin/
dist/
coverage.out
*.test
*.prof

# OS
.DS_Store
Thumbs.db

# IDE
.idea/
.vscode/
*.swp
```

**Agent rule:** Before every commit, check `git diff --cached` for secrets, credentials, API keys, or config files. If found, abort the commit and warn the user.
