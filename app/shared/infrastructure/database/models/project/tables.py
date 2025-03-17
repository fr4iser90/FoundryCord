"""
Association tables for project relations.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from ..base import Base

# Association table for many-to-many project members
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", String(20), primary_key=True),  # Discord user ID
) 