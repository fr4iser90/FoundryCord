# app/shared/infrastructure/repositories/audit/__init__.py
"""Audit repository implementations"""
from .auditlog_repository_impl import AuditLogRepositoryImpl

__all__ = ['AuditLogRepositoryImpl']