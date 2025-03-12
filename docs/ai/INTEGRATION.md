# AI Role Integration Guide

This document explains how different AI roles collaborate within the HomeLab Discord Bot project.

## Role Collaboration Matrix

| Role | Collaborates With | Primary Interactions |
|------|-------------------|---------------------|
| BOT_CORE_ARCHITECT | All roles | Design review, architecture guidance |
| BOT_CORE_DOMAIN | BOT_CORE_DATABASE, BOT_APP_* | Model design, business logic |
| BOT_INFRA_* | BOT_CORE_ARCHITECT, BOT_SYSTEM_* | Infrastructure planning |
| ... | ... | ... |

## Collaboration Workflows

### Feature Development Workflow
1. BOT_CORE_ARCHITECT - Determines architectural approach
2. BOT_CORE_DOMAIN - Designs domain models
3. BOT_APP_SERVICE - Implements application services
4. BOT_UI_* - Creates UI components
5. BOT_CORE_TEST - Verifies implementation

### System Enhancement Workflow
... 