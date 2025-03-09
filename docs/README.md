# HomeLab Discord Bot Documentation

This directory contains comprehensive documentation for the HomeLab Discord Bot project, designed to help both human developers and AI assistants understand and contribute to the project effectively.

## Documentation Structure

### Core Documentation
- [**PROTOCOL.md**](core/PROTOCOL.md): Defines the development methodology and workflow
- [**ARCHITECTURE.md**](core/ARCHITECTURE.md): High-level architecture overview
- [**SECURITY_POLICY.md**](core/SECURITY_POLICY.md): Security practices and policies
- [**CONVENTIONS.md**](core/CONVENTIONS.md): Coding standards and conventions
- [**VARIABLES.md**](core/VARIABLES.md): Environment variables reference

### Implementation Guides
- **Patterns**:
  - [**DESIGN_PATTERN.md**](development/patterns/DESIGN_PATTERN.md): Architecture and design patterns
  - [**DASHBOARD_PATTERN.md**](development/patterns/DASHBOARD_PATTERN.md): Dashboard implementation patterns
  - [**SLASHCOMMAND_PATTERN.md**](development/patterns/SLASHCOMMAND_PATTERN.md): Slash command implementation
- **Development Roles**:
  - [**BOT_FRAMEWORK_DEVELOPER.md**](development/roles/BOT_FRAMEWORK_DEVELOPER.md): Core bot development
  - [**SECURITY_SPECIALIST.md**](development/roles/SECURITY_SPECIALIST.md): Security implementation
  - [**SYSTEM_MONITORING_DEVELOPER.py**](development/roles/SYSTEM_MONITORING_DEVELOPER.py): Monitoring features
  - [**SLASH_COMMAND_DEVELOPER.py**](development/roles/SLASH_COMMAND_DEVELOPER.py): Command implementation
  - [**UI_UX_DESIGNER.py**](development/roles/UI_UX_DESIGNER.py): Dashboard and UI development

### Project Planning
- [**ACTION_PLAN.md**](planning/ACTION_PLAN.md): Current tasks and priorities
- [**ROADMAP.md**](planning/ROADMAP.md): Long-term project roadmap
- [**MILESTONES.md**](planning/MILESTONES.md): Project milestones and progress

### Technical Reference
- [**SUBJECT_GUIDE.md**](reference/SUBJECT_GUIDE.md): System overview and concepts
- [**API_REFERENCE.md**](reference/API_REFERENCE.md): API documentation
- [**CONFIG_REFERENCE.md**](reference/CONFIG_REFERENCE.md): Configuration options
- [**ENV_VARIABLES.md**](reference/ENV_VARIABLES.md): Environment variables

### Templates
- **Code Templates**:
  - [**SERVICE_TEMPLATE.md**](templates/code/SERVICE_TEMPLATE.md): Template for new services
  - [**COMMAND_TEMPLATE.md**](templates/code/COMMAND_TEMPLATE.md): Template for new commands
- **Documentation Templates**:
  - [**MODULE_GUIDE_TEMPLATE.md**](templates/docs/MODULE_GUIDE_TEMPLATE.md): Template for module guides
  - [**FEATURE_REQUEST.md**](templates/docs/FEATURE_REQUEST.md): Template for feature requests
- **Role Templates**:
  - [**ROLE_DEFINITION.md**](development/template/ROLE_DEFINITION.md): Template for defining roles

## How to Use These Files with AI Assistants

### For Developers
1. **Always reference relevant documentation in your prompts**:
   ```
   @core/PROTOCOL.md @planning/ACTION_PLAN.md Please help me implement...
   ```

2. **Keep ACTION_PLAN.md updated** as tasks are completed to maintain an accurate project status.

3. **Add new guides** for complex topics using the templates provided.

### For AI Assistants
1. **Follow the core PROTOCOL.md** workflow for all development tasks.

2. **Verify understanding** against reference documentation before making changes.

3. **Consult ACTION_PLAN.md** to understand the current priorities and tasks.

## Documentation Maintenance
- All documentation should be kept up-to-date as the project evolves.
- Each file should include a "Last Updated" date in its header.
- Use internal linking to connect related documentation.