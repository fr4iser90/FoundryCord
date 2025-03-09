from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    discord_id = Column(String, unique=True)
    username = Column(String)
    role = Column(String)  # super_admin, admin, moderator, user, guest
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    token = Column(String) 
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Session(user_id='{self.user_id}', expires_at='{self.expires_at}')>"

class RateLimit(Base):
    __tablename__ = 'rate_limits'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    command_type = Column(String)
    attempt_count = Column(BigInteger, default=0)
    last_attempt = Column(DateTime)
    blocked_until = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<RateLimit(user_id='{self.user_id}', command_type='{self.command_type}')>"
