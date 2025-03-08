# app/bot/application/services/wireguard/__init__.py
from .wireguard_service import setup, WireguardService

__all__ = ["setup", "WireguardService"]