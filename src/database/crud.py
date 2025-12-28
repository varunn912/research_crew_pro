from sqlalchemy.orm import Session
from .models import ResearchHistory, SessionLocal
from datetime import datetime
from typing import List, Optional

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_research_record(
    topic: str,
    language: str = 'en',
    status: str = 'pending'
) -> ResearchHistory:
    """Create a new research record."""
    db = SessionLocal()
    try:
        record = ResearchHistory(
            topic=topic,
            language=language,
            status=status,
            created_at=datetime.utcnow()
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    finally:
        db.close()

def update_research_status(
    record_id: int,
    status: str,
    report_path: Optional[str] = None,
    pdf_path: Optional[str] = None,
    google_docs_url: Optional[str] = None,
    notion_url: Optional[str] = None,
    audio_path: Optional[str] = None,
    duration_seconds: Optional[float] = None,
    summary: Optional[str] = None
) -> Optional[ResearchHistory]:
    """Update research record status and paths."""
    db = SessionLocal()
    try:
        record = db.query(ResearchHistory).filter(ResearchHistory.id == record_id).first()
        if record:
            record.status = status
            if report_path:
                record.report_path = report_path
            if pdf_path:
                record.pdf_path = pdf_path
            if google_docs_url:
                record.google_docs_url = google_docs_url
            if notion_url:
                record.notion_url = notion_url
            if audio_path:
                record.audio_path = audio_path
            if duration_seconds:
                record.duration_seconds = duration_seconds
            if summary:
                record.summary = summary
            if status == 'completed':
                record.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(record)
        return record
    finally:
        db.close()

def get_research_by_id(record_id: int) -> Optional[ResearchHistory]:
    """Get research record by ID."""
    db = SessionLocal()
    try:
        return db.query(ResearchHistory).filter(ResearchHistory.id == record_id).first()
    finally:
        db.close()

def get_all_research(limit: int = 100) -> List[ResearchHistory]:
    """Get all research records."""
    db = SessionLocal()
    try:
        return db.query(ResearchHistory).order_by(ResearchHistory.created_at.desc()).limit(limit).all()
    finally:
        db.close()

def get_research_by_topic(topic: str) -> List[ResearchHistory]:
    """Get research records by topic."""
    db = SessionLocal()
    try:
        return db.query(ResearchHistory).filter(
            ResearchHistory.topic.ilike(f"%{topic}%")
        ).order_by(ResearchHistory.created_at.desc()).all()
    finally:
        db.close()

def delete_research_record(record_id: int) -> bool:
    """Delete research record."""
    db = SessionLocal()
    try:
        record = db.query(ResearchHistory).filter(ResearchHistory.id == record_id).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False
    finally:
        db.close()