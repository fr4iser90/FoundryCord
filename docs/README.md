# HomeLab Discord Bot Documentation

This directory contains documentation for the HomeLab Discord Bot project, designed to help both human developers and AI assistants understand and contribute to the project effectively.

## Documentation Structure

- **PROTOCOL.md**: Defines the development methodology, workflow, and best practices for working on this project. This is the primary reference for how work should be approached.

- **ACTION_PLAN.md**: Contains the current tasks, their status, and implementation strategy. This is a living document that gets updated as work progresses.

- **SUBJECT_GUIDE.md**: Provides an overview of the system architecture, components, and key concepts. This helps new developers and AI assistants understand the project quickly.

- **SECURITY.md**: Details security measures, concerns, and recommendations for the project.

- **templates/**: Contains templates for various documentation needs:
  - **ROLE_DEFINITION.md**: Template for defining new roles in the project.

## How to Use These Files with AI Assistants

### For Developers

1. **Always reference these files in your prompts to AI assistants**:
   ```
   @PROTOCOL.md @ACTION_PLAN.md Please help me implement...
   ```

2. **Keep ACTION_PLAN.md updated** as tasks are completed to maintain an accurate project status.

3. **Add new subject guides** as needed for complex topics that require detailed explanation.

4. **Use the templates** when creating new documentation.

### For AI Assistants

1. **Follow the PROTOCOL.md** workflow for all development tasks.

2. **Verify your understanding** against SUBJECT_GUIDE.md before making changes.

3. **Consult ACTION_PLAN.md** to understand the current priorities and tasks.

4. **Apply security best practices** from SECURITY.md in all code changes.

5. **When uncertain, ask for clarification** rather than making assumptions.

## Documentation Maintenance

- All documentation should be kept up-to-date as the project evolves.
- Each file should include a "Last Updated" date at the top.
- Major changes to documentation should be noted in commit messages.
- Documentation should be reviewed periodically to ensure accuracy.

## Adding New Documentation

When adding new documentation:

1. Follow the established naming conventions
2. Add a reference to the new document in this README
3. Link to relevant existing documentation where appropriate
4. Include clear examples where possible

## Using Documentation in Development Workflow

1. **Start by reading** relevant documentation before beginning work
2. **Reference documentation** in pull requests to show compliance with standards
3. **Update documentation** as part of your changes when appropriate
4. **Create new documentation** for significant new features or components