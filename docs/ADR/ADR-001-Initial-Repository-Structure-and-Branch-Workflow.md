# ADR-001: Initial Repository Structure and Branch Workflow

* **Status:** Approved
* **Decider:** Radhika Patil (DevOps), approved by Tech Lead
* **Date:** 2026-07-26

## Context and Problem Statement

For SentinelX Trust AI to have clear collaboration across multiple developers (Rayri, Priya, Arjun) and maintain deployment readiness, we need a standardized repository structure and an agreed-upon branching strategy.

## Decision Drivers

- Need to isolate production releases from active integration and experimental feature development.
- Need to prevent accidental push of local environment configurations (`.env`) or runtimes (`.venv`).
- Need to establish clear rules for code review and merge criteria (PR verification).

## Considered Options

1. **GitHub Flow**: Feature branches merge directly to `main`.
2. **GitLab Flow**: Feature branches merge to `main`, which then goes to environment-specific branches.
3. **GitFlow (Modified)**: Separate `main` (production-ready) and `develop` (integration) branches with `feature/*`, `release/*`, and `hotfix/*` branches.

## Decision Outcome

**Option 3: Modified GitFlow** was selected as the standard git branching model.

### Branch Structure
- `main`: Clean, stable production releases. Direct commits are strictly forbidden.
- `develop`: Main integration branch where feature branches are merged.
- `feature/*`: Local developer branches for building features (e.g., `feature/scraper`, `feature/auth`).
- `release/*`: Prepared staging builds prior to production release.
- `hotfix/*`: Emergency patches pushed directly from and to `main`.

### Git Hygiene Rules
- Root level `.gitignore` created to prevent committing `.env`, `.venv`, and temporary scrapings.
- All code changes must go through Pull Requests targeting `develop`.
- Direct pushes to `main` and `develop` are protected.
