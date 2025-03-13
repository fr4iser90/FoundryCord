from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.database import Base

class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    level = Column(String(10), index=True)
    logger_name = Column(String(100), index=True)
    message = Column(Text)
    module = Column(String(100), nullable=True)
    function = Column(String(100), nullable=True)
    line_num = Column(Integer, nullable=True)
    exception = Column(Text, nullable=True)
