# 9. Architectural Decision Records (ADRs)

This document logs significant architectural decisions made during the project's development.
Using ADRs helps understand the reasoning behind choices, especially when looking back or onboarding new team members.

## Format

Each ADR should follow a consistent format, for example (using Markdown Architectural Decision Records - MADR):

```markdown
# ADR-XXX: [Short Title of Decision]

*   **Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-YYY]
*   **Date:** [YYYY-MM-DD]
*   **Deciders:** [List of people involved in the decision]

## Context and Problem Statement

Describe the issue that needs to be addressed or the context driving the decision. What is the problem we are trying to solve?

## Decision Drivers

*   List the forces driving the decision (e.g., performance requirements, maintainability, team knowledge, specific feature needs, simplicity).

## Considered Options

*   [Option 1]
*   [Option 2]
*   [Option 3]
*   ...

Briefly describe each option considered.

## Decision Outcome

Chosen Option: "[Option X]", because [justification].

Explain why the chosen option was selected over the others. Detail the decision made.

### Positive Consequences

*   What benefits does this decision provide?

### Negative Consequences

*   What are the downsides, trade-offs, or risks associated with this decision?

## Links (Optional)

*   Link to related issues, discussions, documentation, etc.
```

---

## Log

*   [ADR-001: Initial Choice of FastAPI Framework](./adr/001-use-fastapi.md) (Example Link)
*   [ADR-002: Using Gridstack.js for Frontend Layout](./adr/002-use-gridstack.md) (Example Link)
*   *(Add links to new ADRs here as they are created. Store individual ADRs in `docs/architecture/adr/`)* 