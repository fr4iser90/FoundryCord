from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# Association table for user-server many-to-many relationship
user_server = Table(
    'user_server', 
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('server_id', String, ForeignKey('servers.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)  # Discord User ID
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_login = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    servers = relationship('Server', secondary=user_server, back_populates='users')
    dashboards = relationship('Dashboard', back_populates='user')
    activities = relationship('UserActivity', back_populates='user')
    settings = relationship('UserSetting', back_populates='user', uselist=False)

class Server(Base):
    __tablename__ = 'servers'
    
    id = Column(String, primary_key=True)  # Discord Server ID
    name = Column(String(100), nullable=False)
    icon_url = Column(Text, nullable=True)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship('User', secondary=user_server, back_populates='servers')
    dashboards = relationship('Dashboard', back_populates='server')

class Dashboard(Base):
    __tablename__ = 'dashboards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    dashboard_type = Column(String(50), nullable=False)  # e.g., 'system', 'project', etc.
    layout = Column(Text, nullable=False)  # JSON storage of layout
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    server_id = Column(String, ForeignKey('servers.id'), nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='dashboards')
    server = relationship('Server', back_populates='dashboards')
    components = relationship('DashboardComponent', back_populates='dashboard')

class DashboardComponent(Base):
    __tablename__ = 'dashboard_components'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    component_type = Column(String(50), nullable=False)  # e.g., 'cpu_chart', 'memory_usage', etc.
    config = Column(Text, nullable=False)  # JSON storage of component configuration
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    # Foreign keys
    dashboard_id = Column(Integer, ForeignKey('dashboards.id'), nullable=False)
    
    # Relationships
    dashboard = relationship('Dashboard', back_populates='components')

class UserActivity(Base):
    __tablename__ = 'user_activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_type = Column(String(50), nullable=False)  # e.g., 'login', 'dashboard_create', etc.
    details = Column(Text, nullable=True)  # Additional details about the activity
    ip_address = Column(String(45), nullable=True)  # IPv6 can be up to 45 chars
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='activities')

class UserSetting(Base):
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    theme = Column(String(20), default='dark', nullable=False)
    refresh_rate = Column(Integer, default=60, nullable=False)  # in seconds
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    notify_system_alerts = Column(Boolean, default=True, nullable=False)
    notify_server_status = Column(Boolean, default=True, nullable=False)
    notify_updates = Column(Boolean, default=True, nullable=False)
    notification_method = Column(String(20), default='discord', nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='settings')

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(String(64), primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_valid = Column(Boolean, default=True, nullable=False) 