# app/shared/constants/user_constants.py
"""User role group constants"""
from app.shared.infrastructure.database.config.user_config import load_user_groups

# Load user groups at import time
USER_GROUPS = load_user_groups()
SUPER_ADMINS = USER_GROUPS['super_admins']
ADMINS = USER_GROUPS['admins']
MODERATORS = USER_GROUPS['moderators']
USERS = USER_GROUPS['users']
GUESTS = USER_GROUPS['guests']