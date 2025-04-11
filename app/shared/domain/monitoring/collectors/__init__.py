"""Monitoring collector interfaces"""
from .system_collector import SystemCollectorInterface
from .service_collector import ServiceCollectorInterface

__all__ = ['SystemCollectorInterface', 'ServiceCollectorInterface'] 