# WireGuard Configuration Cogs

## Purpose
Manages Discord bot commands for WireGuard VPN configuration generation and distribution.

## Key Features
- `/get-user-config`: Generates personalized WireGuard client configurations
- `/get-user-qr`: Creates QR codes for mobile device setup
- Automated key rotation
- Configuration version tracking

## Main Components
- `get_user_config.py`: Core logic for config generation
- `get_user_qr.py`: QR code generation using segno library
- Rate-limited endpoints via rate_limit_middleware

## Dependencies
- Requires access to WireGuard server templates in /utils
- Integrates with auth_middleware for permission checks
