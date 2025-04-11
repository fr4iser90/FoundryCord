# app/shared/domain/repositories/audit/__init__.py
"""Audit repository interfaces"""
from .audit_log_repository import AuditLogRepository

__all__ = ['AuditLogRepository']