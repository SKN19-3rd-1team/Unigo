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


class MajorCategory(Base):
    """
    전공 카테고리와 해당 카테고리에 속한 전공 목록을 저장합니다.
    Source: backend/data/major_categories.json
    """

    __tablename__ = "major_categories"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(255), unique=True, index=True, nullable=False)

    # JSON list of major names: ["Major A", "Major B", ...]
    major_names = Column(LONGTEXT, nullable=False)


class University(Base):
    """
    대학 기본 정보 (코드, URL)를 저장합니다.
    Source: backend/data/university_data_cleaned.json
    """

    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    code = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)
