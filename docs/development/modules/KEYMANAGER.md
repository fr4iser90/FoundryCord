# Key Management

## Overview

The Homelab Discord Bot uses encryption for sensitive data with automatic key management.

## Automatic Key Management (Default)

By default, the system manages all keys automatically:

- Keys are automatically generated during first setup
- Keys are securely stored in the database 
- No need to manage or backup key files
- Support for key rotation
- Enables high-availability deployments

## For Developers: Manual Key Management 

For developers who need manual key management:

1. Open `app/bot/infrastructure/encryption/encryption_service.py`
2. Change `AUTO_KEY_MANAGEMENT = True` to `AUTO_KEY_MANAGEMENT = False`
3. Add the following environment variables to your `.env` file:
   ```
   AES_KEY=your_base64_encoded_aes_key
   ENCRYPTION_KEY=your_fernet_key
   JWT_SECRET_KEY=your_base64_encoded_jwt_key
   ```

### Key Generation for Developers

# ====================
# SECURITY CONFIGURATION
# ====================
# Note: Keys are automatically managed in the database.
# Developers: For manual key management, set AUTO_KEY_MANAGEMENT=false in encryption_service.py.
# AES_KEY=                # Encryption key for sensitive data
# ENCRYPTION_KEY=         # General purpose encryption key
# JWT_SECRET_KEY=         # JWT token signing key

Developers can generate secure keys using the following Python code:

```python
import os, base64
from cryptography.fernet import Fernet

# AES key
aes_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
print(f"AES_KEY={aes_key}")

# Fernet key
encryption_key = Fernet.generate_key().decode()
print(f"ENCRYPTION_KEY={encryption_key}")

# JWT key
jwt_key = base64.urlsafe_b64encode(os.urandom(24)).decode()
print(f"JWT_SECRET_KEY={jwt_key}")
```

## Related Security Documentation
- [Security Policy](./SECURITY_POLICY.md) - Overall security implementation
- [Security Role](../../ai/roles/core/BOT_CORE_SECURITY.md) - Security implementation responsibilities
- [Environment Variables](../reference/config/ENV_VARIABLES.md) - Security-related configuration

