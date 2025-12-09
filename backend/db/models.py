from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from backend.db.connection import Base


class Major(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, index=True)
    major_id = Column(String(255), unique=True, index=True, nullable=False)
    major_name = Column(String(255), index=True, nullable=False)

    # Text fields
    cluster = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    interest = Column(Text, nullable=True)
    property = Column(Text, nullable=True)
    job = Column(Text, nullable=True)  # Comma separated or long text

    # JSON fields for complex structures (Stored as Text to avoid pymysql serialization issues)
    # Using LONGTEXT for large JSON data
    relate_subject = Column(LONGTEXT, nullable=True)
    enter_field = Column(LONGTEXT, nullable=True)
    department_aliases = Column(LONGTEXT, nullable=True)
    career_act = Column(LONGTEXT, nullable=True)
    qualifications = Column(LONGTEXT, nullable=True)
    main_subject = Column(LONGTEXT, nullable=True)
    university = Column(LONGTEXT, nullable=True)
    chart_data = Column(LONGTEXT, nullable=True)
    raw_data = Column(LONGTEXT, nullable=True)  # Store original raw json for backup

    # Statistics
    salary = Column(Float, nullable=True)
    employment = Column(Text, nullable=True)

    # Extracted stats from chart_data (optional, for easier querying)
    employment_rate = Column(Float, nullable=True)
    acceptance_rate = Column(Float, nullable=True)
