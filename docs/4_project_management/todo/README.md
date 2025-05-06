# Project TODO Lists

## Purpose

This directory (`docs/4_project_management/todo/`) and its subdirectories house all ongoing and archived TODO lists for the [FoundryCord](docs/1_introduction/glossary.md#foundrycord) project. These lists are crucial for tracking development tasks, bug fixes, feature implementations, and other project-related work items.

Maintaining clear and actionable TODO lists helps the team stay organized, prioritize work, and understand the current state of development for different components and initiatives.

## Organization

TODO lists are generally organized by the primary application component they relate to:

*   **`bot/`**: Contains TODO lists specifically for the Discord Bot (`app/bot/`).
*   **`web/`**: Contains TODO lists specifically for the Web Application (`app/web/`).
*   **`shared/`**: Contains TODO lists for the Shared Core Library (`app/shared/`) or for tasks that are cross-cutting and significantly impact multiple components (like large-scale refactoring or documentation updates such as `documentation-update-06-05.md`).

Each of these directories may also contain an `archive/` subdirectory:

*   **`archive/`**: Used to store TODO lists for completed milestones, old initiatives, or tasks that are no longer relevant. This keeps the main component directories focused on active work.

Project-wide or very high-level TODOs that don\'t fit neatly into `bot/`, `web/`, or `shared/` might occasionally be placed directly in the root `todo/` directory, but this should be rare.

## TODO List Format

All TODO lists should be written in Markdown (`.md`).

*   **Filename:** Choose a clear and descriptive filename that indicates the scope or timeframe of the TODO list (e.g., `feature-guild-designer-phase1.md`, `bugfix-user-auth-issues.md`, `refactor-database-layer-Q3.md`). Including a date (e.g., `YYYY-MM-DD` or `MM-YY`) can be helpful for time-bound initiatives.
*   **Task Format:** Use standard Markdown task list syntax:
    *   `* [ ] Uncompleted task description.`
    *   `* [x] Completed task description.`
*   **Task Granularity:** Break down large, complex tasks into smaller, actionable sub-tasks. This makes them easier to manage, assign, and track progress on.
*   **Task Details:** For clarity, especially on larger initiatives, consider adding details to each task or group of tasks, such as:
    *   **Focus:** A brief explanation of the main goal or area of concern for the task.
    *   **Affected Files/Modules:** List the primary files or modules expected to be impacted by the task. This helps in understanding scope and potential conflicts.
    *   **Priority (Optional):** (e.g., High, Medium, Low) or (P1, P2, P3).
    *   **Assignee (Optional):** Who is responsible for the task.
    *   **Notes/Context:** Any additional relevant information or links.

(Refer to `docs/4_project_management/todo/shared/documentation-update-06-05.md` for a good example of a structured TODO list for a specific initiative.)

## Task Lifecycle

1.  **Creation:** New tasks or TODO lists are created as needed when new features are planned, bugs are identified, or refactoring efforts are decided upon.
2.  **Prioritization & Assignment (If applicable):** Tasks are prioritized, and assignees might be identified.
3.  **Execution:** Developers work on tasks, marking them as complete `[x]` as they are finished and committed.
4.  **Review (If applicable):** Completed tasks might be reviewed as part of a Pull Request or other quality assurance process.
5.  **Archival:** Once all tasks in a specific TODO list are completed, or if an initiative is finished or becomes obsolete, the entire `.md` file should be moved to the appropriate `archive/` subdirectory (e.g., from `bot/some-feature.md` to `bot/archive/some-feature.md`).

## Finding Current Tasks

To find current, active tasks:

*   Navigate to the relevant subdirectory (`bot/`, `web/`, `shared/`).
*   Look for `.md` files that are **not** in an `archive/` folder.
*   Open the file and review the uncompleted tasks `[ ]`.

Regularly reviewing and updating these TODO lists is a collective responsibility to ensure the project stays on track. 