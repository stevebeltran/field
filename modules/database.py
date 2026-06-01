"""
Database module for Field Reports System
Handles MySQL connections and CRUD operations
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from urllib.parse import quote

load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# URL-encode password to handle special characters like @ and (
ENCODED_PASSWORD = quote(DB_PASSWORD, safe='')

# Connection string for MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FieldReport(Base):
    """Model for storing field reports"""
    __tablename__ = "field_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), index=True)
    report_type = Column(String(100))  # 'pdf_import' or 'new_report'
    created_date = Column(DateTime, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Store all field data as JSON for flexibility
    field_data = Column(JSON, nullable=False)

    # Metadata
    source_file = Column(String(500), nullable=True)  # Original PDF filename if imported
    created_by = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_report(report_name, report_type, field_data, source_file=None, created_by=None, notes=None):
    """Create a new field report"""
    db = SessionLocal()
    try:
        report = FieldReport(
            report_name=report_name,
            report_type=report_type,
            field_data=field_data,
            source_file=source_file,
            created_by=created_by,
            notes=notes
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_report(report_id):
    """Get a specific report by ID"""
    db = SessionLocal()
    try:
        return db.query(FieldReport).filter(FieldReport.id == report_id).first()
    finally:
        db.close()


def search_reports(search_term=None, report_type=None, limit=100):
    """Search reports by name or field data"""
    db = SessionLocal()
    try:
        query = db.query(FieldReport)

        if search_term:
            query = query.filter(
                (FieldReport.report_name.contains(search_term)) |
                (FieldReport.source_file.contains(search_term))
            )

        if report_type:
            query = query.filter(FieldReport.report_type == report_type)

        return query.order_by(FieldReport.created_date.desc()).limit(limit).all()
    finally:
        db.close()


def update_report(report_id, field_data=None, notes=None):
    """Update an existing report"""
    db = SessionLocal()
    try:
        report = db.query(FieldReport).filter(FieldReport.id == report_id).first()
        if report:
            if field_data is not None:
                report.field_data = field_data
            if notes is not None:
                report.notes = notes
            report.updated_date = datetime.utcnow()
            db.commit()
            db.refresh(report)
        return report
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def delete_report(report_id):
    """Delete a report"""
    db = SessionLocal()
    try:
        report = db.query(FieldReport).filter(FieldReport.id == report_id).first()
        if report:
            db.delete(report)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
