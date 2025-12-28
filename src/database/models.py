from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create database directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Database setup
DATABASE_URL = "sqlite:///data/research_history.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ResearchHistory(Base):
    """Model for storing research history."""
    __tablename__ = "research_history"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(500), nullable=False, index=True)
    language = Column(String(10), default='en')
    status = Column(String(50), default='completed')  # pending, completed, failed
    report_path = Column(String(500))
    pdf_path = Column(String(500))
    google_docs_url = Column(String(500))
    notion_url = Column(String(500))
    audio_path = Column(String(500))
    duration_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    summary = Column(Text)
    
    def __repr__(self):
        return f"<ResearchHistory(id={self.id}, topic='{self.topic}', status='{self.status}')>"

# Create tables
Base.metadata.create_all(bind=engine)