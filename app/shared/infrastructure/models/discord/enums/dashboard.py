from enum import Enum

class DashboardType(Enum):
    """Types of dashboards"""
    SERVER = "server"
    PROJECT = "project"
    MONITORING = "monitoring"
    CUSTOM = "custom"

class ComponentType(Enum):
    """Types of dashboard components"""
    METRIC = "metric"
    CHART = "chart"
    TABLE = "table"
    LIST = "list"
    CUSTOM = "custom" 