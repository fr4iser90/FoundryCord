from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    discord_id = Column(String, unique=True)
    username = Column(String)
    role = Column(String)  # super_admin, admin, moderator, user, guest
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    token = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class RateLimit(Base):
    __tablename__ = 'rate_limits'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    command_type = Column(String)
    attempt_count = Column(BigInteger, default=0)
    last_attempt = Column(DateTime)
    blocked_until = Column(DateTime, nullable=True)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    action = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)