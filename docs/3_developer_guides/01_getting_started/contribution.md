# Contribution Guidelines

Thank you for considering contributing to FoundryCord! We welcome contributions from the community to help make this project better. To ensure a smooth and effective collaboration process, please read and follow these guidelines.

## Getting Started

1.  **Ensure you have a working local setup.** Follow the [Getting Started: Local Development Setup](./setup.md) guide.
2.  **Familiarize yourself with the project:** Review the [Architecture Overview](../02_architecture/overview.md) and [Coding Conventions](./coding_conventions.md).
3.  **Find an issue to work on or propose a new feature:** Check the project\'s issue tracker on GitHub. If you plan to work on a new feature, it\'s a good idea to open an issue first to discuss it with the maintainers.

## Branching Strategy

We generally follow a Gitflow-like branching model, but simplified for this project:

*   **`main`:** This branch represents the most recent stable release. Direct commits to `main` are typically restricted.
*   **`develop`:** This is the primary development branch where all active work happens. Feature branches are merged into `develop`.
*   **Feature Branches (`feature/...`):** When you start working on a new feature, create a branch off `develop`:
    ```bash
    git checkout develop
    git pull origin develop
    git checkout -b feature/your-feature-name
    ```
*   **Bugfix Branches (`bugfix/...`):** For fixing bugs found in `develop` or a release:
    ```bash
    git checkout develop # or main if it's a hotfix for a release
    git pull origin develop # or main
    git checkout -b bugfix/issue-number-short-description
    ```
*   **Hotfix Branches (`hotfix/...`):** For critical bugs in a `main` release that need immediate attention. Branched from `main` and merged back into both `main` and `develop`.

## Making Changes

1.  **Code:** Write clean, maintainable code that adheres to our [Coding Conventions](./coding_conventions.md).
2.  **Tests:** Add or update tests for your changes. Refer to the [Testing Guidelines](./testing_guidelines.md).
3.  **Documentation:** Update any relevant documentation (user guides, developer guides, READMEs) to reflect your changes. New features should be documented.
4.  **Commits:** Write clear and concise commit messages. We encourage following a convention like [Conventional Commits](https://www.conventionalcommits.org/), but at a minimum, your commit messages should clearly describe the change.
    *   Example: `feat: Add user authentication via email and password`
    *   Example: `fix: Correct calculation error in dashboard widget`
    *   Example: `docs: Update setup guide with new migration step`

## Submitting Pull Requests (PRs)

Once your changes are ready and tested:

1.  **Push your branch** to your fork on GitHub:
    ```bash
    git push origin feature/your-feature-name
    ```
2.  **Open a Pull Request** against the `develop` branch of the main FoundryCord repository (unless it\'s a hotfix for `main`).
3.  **PR Description:**
    *   Provide a clear and descriptive title for your PR.
    *   In the description, summarize the changes you made.
    *   If your PR addresses an existing GitHub issue, link to it (e.g., "Closes #123" or "Fixes #456").
    *   Mention any specific areas you\'d like reviewers to focus on.
4.  **Draft PRs:** If your work is ongoing but you want early feedback, open a Draft Pull Request.

## Code Review Process

*   Maintainers or other contributors will review your PR.
*   Be prepared to discuss your changes and make adjustments based on feedback.
*   Once the PR is approved and passes any automated checks (CI), it will be merged.

## Code of Conduct

While a formal Code of Conduct is not yet established, we expect all contributors to interact respectfully and constructively. Harassment or discriminatory behavior will not be tolerated.

## Questions?

If you have questions about contributing, feel free to open an issue or discuss on the project\'s communication channels (if available). 